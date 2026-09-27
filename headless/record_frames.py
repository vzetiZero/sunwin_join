# -*- coding: utf-8 -*-
"""
record_frames.py - Ghi lai TOAN BO khung WebSocket cua game (giai ma msgpack)
de tim phuong thuc JOIN BAN NGAY (quick play) cho bat ky sanh nao (TLMN / Sam Loc).

CAN: pip install websocket-client msgpack

Cach dung:
  # 1) Mo Chrome moi (tu dang nhap trong cua so Chrome vua hien)
  python record_frames.py

  # 2) Dung lai profile da luu trong pair_tool/_profiles (tu dang nhap acc)
  python record_frames.py --profile acc1

  # 3) Gan vao Chrome dang mo san remote-debugging
  python record_frames.py --port 9222

  # 4) Phan tich lai file da ghi (khong can mo Chrome)
  python record_frames.py --analyze frames_20260927_101500.jsonl

Quy trinh tim 'join ngay' (quick play):
  1. Dang nhap, vao SANH cua game (vd Sam Loc).
  2. Bam ENTER (danh dau "TRUOC KHI join").
  3. Bam nut CHƠI NHANH / VÀO BÀN trong game.
  4. Bam ENTER (danh dau "SAU KHI join"), roi go 'q' + Enter de dung.
  -> Khung nam GIUA 2 dau MARK la goi join can tim.
"""
import os, sys, json, time, base64, socket, subprocess, tempfile, shutil
import threading, urllib.request

try:
    import websocket, msgpack
except Exception:
    print("!! Thieu thu vien. Chay: pip install websocket-client msgpack")
    raise

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAME = "https://web.sunwin.villas/?affId=Sunwin"
PROFILES = os.path.join(ROOT, "pair_tool", "_profiles")


def log(*a):
    print(*a)
    try:
        sys.stdout.flush()
    except Exception:
        pass


