# -*- coding: utf-8 -*-
"""
sunwin_headless.py - 2 tài khoản gặp nhau KHÔNG cần trình duyệt (có log rõ ràng).

Chạy:
  python sunwin_headless.py auth_acc1.json auth_acc2.json [bet] [gid] [soNguoi]
    bet   : mức cược (mặc định 100)
    gid   : 1 = TLMN (mặc định)
    soNguoi: 2 (mặc định)

Log ghi ra màn hình + file pair_log.txt (cùng thư mục).
"""
import json, os, sys, time, threading
import websocket, msgpack

HERE = os.path.dirname(os.path.abspath(__file__))
LOGF = open(os.path.join(HERE, "pair_log.txt"), "a", encoding="utf-8")

def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line)
    LOGF.write(line + "\n"); LOGF.flush()

LOBBY = "wss://ws-lby.azhkthg1.net/wsbinary"
CARD = "wss://ws-card04.azhkthg1.net/wsbinary%s"
ORIGIN = "https://web.sunwin.villas"
STOP = {"v": False}

def load(path):
    a = json.load(open(path, encoding="utf-8"))
    info = a["info"]; sig = a["signature"]
    tok = json.loads(info)["wsToken"]
    return info, sig, tok, a.get("username", "?")

class C:
    def __init__(self, tag, url):
        self.tag = tag
        self.ws = websocket.create_connection(url, max_size=None, origin=ORIGIN)
        self.dn = None; self.uid = None; self.players = []; self.joined = False; self.auth_ok = False
    def auth(self, info, sig):
        self.ws.send_binary(msgpack.packb([1, "Simms", "", "", {"info": info, "signature": sig}], use_bin_type=True))
    def send(self, obj):
        self.ws.send_binary(msgpack.packb(obj, use_bin_type=True))
    def reader(self):
        while not STOP["v"]:
            try:
                self.ws.settimeout(2); d = self.ws.recv()
            except Exception:
                continue
            if not isinstance(d, bytes):
                continue
            try:
                m = msgpack.unpackb(d, raw=False, strict_map_key=False)
            except Exception:
                continue
            if isinstance(m, list) and len(m) >= 4 and m[1] is True and m[0] == 1 and not self.auth_ok:
                self.auth_ok = True
                log("%s AUTH OK (user=%s)" % (self.tag, m[3]))
            if isinstance(m, list) and len(m) >= 4 and m[0] == 3 and isinstance(m[1], bool):
                self.joined = bool(m[1])
                log("%s VAO BAN %s -> ack=%s" % (self.tag, m[3], m[1]))
            if isinstance(m, list) and len(m) >= 2 and isinstance(m[1], dict):
                d2 = m[1]
                if "dn" in d2 and "uid" in d2 and self.dn is None:
                    self.dn = d2.get("dn"); self.uid = d2.get("uid")
                    log("%s user: %s (%s)" % (self.tag, self.dn, self.uid))
                if "ps" in d2:
                    self.players = [(p.get("dn"), p.get("pid")) for p in d2["ps"]]

def main():
    a1 = sys.argv[1] if len(sys.argv) > 1 else "auth_acc1.json"
    a2 = sys.argv[2] if len(sys.argv) > 2 else "auth_acc2.json"
    bet = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    gid = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    mu = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    if not os.path.isabs(a1): a1 = os.path.join(HERE, a1)
    if not os.path.isabs(a2): a2 = os.path.join(HERE, a2)

    info1, sig1, tok1, u1 = load(a1)
    info2, sig2, tok2, u2 = load(a2)
    log("=== BAT DAU GHEP BAN  gid=%s bet=%s soNguoi=%s ===" % (gid, bet, mu))
    log("ACC1 = %s   |   ACC2 = %s" % (u1, u2))

    # ---------- ACC1: lobby -> TAO BAN ----------
    log("ACC1 ket noi lobby ws-lby...")
    l1 = C("ACC1-lobby", LOBBY + "?token=" + tok1)
    l1.auth(info1, sig1)
    time.sleep(1.0)
    l1.send([6, "Simms", "channelPlugin", {"cmd": 308, "gid": gid, "aid": 1, "b": bet, "Mu": mu, "pwd": "", "iJ": False}])
    log("ACC1 GUI TAO BAN: [6,'Simms','channelPlugin',{cmd:308,gid:%s,b:%s,Mu:%s,pwd:''}]" % (gid, bet, mu))
    rid = sid = None
    end = time.time() + 10
    while time.time() < end and rid is None:
        try:
            l1.ws.settimeout(2); d = l1.ws.recv()
        except Exception:
            continue
        if not isinstance(d, bytes):
            continue
        try:
            m = msgpack.unpackb(d, raw=False, strict_map_key=False)
        except Exception:
            continue
        if isinstance(m, list) and len(m) >= 2 and isinstance(m[1], dict) and m[1].get("cmd") == 308 and m[1].get("ri"):
            ri = m[1]["ri"]; rid = ri.get("rid"); sid = ri.get("sid")
    if not rid:
        log("!! ACC1 tao ban THAT BAI"); return
    soban = "%s%s" % (sid, rid)
    log("ACC1 TAO BAN THANH CONG -> soBan=%s (rid=%s, sid=%s)" % (soban, rid, sid))

    # ---------- ACC2: card socket -> VAO BAN ngay ----------
    card = (CARD % sid) + "?token="
    log("ACC1 ket noi card socket (ws-card04...wsbinary%s)..." % sid)
    c1 = C("ACC1-card", card + tok1); c1.auth(info1, sig1)
    threading.Thread(target=c1.reader, daemon=True).start()
    time.sleep(0.4)
    log("ACC1 VAO BAN (chu phong): [3,'Simms',%s,'']" % rid)
    c1.send([3, "Simms", rid, ""])
    time.sleep(0.3)
    log("ACC2 ket noi card socket (ws-card04...wsbinary%s)..." % sid)
    c2 = C("ACC2", card + tok2); c2.auth(info2, sig2)
    threading.Thread(target=c2.reader, daemon=True).start()
    time.sleep(0.6)
    log("ACC2 GUI VAO BAN: [3,'Simms',%s,'']" % rid)
    c2.send([3, "Simms", rid, ""])

    # ---------- Theo doi 25s ----------
    log("--- Theo doi ban %s (25s) ---" % soban)
    got = False
    end = time.time() + 25
    while time.time() < end:
        pl = c2.players or c1.players
        if pl:
            log("Trong ban %s hien co: %s" % (soban, ", ".join("%s(pid%s)" % (dn, pid) for dn, pid in pl)))
            if len(pl) >= 2 and not got:
                got = True
                log(">>> ✅✅ 2 TAI KHOAN DA GAP NHAU trong ban %s <<<" % soban)
        for w in (c1, c2):
            try:
                w.send([7, "Simms", 3, 0])
            except Exception:
                pass
        time.sleep(3)
    STOP["v"] = True
    log("=== KET THUC (ban %s) ===" % soban)

if __name__ == "__main__":
    main()
