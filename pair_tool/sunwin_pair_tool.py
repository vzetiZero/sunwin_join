# -*- coding: utf-8 -*-
"""
Sunwin Pair Tool  -  Ghép 2 tài khoản vào cùng 1 bàn, KHÔNG cần extension, KHÔNG pass.
- acc1 tạo bàn MỞ (Mu=2 hoặc 4) -> acc2 vào NGAY -> gặp nhau.
- Bàn 4 người -> nhiều ghế nên acc2 luôn vào được, khách cũng vào được (không cần pass).
- Tự thử lại nếu bị chiếm ghế. Có log rõ ràng.
Cần: pip install websocket-client msgpack
"""
import json, os, sys, time, threading, base64, queue, urllib.request
import tkinter as tk
from tkinter import ttk, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
ACC_FILE = os.path.join(HERE, "accounts.json")
LOG_FILE = os.path.join(HERE, "pair_tool.log")
GPM_API = "http://127.0.0.1:19995"
GAME = "https://web.sunwin.villas/?affId=Sunwin"
LOBBY = "wss://ws-lby.azhkthg1.net/wsbinary"
CARD = "wss://ws-card04.azhkthg1.net/wsbinary%s"
ORIGIN = "https://web.sunwin.villas"

BET_LABELS = ['100','500','1K','2K','5K','10K','20K','50K','100K','200K','500K','1M']
BET_MAP = {'100':100,'500':500,'1K':1000,'2K':2000,'5K':5000,'10K':10000,'20K':20000,
           '50K':50000,'100K':100000,'200K':200000,'500K':500000,'1M':1000000}
BG='#070b14'; CARD_BG='#0f172a'; MUTED='#64748b'; LINE='#1e293b'; GOLD='#f0c040'
VERBOSE = False  # bat True de xem chi tiet frame (debug)

def load_accounts():
    if os.path.exists(ACC_FILE):
        try: return json.load(open(ACC_FILE, encoding='utf-8'))
        except Exception: pass
    return [
        {"name": "acc1", "profile_id": "6fee69df-7149-4492-9bb7-dd6d0d1bf897", "auth": "auth_acc1.json"},
        {"name": "acc2", "profile_id": "c21a0e18-9c9b-4902-8c5f-bc16fedc9fdc", "auth": "auth_acc2.json"},
    ]
def auth_path(a):
    p = a.get('auth') or ('auth_%s.json' % a.get('name', 'acc'))
    return p if os.path.isabs(p) else os.path.join(HERE, p)
def load_auth(a):
    p = auth_path(a)
    if not os.path.exists(p): return None
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return None
def auth_ok(auth):
    if not auth: return False
    try:
        ts = json.loads(auth['info']).get('timestamp', 0)
        return (time.time()*1000 - ts) < 3*3600*1000
    except Exception: return False
def gpm_start(pid):
    for act in ('close/%s' % pid, 'stop/%s' % pid):
        try: urllib.request.urlopen("%s/api/v3/profiles/%s" % (GPM_API, act), timeout=6).read()
        except Exception: pass
    time.sleep(1.5)
    try:
        r = urllib.request.urlopen("%s/api/v3/profiles/start/%s" % (GPM_API, pid), timeout=30)
        j = json.loads(r.read().decode('utf-8'))
        addr = (j.get('data') or {}).get('remote_debugging_address') or ''
        return addr.split(':')[-1] if ':' in addr else None
    except Exception: return None
def open_new_tab(port):
    for method in ('PUT', 'GET'):
        try:
            req = urllib.request.Request("http://127.0.0.1:%s/json/new?%s" % (port, GAME), method=method)
            with urllib.request.urlopen(req, timeout=8) as r: return json.load(r)
        except Exception: time.sleep(0.5)
    return None