# ----------------------------- Chrome helpers -----------------------------
def find_chrome():
    cands = [
        os.path.join(os.environ.get("PROGRAMFILES", ""), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
        r"E:\Tools\Google Chrome\App\Chrome-bin\chrome.exe",
    ]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return shutil.which("chrome") or shutil.which("chrome.exe")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def launch_chrome(profile=None, incognito=False):
    """profile: thu muc user-data-dir (de tu dang nhap lai). Tra ve (proc, port, tmpdir)."""
    chrome = find_chrome()
    if not chrome:
        return None, None, None
    port = free_port()
    tmp = None
    if profile:
        ud = profile
        os.makedirs(ud, exist_ok=True)
    else:
        ud = tempfile.mkdtemp(prefix="sunwin_rec_")
        tmp = ud
    args = [chrome, "--remote-debugging-port=%d" % port, "--user-data-dir=" + ud,
            "--no-first-run", "--no-default-browser-check", "--disable-features=Translate"]
    if incognito:
        args.append("--incognito")
    args.append(GAME)
    try:
        proc = subprocess.Popen(args)
    except Exception as e:
        log("!! Khong mo duoc Chrome: %s" % e)
        return None, None, tmp
    return proc, port, tmp


def http_json(port, path):
    with urllib.request.urlopen("http://127.0.0.1:%s%s" % (port, path), timeout=5) as r:
        return json.load(r)


def wait_target(port, timeout=30, want="sunwin"):
    """Cho Chrome san sang va tra ve tab game (page co webSocketDebuggerUrl)."""
    end = time.time() + timeout
    fallback = None
    while time.time() < end:
        try:
            for t in http_json(port, "/json"):
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                    if fallback is None:
                        fallback = t
                    if (want is None) or (want in (t.get("url") or "").lower()):
                        return t
        except Exception:
            pass
        time.sleep(0.6)
    return fallback


# ----------------------------- decode -----------------------------
def decode_frame(opcode, payload_b64):
    try:
        raw = base64.b64decode(payload_b64 or "")
    except Exception:
        raw = b""
    obj = None
    if opcode == 2:
        try:
            obj = msgpack.unpackb(raw, raw=False, strict_map_key=False)
        except Exception:
            obj = "<bin %d bytes>" % len(raw)
    else:
        try:
            obj = raw.decode("utf-8", "replace")
        except Exception:
            obj = ""
    return raw, obj


def short(obj, n=320):
    try:
        if isinstance(obj, bytes):
            s = obj.decode("utf-8", "replace")
        elif isinstance(obj, str):
            s = obj
        else:
            s = json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        s = str(obj)
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + "..."


def now_str():
    return time.strftime("%H:%M:%S") + (".%03d" % (int(time.time() * 1000) % 1000))


def sock_name(url):
    u = url or ""
    if "ws-lby" in u:
        return "lobby"
    if "ws-card" in u:
        return "card"
    base = u.split("?")[0].rstrip("/")
    return base.split("/")[-1][:16] or "?"


# ----------------------------- recorder -----------------------------
class Recorder(object):
    def __init__(self, ws, outpath):
        self.ws = ws
        self.outpath = outpath
        self.f = open(outpath, "w", encoding="utf-8")
        self.mid = 0
        self.seq = 0
        self.stop = threading.Event()
        self.urls = {}

    def cmd(self, method, params=None):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params or {}}))
        return self.mid

    def write(self, rec):
        self.seq += 1
        rec["seq"] = self.seq
        try:
            self.f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            self.f.flush()
        except Exception:
            pass

    def marker(self, text):
        self.write({"t": now_str(), "dir": "mark", "text": text})
        log("========== MARK: %s ==========" % text)

    def sname(self, url):
        return sock_name(url)

    def pump(self):
        self.ws.settimeout(1.0)
        while not self.stop.is_set():
            try:
                raw = self.ws.recv()
            except Exception:
                continue
            if not raw:
                continue
            try:
                m = json.loads(raw)
            except Exception:
                continue
            meth = m.get("method")
            p = m.get("params") or {}
            if meth == "Network.webSocketCreated":
                self.urls[p.get("requestId")] = p.get("url")
                self.write({"t": now_str(), "dir": "open", "url": p.get("url")})
                log("[OPEN ] %s" % p.get("url"))
            elif meth == "Network.webSocketClosed":
                url = self.urls.get(p.get("requestId"))
                self.write({"t": now_str(), "dir": "close", "url": url})
                log("[CLOSE] %s" % url)
            elif meth == "Network.webSocketFrameError":
                self.write({"t": now_str(), "dir": "err",
                            "url": self.urls.get(p.get("requestId")),
                            "msg": p.get("errorMessage")})
                log("[ERROR] %s" % p.get("errorMessage"))
            elif meth in ("Network.webSocketFrameSent", "Network.webSocketFrameReceived"):
                resp = p.get("response") or {}
                op = resp.get("opcode", 0)
                b64 = resp.get("payloadData", "")
                raw, obj = decode_frame(op, b64)
                is_out = meth.endswith("Sent")
                url = self.urls.get(p.get("requestId"))
                self.write({"t": now_str(), "dir": "out" if is_out else "in", "op": op,
                            "url": url, "len": len(raw), "b64": b64, "obj": obj})
                tag = "OUT" if is_out else "IN "
                log("%s [%s] %s" % (tag, self.sname(url), short(obj)))


