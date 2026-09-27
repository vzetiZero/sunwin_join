# -*- coding: utf-8 -*-
"""
capture_auth.py - Lấy 'auth' (info + signature + token) của 1 tài khoản đang đăng nhập.
Mở 1 TAB MỚI vào game (app tự đăng nhập lại) rồi bắt gói auth.

  python capture_auth.py <PORT_remote_debug> auth_<ten>.json
Lấy PORT: http://127.0.0.1:19995/api/v3/profiles  (trường remote_debugging_address)
"""
import json, sys, time, urllib.request, base64
import websocket, msgpack

GAME = "https://web.sunwin.villas/?affId=Sunwin"

def open_new(port):
    for method in ("PUT", "GET"):
        try:
            req = urllib.request.Request("http://127.0.0.1:%s/json/new?%s" % (port, GAME), method=method)
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.load(r)
        except Exception:
            time.sleep(1)
    return None

def main():
    port = sys.argv[1]; out = sys.argv[2]
    t = open_new(port)
    if not t or not t.get("webSocketDebuggerUrl"):
        print("Khong mo duoc tab game"); return
    print("TARGET:", t.get("url"))
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], max_size=None, suppress_origin=True)
    mid = 0
    def cmd(m, params=None):
        nonlocal mid
        mid += 1
        ws.send(json.dumps({"id": mid, "method": m, "params": params or {}}))
        return mid
    cmd("Network.enable")
    got = None
    deadline = time.time() + 45
    ws.settimeout(1.0)
    while time.time() < deadline and got is None:
        try:
            raw = ws.recv()
        except Exception:
            continue
        try:
            msg = json.loads(raw)
        except Exception:
            continue
        if msg.get("method") == "Network.webSocketFrameSent":
            resp = msg["params"].get("response") or {}
            if resp.get("opcode") != 2:
                continue
            try:
                obj = msgpack.unpackb(base64.b64decode(resp.get("payloadData", "")), raw=False, strict_map_key=False)
            except Exception:
                continue
            if isinstance(obj, list) and len(obj) >= 5 and obj[1] == "Simms" and isinstance(obj[4], dict) and "signature" in obj[4]:
                got = obj[4]
    if not got:
        print("KHONG bat duoc auth."); return
    info = got.get("info")
    try:
        username = json.loads(info).get("username")
    except Exception:
        username = "?"
    open(out, "w", encoding="utf-8").write(json.dumps({"info": info, "signature": got.get("signature"), "username": username}, ensure_ascii=False))
    print("SAVED", out, "| username:", username)

if __name__ == "__main__":
    main()