def capture_auth(port, seconds=90, log=print):
    import websocket, msgpack
    t = open_new_tab(port)
    if not t or not t.get('webSocketDebuggerUrl'):
        log("!! Không mở được tab game."); return None
    log("Đã mở tab game. Hãy đăng nhập nếu được yêu cầu...")
    ws = websocket.create_connection(t['webSocketDebuggerUrl'], max_size=None, suppress_origin=True)
    mid = 0
    def cmd(m, p=None):
        nonlocal mid; mid += 1
        ws.send(json.dumps({'id': mid, 'method': m, 'params': p or {}})); return mid
    cmd('Network.enable')
    AUTO = ("(function(){try{var cc=window.cc;if(!cc)return 'no-cc';var s=cc.director.getScene();"
            "function cn(c){try{return cc.js.getClassName(c);}catch(e){return '';}}"
            "var lob=null,seen=new Set();(function w(n,d){if(!n||d>30||seen.has(n)||lob)return;seen.add(n);"
            "var cs=[];try{cs=n.getComponents?n.getComponents(cc.Component):(n.components||[]);}catch(e){}"
            "cs.forEach(function(c){if(cn(c)==='LobbyViewController')lob=c;});"
            "(n.children||[]).forEach(function(k){w(k,d+1);});})(s,0);if(!lob)return 'no-lobby';var d=[];"
            "['autoLoginAcc','processLoginAcc','loginFromLPCompleted','reloginCompleted'].forEach(function(m){"
            "try{if(typeof lob[m]==='function'){lob[m]();d.push(m);}}catch(e){}});"
            "return 'login:'+d.join(',');})()")
    end = time.time() + seconds
    start = time.time()
    auto = 0
    ws.settimeout(1.0)
    while time.time() < end:
        try: raw = ws.recv()
        except Exception: raw = None
        if auto < 3 and (time.time() - start) > (12 + auto * 12):
            auto += 1
            try:
                cmd('Runtime.evaluate', {'expression': AUTO, 'returnByValue': True})
                log("Chưa thấy auth — tự bấm đăng nhập (#%d)..." % auto)
            except Exception:
                pass
            ws.settimeout(1.0)
        if raw is None: continue
        try: msg = json.loads(raw)
        except Exception: continue
        if msg.get('method') == 'Network.webSocketFrameSent':
            resp = msg['params'].get('response') or {}
            if resp.get('opcode') != 2: continue
            try: obj = msgpack.unpackb(base64.b64decode(resp.get('payloadData','')), raw=False, strict_map_key=False)
            except Exception: continue
            if isinstance(obj, list) and len(obj) >= 5 and obj[1] == 'Simms' and isinstance(obj[4], dict) and 'signature' in obj[4]:
                info = obj[4].get('info')
                try: username = json.loads(info).get('username')
                except Exception: username = '?'
                # dong tab game de nha phien (khong giu phong) cho headless
                try:
                    urllib.request.urlopen("http://127.0.0.1:%s/json/close/%s" % (port, t.get('id')), timeout=5).read()
                    log("Đã đóng tab game (nhả phiên cho headless).")
                except Exception:
                    pass
                return {'info': info, 'signature': obj[4].get('signature'), 'username': username}
    return None

def verify_auth(auth, log=print, tag='acc'):
    """Ket noi lobby + auth de kiem tra token con hop le khong. Tra ve username neu OK."""
    import websocket, msgpack
    name = tag
    try:
        u = json.loads(auth['info']).get('username', '')
    except Exception:
        u = ''
    try:
        ws = websocket.create_connection(LOBBY + '?token=' + json.loads(auth['info'])['wsToken'],
                                         max_size=None, origin=ORIGIN)
    except Exception as e:
        log("%s: kết nối lobby LỖI (%s)" % (name, e)); return None
    ws.send_binary(msgpack.packb([1, 'Simms', '', '', {'info': auth['info'], 'signature': auth['signature']}], use_bin_type=True))
    end = time.time() + 7
    while time.time() < end:
        try:
            ws.settimeout(1.5); d = ws.recv()
        except Exception:
            continue
        if not isinstance(d, bytes):
            continue
        try:
            m = msgpack.unpackb(d, raw=False, strict_map_key=False)
        except Exception:
            continue
        if isinstance(m, list) and len(m) >= 4 and m[0] == 1 and m[1] is True:
            return m[3] or u
    return None

