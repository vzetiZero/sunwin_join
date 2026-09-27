# -*- coding: utf-8 -*-
"""
Sunwin Pair Tool (PySide6) - Ghép 2 tài khoản vào cùng 1 bàn SOLO, KHÔNG cần extension/GPM.
- "Thêm acc": mở Chrome ẩn danh -> vào trang đăng nhập -> tự bắt auth (info+signature+token).
- Acc hết hạn: bấm "Đăng nhập lại" -> mở Chrome -> đăng nhập -> lấy auth mới.
- "GHÉP BÀN SOLO": acc1 tạo bàn 2 người (không pass) -> acc2 vào; log gọn "server đang tìm".
Cần: pip install websocket-client msgpack PySide6
"""
import json, os, sys, time, threading, base64, urllib.request, subprocess, tempfile, socket, shutil
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QComboBox, QLineEdit, QPlainTextEdit,
                               QCheckBox, QFrame, QMessageBox, QInputDialog, QSizePolicy)

HERE = os.path.dirname(os.path.abspath(__file__))
ACC_FILE = os.path.join(HERE, "accounts.json")
LOG_FILE = os.path.join(HERE, "pair_tool.log")
GAME = "https://web.sunwin.villas/?affId=Sunwin"
LOBBY = "wss://ws-lby.azhkthg1.net/wsbinary"
CARD = "wss://ws-card04.azhkthg1.net/wsbinary%s"
ORIGIN = "https://web.sunwin.villas"
BET_LABELS = ['100','500','1K','2K','5K','10K','20K','50K','100K','200K','500K','1M']
BET_MAP = {'100':100,'500':500,'1K':1000,'2K':2000,'5K':5000,'10K':10000,'20K':20000,
           '50K':50000,'100K':100000,'200K':200000,'500K':500000,'1M':1000000}
VERBOSE = False

# ----------------------------- config -----------------------------
def load_accounts():
    if os.path.exists(ACC_FILE):
        try: return json.load(open(ACC_FILE, encoding='utf-8'))
        except Exception: pass
    return [
        {"name": "acc1", "auth": "auth_acc1.json"},
        {"name": "acc2", "auth": "auth_acc2.json"},
    ]
def save_accounts(accs):
    try: open(ACC_FILE, 'w', encoding='utf-8').write(json.dumps(accs, ensure_ascii=False, indent=2))
    except Exception: pass
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
def _uname(auth):
    try: return json.loads(auth['info']).get('username')
    except Exception: return None

# ----------------------------- chrome -----------------------------
def find_chrome():
    cands = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe"),
        r"E:\Tools\Google Chrome\App\Chrome-bin\chrome.exe",
    ]
    for c in cands:
        if c and os.path.isfile(c): return c
    return shutil.which('chrome') or shutil.which('chrome.exe')
def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
def launch_chrome(url=GAME, incognito=True):
    chrome = find_chrome()
    if not chrome:
        return None, None, None
    port = free_port()
    d = tempfile.mkdtemp(prefix='sunwin_')
    args = [chrome, '--remote-debugging-port=%d' % port, '--user-data-dir=' + d,
            '--no-first-run', '--no-default-browser-check', '--disable-features=Translate']
    if incognito: args.append('--incognito')
    args.append(url)
    try:
        proc = subprocess.Popen(args)
    except Exception:
        return None, None, None
    return proc, port, d
def close_chrome(proc, tmpdir):
    try:
        if proc: proc.terminate()
    except Exception: pass
    try:
        if tmpdir: shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception: pass

# ----------------------------- capture auth -----------------------------
def open_new_tab(port):
    for method in ('PUT', 'GET'):
        try:
            req = urllib.request.Request("http://127.0.0.1:%s/json/new?%s" % (port, GAME), method=method)
            with urllib.request.urlopen(req, timeout=8) as r: return json.load(r)
        except Exception: time.sleep(0.5)
    return None