# ----------------------------- analyze -----------------------------
def find_keys(obj, keys, acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                acc.append(v)
            find_keys(v, keys, acc)
    elif isinstance(obj, list):
        for v in obj:
            find_keys(v, keys, acc)
    return acc


def analyze(path):
    frames = []
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                frames.append(json.loads(line))
            except Exception:
                pass
    except Exception as e:
        log("!! Khong doc duoc %s: %s" % (path, e))
        return

    log("\n================ PHAN TICH %s ================" % os.path.basename(path))
    marks = [f for f in frames if f.get("dir") == "mark"]
    outs = [f for f in frames if f.get("dir") == "out"]
    ins = [f for f in frames if f.get("dir") == "in"]
    log("Dau moc: %d | Gui ra: %d | Nhan vao: %d | Tong: %d" % (len(marks), len(outs), len(ins), len(frames)))

    cmds = {}
    gids = set()
    for f in frames:
        obj = f.get("obj")
        if f.get("dir") == "out" and isinstance(obj, list) and obj and isinstance(obj[0], int):
            cmds.setdefault(obj[0], []).append(f)
        for g in find_keys(obj, ("gid", "gameID", "gameId", "tableGameID", "game_id")):
            if isinstance(g, (int, str)) and str(g) != "":
                gids.add(str(g))

    log("\n-- LENH GUI RA (theo ma lenh dau tien) --")
    for k in sorted(cmds.keys()):
        arr = cmds[k]
        log("  cmd[%s] x %d   vi du: %s" % (k, len(arr), short(arr[0].get("obj"), 220)))

    if gids:
        log("\n-- UNG VIEN gameID/gid trong cac goi: %s" % ", ".join(sorted(gids)))

    if marks:
        log("\n-- CAC GOI GUI RA GIUA CAC DAU MOC (ung vien JOIN NGAY) --")
        for i, mk in enumerate(marks):
            start = mk.get("seq", 0)
            end = marks[i + 1].get("seq", 10 ** 9) if i + 1 < len(marks) else 10 ** 9
            for f in outs:
                if start < f.get("seq", 0) < end:
                    log("   [%s] %s" % (f.get("t"), short(f.get("obj"), 260)))

    log("\nGoi y: join ngay thuong co dang [3,\"Simms\",...] hoac [6,...,{cmd:...}] nam giua 2 MARK.")
    log("Gui ket qua (hoac file .jsonl + anh console probe_quickjoin.js) de minh hoa giai ma tiep.\n")


# ----------------------------- main -----------------------------
def run_record(args):
    proc = port = tmp = None
    if args.port:
        port = int(args.port)
    else:
        prof = None
        if args.profile:
            prof = args.profile
            if not os.path.isabs(prof):
                prof = os.path.join(PROFILES, prof)
        log("Dang mo Chrome...")
        proc, port, tmp = launch_chrome(profile=prof)
        if not port:
            log("!! Khong tim thay Chrome (chrome.exe).")
            return
        log("Chrome da mo (debug port %d). Neu chua dang nhap, hay dang nhap vao game." % port)

    t = wait_target(port, 30)
    if not t:
        log("!! Khong tim thay tab game tren port %d." % port)
        return
    log("Gan vao tab: %s" % t.get("url"))

    ws = websocket.create_connection(t["webSocketDebuggerUrl"], max_size=None, suppress_origin=True)
    outpath = args.out or os.path.join(HERE, "frames_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    rec = Recorder(ws, outpath)
    rec.cmd("Network.enable")
    threading.Thread(target=rec.pump, daemon=True).start()

    log("BAT DAU GHI -> %s" % outpath)
    log("Thao tac: vao SANH game -> Enter (mark TRUOC) -> bam CHƠI NHANH / VÀO BÀN -> Enter (mark SAU) -> go 'q' + Enter de dung.")
    log("(Enter trong = danh dau; 'q' = dung)")

    if args.seconds and args.seconds > 0:
        try:
            time.sleep(args.seconds)
        except KeyboardInterrupt:
            pass
    else:
        try:
            while not rec.stop.is_set():
                line = input("> ")
                if line.strip().lower() in ("q", "quit", "exit"):
                    break
                rec.marker(line.strip() or "MARK")
        except EOFError:
            log("(Khong co ban phim tuong tac - chay toi khi Ctrl+C)")
            try:
                while not rec.stop.is_set():
                    time.sleep(0.5)
            except KeyboardInterrupt:
                pass
        except KeyboardInterrupt:
            pass

    rec.stop.set()
    time.sleep(0.3)
    try:
        ws.close()
    except Exception:
        pass
    if proc:
        try:
            proc.terminate()
        except Exception:
            pass
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    log("DA DUNG. File: %s" % outpath)
    analyze(outpath)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Ghi khung WebSocket game de tim phuong thuc join ngay.")
    ap.add_argument("--profile", help="ten profile trong pair_tool/_profiles (tu dang nhap)")
    ap.add_argument("--port", help="gan vao Chrome dang mo san remote-debugging port")
    ap.add_argument("--out", help="file dau ra .jsonl")
    ap.add_argument("--seconds", type=int, default=0, help="tu dung sau N giay (0 = cho Enter/q)")
    ap.add_argument("--analyze", help="phan tich lai file .jsonl da ghi roi thoat")
    args = ap.parse_args()
    if args.analyze:
        analyze(args.analyze)
        return
    run_record(args)


if __name__ == "__main__":
    main()