# ----------------------------- pair -----------------------------
LASTF = os.path.join(HERE, "last_room.json")
def _load_last():
    try: return json.load(open(LASTF, encoding='utf-8'))
    except Exception: return {}
def _save_last(d):
    try: open(LASTF, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False))
    except Exception: pass
def _uname(auth):
    try: return json.loads(auth['info']).get('username')
    except Exception: return None

def leave_room(auth, rid, log=print, tag='acc'):
    """Gui goi LeaveRoom [4,'Simms',rid] de thoat phong cu."""
    import websocket, msgpack
    tok = json.loads(auth['info'])['wsToken']
    try:
        ws = websocket.create_connection(LOBBY + '?token=' + tok, max_size=None, origin=ORIGIN)
    except Exception as e:
        log("%s: LEAVE lỗi kết nối (%s)" % (tag, e)); return False
    try:
        ws.send_binary(msgpack.packb([1, 'Simms', '', '', {'info': auth['info'], 'signature': auth['signature']}], use_bin_type=True))
        time.sleep(0.6)
        ws.send_binary(msgpack.packb([4, 'Simms', rid], use_bin_type=True))
        time.sleep(0.6)
    except Exception:
        pass
    try: ws.close()
    except Exception: pass
    log("%s: đã gửi LEAVE phòng %s (giải phóng khỏi phòng cũ)" % (tag, rid))
    return True

def _conn(url):
    import websocket
    return websocket.create_connection(url, max_size=None, origin=ORIGIN)

class Acc(object):
    def __init__(self, tag, url):
        self.tag = tag; self.ws = _conn(url)
        self.dn = None; self.players = []; self.joined = False; self.auth_ok = False; self.rid = None
    def auth(self, auth):
        import msgpack
        self.ws.send_binary(msgpack.packb([1, 'Simms', '', '', {'info': auth['info'], 'signature': auth['signature']}], use_bin_type=True))
    def send(self, o):
        import msgpack
        self.ws.send_binary(msgpack.packb(o, use_bin_type=True))
    def reader(self, log, stop):
        import msgpack
        _log = log if VERBOSE else (lambda *a: None)
        while not stop[0]:
            try:
                self.ws.settimeout(2); d = self.ws.recv()
            except Exception:
                continue
            if not isinstance(d, bytes): continue
            try: m = msgpack.unpackb(d, raw=False, strict_map_key=False)
            except Exception: continue
            if isinstance(m, list) and len(m) >= 4 and m[0] == 1 and m[1] is True and not self.auth_ok:
                self.auth_ok = True; _log("%s auth OK (user=%s)" % (self.tag, m[3]))
            if isinstance(m, list) and len(m) >= 4 and m[0] == 3 and isinstance(m[1], bool):
                if self.rid is None or m[3] == self.rid:
                    self.joined = bool(m[1]); _log("%s vào bàn %s -> ack=%s" % (self.tag, m[3], m[1]))
            if isinstance(m, list) and len(m) >= 2 and isinstance(m[1], dict):
                d2 = m[1]
                if 'dn' in d2 and 'uid' in d2 and self.dn is None:
                    self.dn = d2.get('dn'); _log("%s user: %s" % (self.tag, self.dn))
                if 'ps' in d2:
                    self.players = [(p.get('dn'), p.get('pid')) for p in d2['ps']]
                    _log("%s thấy trong bàn: %s" % (self.tag, ", ".join("%s(pid%s)" % (a, b) for a, b in self.players)))

def _create_room(auth1, gid, bet, mu, pwd, log):
    import msgpack
    tok1 = json.loads(auth1['info'])['wsToken']
    l1 = Acc('acc1-lobby', LOBBY + '?token=' + tok1); l1.auth(auth1)
    time.sleep(1.0)
    l1.send([6, 'Simms', 'channelPlugin', {'cmd': 308, 'gid': gid, 'aid': 1, 'b': bet, 'Mu': mu, 'pwd': pwd, 'iJ': False}])
    end = time.time() + 10
    while time.time() < end:
        try:
            l1.ws.settimeout(2); d = l1.ws.recv()
        except Exception:
            continue
        if not isinstance(d, bytes): continue
        try: m = msgpack.unpackb(d, raw=False, strict_map_key=False)
        except Exception: continue
        if isinstance(m, list) and len(m) >= 2 and isinstance(m[1], dict) and m[1].get('cmd') == 308 and m[1].get('ri'):
            ri = m[1]['ri']; return ri.get('rid'), ri.get('sid')
    return None, None