def capture_auth(port, seconds=120, log=print):
    """Cho nguoi dung dang nhap; bat goi auth [1,'Simms',...] -> {info, signature, username}."""
    import websocket, msgpack
    t = open_new_tab(port)
    if not t or not t.get('webSocketDebuggerUrl'):
        log("!! Chưa mở được tab game (Chrome chưa sẵn sàng?)"); return None
    log("Đã mở trang game. Hãy ĐĂNG NHẬP (tài khoản đã lưu thì bấm Đăng nhập tiếp)...")
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
    end = time.time() + seconds; start = time.time(); auto = 0
    ws.settimeout(1.0)
    while time.time() < end:
        try: raw = ws.recv()
        except Exception: raw = None
        if auto < 4 and (time.time() - start) > (10 + auto * 12):
            auto += 1
            try:
                cmd('Runtime.evaluate', {'expression': AUTO, 'returnByValue': True})
                log("Chưa thấy auth — tự bấm đăng nhập (#%d)..." % auto)
            except Exception: pass
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
                try:
                    urllib.request.urlopen("http://127.0.0.1:%s/json/close/%s" % (port, t.get('id')), timeout=5).read()
                except Exception: pass
                return {'info': info, 'signature': obj[4].get('signature'), 'username': username}
    return None

def verify_auth(auth, log=print, tag='acc'):
    import websocket, msgpack
    try:
        u = json.loads(auth['info']).get('username', '')
    except Exception: u = ''
    try:
        ws = websocket.create_connection(LOBBY + '?token=' + json.loads(auth['info'])['wsToken'],
                                         max_size=None, origin=ORIGIN)
    except Exception as e:
        log("%s: kết nối lobby LỖI (%s)" % (tag, e)); return None
    ws.send_binary(msgpack.packb([1, 'Simms', '', '', {'info': auth['info'], 'signature': auth['signature']}], use_bin_type=True))
    end = time.time() + 7
    while time.time() < end:
        try:
            ws.settimeout(1.5); d = ws.recv()
        except Exception: continue
        if not isinstance(d, bytes): continue
        try: m = msgpack.unpackb(d, raw=False, strict_map_key=False)
        except Exception: continue
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

def leave_room(auth, rid, log=print, tag='acc'):
    import websocket, msgpack
    tok = json.loads(auth['info'])['wsToken']
    try:
        ws = websocket.create_connection(LOBBY + '?token=' + tok, max_size=None, origin=ORIGIN)
    except Exception:
        return False
    try:
        ws.send_binary(msgpack.packb([1, 'Simms', '', '', {'info': auth['info'], 'signature': auth['signature']}], use_bin_type=True))
        time.sleep(0.6)
        ws.send_binary(msgpack.packb([4, 'Simms', rid], use_bin_type=True))
        time.sleep(0.6)
    except Exception: pass
    try: ws.close()
    except Exception: pass
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
        while not stop[0]:
            try:
                self.ws.settimeout(2); d = self.ws.recv()
            except Exception: continue
            if not isinstance(d, bytes): continue
            try: m = msgpack.unpackb(d, raw=False, strict_map_key=False)
            except Exception: continue
            if isinstance(m, list) and len(m) >= 4 and m[0] == 1 and m[1] is True:
                self.auth_ok = True
            if isinstance(m, list) and len(m) >= 4 and m[0] == 3 and isinstance(m[1], bool):
                if self.rid is None or m[3] == self.rid:
                    self.joined = bool(m[1])
            if isinstance(m, list) and len(m) >= 2 and isinstance(m[1], dict):
                d2 = m[1]
                if 'dn' in d2 and 'uid' in d2 and self.dn is None:
                    self.dn = d2.get('dn')
                if 'ps' in d2:
                    self.players = [(p.get('dn'), p.get('pid')) for p in d2['ps']]

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
        except Exception: continue
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
        except Exception: pass
        try:
            c1 = Acc('acc1', (CARD % sid) + '?token=' + tok1); c1.auth(auth1)
            threading.Thread(target=c1.reader, args=(log, stop), daemon=True).start()
            c2 = Acc('acc2', (CARD % sid) + '?token=' + tok2); c2.auth(auth2)
            threading.Thread(target=c2.reader, args=(log, stop), daemon=True).start()
        except Exception:
            log("[Tìm bàn] Card socket lỗi — thử lại..."); time.sleep(2); continue
        time.sleep(0.6)
        c1.rid = rid; c2.rid = rid
        c1.send([3, 'Simms', rid, pwd]); c2.send([3, 'Simms', rid, pwd])

        done = False; guest = False; end = time.time() + 18
        while time.time() < end and not stop[0]:
            for w in (c1, c2):
                try: w.send([7, 'Simms', 3, 0])
                except Exception: pass
            dn1 = c1.dn; dn2 = c2.dn
            for a in (c1, c2):
                names_a = set(dn for dn, pid in (a.players or []) if dn)
                if dn1 and dn2 and dn1 in names_a and dn2 in names_a: done = True
                if (names_a - {dn1, dn2}): guest = True
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
        log("[Tìm bàn] Có người khác vào bàn — server đang tìm bàn khác..." if guest
            else "[Tìm bàn] Chưa gặp nhau — server đang tìm...")
        try: c1.ws.close(); c2.ws.close()
        except Exception: pass
    log("[Tìm bàn] Chưa ghép được — bấm GHÉP BÀN SOLO lại.")

# ----------------------------- GUI (PySide6) -----------------------------
STYLE = """
QWidget { background: #ffffff; color: #111827; font-family: 'Segoe UI'; font-size: 13px; }
QLabel#title { font-size: 20px; font-weight: 700; color: #b45309; }
QFrame#card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
QPushButton { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; }
QPushButton:hover { background: #e2e8f0; }
QPushButton#primary { background: #f59e0b; border: 1px solid #d97706; color: #111827; font-weight: 700; }
QPushButton#primary:hover { background: #fbbf24; }
QPushButton#danger { background: #ef4444; border: 1px solid #dc2626; color: #ffffff; font-weight: 700; }
QPushButton#blue { background: #0ea5e9; border: 1px solid #0284c7; color: #ffffff; font-weight: 700; }
QLineEdit, QComboBox, QPlainTextEdit { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 5px; padding: 3px 6px; }
QPlainTextEdit { font-family: Consolas, monospace; font-size: 12px; }
QCheckBox { spacing: 6px; }
"""

class LogBus(QObject):
    msg = Signal(str)

class Row(object):
    def __init__(self, acc):
        self.acc = acc
        self.chk = None; self.status = None

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.accounts = load_accounts()
        self.stop = [False]
        self.bus = LogBus()
        self.bus.msg.connect(self.append_log)
        self.rows = []

        self.setWindowTitle("Sunwin Pair Tool — bàn SOLO (PySide6)")
        self.resize(940, 620)
        self.setStyleSheet(STYLE)

        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(16, 14, 16, 14); root.setSpacing(10)

        title = QLabel("TLDT Sunwin — Ghép bàn SOLO (headless)"); title.setObjectName("title")
        root.addWidget(title)

        # accounts
        card = QFrame(); card.setObjectName("card"); cl = QVBoxLayout(card); cl.setContentsMargins(12, 10, 12, 10); cl.setSpacing(6)
        self.acc_box = QVBoxLayout(); self.acc_box.setSpacing(6); cl.addLayout(self.acc_box)
        root.addWidget(card)
        self.rebuild_rows()

        # toolbar
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Cược:"))
        self.bet = QComboBox(); self.bet.addItems(BET_LABELS); self.bet.setCurrentText('100'); bar.addWidget(self.bet)
        bar.addWidget(QLabel("Game (gid):"))
        self.gid = QLineEdit('1'); self.gid.setFixedWidth(50); bar.addWidget(self.gid)
        bar.addSpacing(8)
        self.btn_add = QPushButton("➕ Thêm acc"); self.btn_add.clicked.connect(self.add_account); bar.addWidget(self.btn_add)
        self.btn_check = QPushButton("Kiểm tra auth"); self.btn_check.setObjectName("blue"); self.btn_check.clicked.connect(self.check_auth); bar.addWidget(self.btn_check)
        self.btn_pair = QPushButton("⚡ GHÉP BÀN SOLO"); self.btn_pair.setObjectName("primary"); self.btn_pair.clicked.connect(self.run_pair); bar.addWidget(self.btn_pair)
        self.btn_stop = QPushButton("Dừng"); self.btn_stop.setObjectName("danger"); self.btn_stop.clicked.connect(self.stop_run); bar.addWidget(self.btn_stop)
        bar.addStretch(1)
        root.addLayout(bar)

        # log
        lc = QFrame(); lc.setObjectName("card"); ll = QVBoxLayout(lc); ll.setContentsMargins(10, 10, 10, 10)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ll.addWidget(self.log)
        root.addWidget(lc, 1)

        self.append_log("Sẵn sàng. Thêm acc (mở Chrome ẩn danh để đăng nhập) hoặc GHÉP BÀN SOLO.")

    # ---- accounts UI ----
    def rebuild_rows(self):
        while self.acc_box.count():
            it = self.acc_box.takeAt(0)
            w = it.widget()
            if w: w.deleteLater()
        self.rows = []
        for a in self.accounts:
            row = QHBoxLayout()
            r = Row(a)
            r.chk = QCheckBox(); row.addWidget(r.chk)
            row.addWidget(QLabel("<b>%s</b>" % a.get('name','?')))
            r.status = QLabel(self.status_text(a)); row.addWidget(r.status)
            row.addStretch(1)
            b = QPushButton("Đăng nhập lại" if load_auth(a) else "Lấy auth")
            b.clicked.connect(lambda _=False, aa=a: self.login_account(aa))
            row.addWidget(b)
            self.acc_box.addLayout(row)
            self.rows.append(r)

    def status_text(self, a):
        au = load_auth(a)
        if not au:
            return "— chưa có auth —"
        try:
            info = json.loads(au['info']); u = info.get('username',''); ts = info.get('timestamp',0)
        except Exception:
            u = ''; ts = 0
        left = (3*3600*1000 - (time.time()*1000 - ts)) / 3600000.0
        if left > 0:
            return "✔ còn hạn (~%.1fh) · %s" % (left, u)
        return "✖ HẾT HẠN · %s" % u

    def refresh_status(self):
        for r in self.rows:
            r.status.setText(self.status_text(r.acc))

    def selected(self):
        return [r.acc for r in self.rows if r.chk.isChecked()]

    # ---- logging ----
    def append_log(self, m):
        line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
        self.log.appendPlainText(line)
        try: open(LOG_FILE, 'a', encoding='utf-8').write(line + "\n")
        except Exception: pass
    def log(self, m):
        self.bus.msg.emit(m)

    # ---- actions ----
    def add_account(self):
        name, ok = QInputDialog.getText(self, "Thêm acc", "Tên acc (vd acc3):")
        if not ok or not name.strip(): return
        name = name.strip()
        if any(a.get('name') == name for a in self.accounts):
            QMessageBox.warning(self, "Thêm acc", "Tên acc đã tồn tại."); return
        acc = {"name": name, "auth": "auth_%s.json" % name}
        self.accounts.append(acc); save_accounts(self.accounts); self.rebuild_rows()
        self.login_account(acc)

    def login_account(self, a):
        def work():
            self.log("Đang mở Chrome ẩn danh để đăng nhập cho %s..." % a.get('name'))
            proc, port, tmp = launch_chrome(GAME, incognito=True)
            if not port:
                self.log("!! Không tìm thấy Chrome (chrome.exe). Cài Chrome hoặc cấu hình đường dẫn."); return
            self.log("Chrome đã mở (debug %s). Hãy đăng nhập..." % port)
            try:
                au = capture_auth(port, 150, log=lambda m: self.log(m))
            finally:
                close_chrome(proc, tmp)
            if not au:
                self.log("!! Chưa lấy được auth. Thử lại và đăng nhập đầy đủ."); return
            open(auth_path(a), 'w', encoding='utf-8').write(json.dumps(au, ensure_ascii=False))
            self.log("✔ Đã lưu auth cho %s (user=%s)" % (a.get('name'), au.get('username')))
        threading.Thread(target=work, daemon=True).start()

    def check_auth(self):
        accs = self.selected() or [r.acc for r in self.rows]
        def work():
            for a in accs:
                au = load_auth(a); name = a.get('name')
                if not au:
                    self.log("[CHECK] %s: chưa có auth" % name); continue
                self.log("[CHECK] %s: đang kiểm tra token..." % name)
                r = verify_auth(au, log=lambda m: self.log(m), tag=name)
                self.log("[CHECK] %s: ✔ AUTH HỢP LỆ (user=%s)" % (name, r) if r
                         else "[CHECK] %s: ✖ KHÔNG hợp lệ / hết hạn — bấm Đăng nhập lại" % name)
        threading.Thread(target=work, daemon=True).start()

    def run_pair(self):
        sel = self.selected()
        if len(sel) != 2:
            QMessageBox.warning(self, "Ghép bàn", "Tick ĐÚNG 2 tài khoản rồi bấm GHÉP."); return
        au1 = load_auth(sel[0]); au2 = load_auth(sel[1])
        if not auth_ok(au1) or not auth_ok(au2):
            QMessageBox.warning(self, "Ghép bàn", "Auth 1 trong 2 acc chưa có/hết hạn."); return
        try: bet = BET_MAP.get(self.bet.currentText(), 100)
        except Exception: bet = 100
        try: gid = int(self.gid.text())
        except Exception: gid = 1
        self.stop[0] = False
        threading.Thread(target=lambda: do_pair(au1, au2, bet, gid, 2, log=lambda m: self.log(m), stop=self.stop),
                         daemon=True).start()

    def stop_run(self):
        self.stop[0] = True
        self.log("Đã yêu cầu dừng...")

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = Main(); w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