def do_pair(auth1, auth2, bet, gid, mu, log, stop, pwd=''):
    log("[Tìm bàn] Bắt đầu ghép 2 acc — bàn SOLO (%s người), cược %s, không pass" % (mu, bet))
    tok1 = json.loads(auth1['info'])['wsToken']; tok2 = json.loads(auth2['info'])['wsToken']
    u1 = _uname(auth1); u2 = _uname(auth2)
    last = _load_last()
    for tag, a, u in (('acc1', auth1, u1), ('acc2', auth2, u2)):
        rid0 = last.get(u)
        if rid0:
            try: leave_room(a, rid0, log, tag)
            except Exception: pass
    for attempt in range(1, 9):
        if stop[0]: break
        rid, sid = _create_room(auth1, gid, bet, mu, pwd, log)
        if not rid:
            log("[Tìm bàn] Server chưa cho tạo bàn — đang thử lại..."); time.sleep(2); continue
        soban = "%s%s" % (sid, rid)
        log("[Tìm bàn] Đã tạo bàn solo %s. Đang chờ 2 acc vào..." % soban)
        try:
            last = _load_last(); last[u1] = rid; last[u2] = rid; _save_last(last)
        except Exception:
            pass
        try:
            c1 = Acc('acc1', (CARD % sid) + '?token=' + tok1); c1.auth(auth1)
            threading.Thread(target=c1.reader, args=(log, stop), daemon=True).start()
            c2 = Acc('acc2', (CARD % sid) + '?token=' + tok2); c2.auth(auth2)
            threading.Thread(target=c2.reader, args=(log, stop), daemon=True).start()
        except Exception:
            log("[Tìm bàn] Card socket lỗi — thử lại..."); time.sleep(2); continue
        time.sleep(0.6)
        c1.rid = rid; c2.rid = rid
        c1.send([3, 'Simms', rid, pwd])
        c2.send([3, 'Simms', rid, pwd])

        done = False; guest = False; end = time.time() + 18
        while time.time() < end and not stop[0]:
            for w in (c1, c2):
                try: w.send([7, 'Simms', 3, 0])
                except Exception: pass
            dn1 = c1.dn; dn2 = c2.dn
            for a in (c1, c2):
                names_a = set(dn for dn, pid in (a.players or []) if dn)
                if dn1 and dn2 and dn1 in names_a and dn2 in names_a:
                    done = True
                if (names_a - {dn1, dn2}):
                    guest = True
            if done: break
            time.sleep(1.5)
        if done:
            log("✅ ĐÃ GHÉP 2 ACC VÀO BÀN SOLO %s  (%s + %s)" % (soban, dn1, dn2))
            log("[Tìm bàn] Đang giữ kết nối... (bấm Dừng để ngắt)")
            while not stop[0]:
                for w in (c1, c2):
                    try: w.send([7, 'Simms', 3, 0])
                    except Exception: pass
                time.sleep(4)
            log("=== ĐÃ DỪNG ===")
            return
        if guest:
            log("[Tìm bàn] Có người khác vào bàn — server đang tìm bàn khác...")
        else:
            log("[Tìm bàn] Chưa gặp nhau — server đang tìm...")
        try: c1.ws.close(); c2.ws.close()
        except Exception: pass
    log("[Tìm bàn] Chưa ghép được — bấm GHÉP BÀN lại.")


# ----------------------------- GUI -----------------------------
class App(object):
    def __init__(self, root):
        self.root = root; self.accounts = load_accounts(); self.stop = [False]; self.q = queue.Queue()
        root.title('Sunwin Pair Tool — ghép bàn headless (không extension, không pass)')
        root.geometry('920x580'); root.configure(bg=BG); root.minsize(840, 500)
        head = tk.Frame(root, bg=BG); head.pack(fill='x', padx=14, pady=(12, 6))
        tk.Label(head, text='TLDT Sunwin — Ghép bàn Headless', fg=GOLD, bg=BG, font=('Segoe UI', 15, 'bold')).pack(side='left')
        self.rows = tk.Frame(root, bg=CARD_BG, highlightthickness=1, highlightbackground=LINE)
        self.rows.pack(fill='x', padx=14, pady=(4, 8)); self.row_w = {}
        for a in self.accounts: self._row(a)
        bar = tk.Frame(root, bg=BG); bar.pack(fill='x', padx=14, pady=(0, 6))
        tk.Label(bar, text='Cược:', fg=MUTED, bg=BG, font=('Segoe UI', 9)).pack(side='left')
        self.betvar = tk.StringVar(value='100')
        ttk.Combobox(bar, textvariable=self.betvar, values=BET_LABELS, state='readonly', width=6).pack(side='left', padx=(4, 14))
        tk.Label(bar, text='Game (gid):', fg=MUTED, bg=BG, font=('Segoe UI', 9)).pack(side='left')
        self.gidvar = tk.StringVar(value='1')
        tk.Entry(bar, textvariable=self.gidvar, width=4, bg='#111827', fg='#e2e8f0', relief='flat').pack(side='left', padx=(4, 14))
        tk.Button(bar, text='Kiểm tra auth', command=self.check_auth, bg='#0ea5e9', fg='#fff',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2', padx=12, pady=3).pack(side='left', padx=(0, 10))
        tk.Button(bar, text='⚡ GHÉP BÀN SOLO', command=self.run, bg=GOLD, fg='#111827',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2', padx=12, pady=3).pack(side='left', padx=(0, 10))
        tk.Button(bar, text='Dừng', command=self.stop_run, bg='#ef4444', fg='#fff',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2', padx=12, pady=3).pack(side='left')
        self.logtxt = tk.Text(root, bg='#0b1220', fg='#e2e8f0', insertbackground='#e2e8f0', font=('Consolas', 9), relief='flat', wrap='word')
        self.logtxt.pack(fill='both', expand=True, padx=14, pady=(0, 12))
        self.log('Sẵn sàng. Hết hạn thì bấm "Lấy auth". Chọn 2 acc rồi bấm "⚡ GHÉP BÀN SOLO" (bàn 2 người, không pass).')
        self.root.after(200, self._drain)

    def _row(self, a):
        f = tk.Frame(self.rows, bg=CARD_BG); f.pack(fill='x', padx=8, pady=5)
        var = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text='Chọn', variable=var, bg=CARD_BG, fg='#e2e8f0', selectcolor=GOLD,
                       activebackground=CARD_BG, activeforeground='#fff', font=('Segoe UI', 9, 'bold')).pack(side='left')
        tk.Label(f, text=a.get('name', '?'), fg='#fff', bg=CARD_BG, width=8, anchor='w', font=('Segoe UI', 10, 'bold')).pack(side='left')
        st = self.status_text(a)
        lbl = tk.Label(f, text=st[0], fg=st[1], bg=CARD_BG, font=('Segoe UI', 9, 'bold'), anchor='w'); lbl.pack(side='left', padx=(0, 10))
        tk.Button(f, text='Lấy auth', command=lambda a=a: self.get_auth(a), bg='#3b82f6', fg='#fff',
                  font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2', padx=10).pack(side='right')
        self.row_w[a.get('name')] = {'status': lbl, 'acc': a, 'var': var}

    def selected_accounts(self):
        return [w['acc'] for w in self.row_w.values() if w['var'].get()]

    def status_text(self, a):
        au = load_auth(a)
        if not au:
            return ('— chưa có auth — bấm "Lấy auth"', '#94a3b8')
        try:
            info = json.loads(au['info']); u = info.get('username', ''); ts = info.get('timestamp', 0)
        except Exception:
            u = ''; ts = 0
        age_h = (time.time()*1000 - ts) / 3600000.0
        if age_h < 3:
            return ('✔ còn hạn (~%.1fh) · %s' % (3 - age_h, u), '#4ade80')
        return ('✖ HẾT HẠN · %s — bấm "Lấy auth"' % u, '#f87171')

    def refresh(self):
        for name, w in self.row_w.items():
            t, c = self.status_text(w['acc']); w['status'].configure(text=t, fg=c)

    def log(self, m):
        line = '[%s] %s\n' % (time.strftime('%H:%M:%S'), m)
        self.logtxt.insert('end', line); self.logtxt.see('end')
        try: open(LOG_FILE, 'a', encoding='utf-8').write(line)
        except Exception: pass

    def get_auth(self, a):
        pid = a.get('profile_id')
        if not pid:
            messagebox.showwarning('Lấy auth', 'Tài khoản chưa cấu hình profile_id (GPM).'); return
        self.log('Đang mở profile GPM: %s ...' % a.get('name'))
        def work():
            port = gpm_start(pid)
            if not port: self.q.put('!! Không mở được profile GPM (kiểm tra GPM đang chạy).'); return
            self.q.put('Profile đã mở (debug %s). Chờ đăng nhập + bắt auth...' % port)
            au = capture_auth(port, 90, log=lambda m: self.q.put(m))
            if not au: self.q.put('!! Chưa bắt được auth. Đăng nhập lại rồi bấm "Lấy auth".'); return
            open(auth_path(a), 'w', encoding='utf-8').write(json.dumps(au, ensure_ascii=False))
            self.q.put('✔ Đã lưu auth cho %s (user=%s)' % (a.get('name'), au.get('username')))
        threading.Thread(target=work, daemon=True).start()

    def check_auth(self):
        accs = self.selected_accounts() or [w['acc'] for w in self.row_w.values()]
        def work():
            for a in accs:
                name = a.get('name'); au = load_auth(a)
                if not au:
                    self.q.put('[CHECK] %s: chưa có auth — bấm "Lấy auth"' % name); continue
                try: u = json.loads(au['info']).get('username', '')
                except Exception: u = ''
                self.q.put('[CHECK] %s: đang kiểm tra token (user=%s) ...' % (name, u))
                r = verify_auth(au, log=lambda m: self.q.put(m), tag=name)
                if r: self.q.put('[CHECK] %s: ✔ AUTH HỢP LỆ (user=%s)' % (name, r))
                else: self.q.put('[CHECK] %s: ✖ AUTH KHÔNG HỢP LỆ / hết hạn — bấm "Lấy auth"' % name)
        threading.Thread(target=work, daemon=True).start()

    def run(self):
        sel = self.selected_accounts()
        if len(sel) != 2:
            messagebox.showwarning('Ghép bàn', 'Chọn ĐÚNG 2 tài khoản (tick cột "Chọn") rồi bấm GHÉP.'); return
        au1 = load_auth(sel[0]); au2 = load_auth(sel[1])
        if not auth_ok(au1) or not auth_ok(au2):
            messagebox.showwarning('Ghép bàn', 'Auth 1 trong 2 acc chưa có/hết hạn. Bấm "Lấy auth" trước.'); return
        try:
            g1 = json.loads(au1['info']).get('username', '?')
            g2 = json.loads(au2['info']).get('username', '?')
        except Exception:
            g1 = g2 = '?'
        self.log('[RUN] Yêu cầu ghép: %s (%s)  +  %s (%s)' % (sel[0].get('name'), g1, sel[1].get('name'), g2))
        bet = BET_MAP.get(self.betvar.get(), 100)
        try: gid = int(self.gidvar.get())
        except Exception: gid = 1
        mu = 2  # bàn SOLO 2 người (2 acc gặp nhau)
        self.stop[0] = False
        threading.Thread(target=lambda: do_pair(au1, au2, bet, gid, mu, log=lambda m: self.q.put(m), stop=self.stop), daemon=True).start()

    def stop_run(self):
        self.stop[0] = True; self.q.put('Đã yêu cầu dừng...')

    def _drain(self):
        try:
            while True: self.log(self.q.get_nowait())
        except queue.Empty: pass
        self.refresh(); self.root.after(400, self._drain)

def main():
    root = tk.Tk(); App(root); root.mainloop()

if __name__ == '__main__':
    main()
