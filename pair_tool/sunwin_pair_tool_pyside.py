# -*- coding: utf-8 -*-
"""
Sunwin Pair Tool (PySide6) - Ghép 2 tài khoản vào cùng 1 bàn SOLO, KHÔNG cần extension/GPM.
- "Thêm acc": mở Chrome (profile riêng, hoặc "Chrome thật" nếu bị chặn login) -> tự bắt auth (info+signature+token).
- Acc hết hạn: bấm "Đăng nhập lại" -> mở Chrome -> đăng nhập -> lấy auth mới.
- "GHÉP BÀN SOLO": acc1 tạo bàn 2 người (không pass) -> acc2 vào; log gọn "server đang tìm".
Cần: pip install websocket-client msgpack PySide6
"""
import json, os, sys, time, threading, base64, re, urllib.request, subprocess, tempfile, socket, shutil
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
# Ten sanh -> gid (gameID). Nguon: config 'availableGames' client tai ve (prefabName ico_*).
# TLMN = ico_TLMN = 1  ->  khop voi gid=1 dang dung => tin cay.
GID_MAP = [
    ("Tiến Lên Miền Nam (TLMN)", 1),
    ("Sâm Lốc", 2),
    ("Mậu Binh", 4),
    ("Liêng", 5),
    ("Poker", 6),
    ("Xì Tố", 7),
    ("Phỏm", 8),
    ("Xì Dách (Blackjack)", 13),
    ("Chắn", 408),
]
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
def prof_dir(name):
    d = os.path.join(HERE, "_profiles", name)
    os.makedirs(d, exist_ok=True)
    return d
def launch_chrome(url=GAME, profile=None, incognito=False):
    """profile: thu muc user-data-dir luu phien (de tu dang nhap lai khi gia han)."""
    chrome = find_chrome()
    if not chrome:
        return None, None, None
    port = free_port()
    tmp = None
    if profile:
        ud = profile
    else:
        ud = tempfile.mkdtemp(prefix='sunwin_'); tmp = ud
    args = [chrome, '--remote-debugging-port=%d' % port, '--user-data-dir=' + ud,
            '--no-first-run', '--no-default-browser-check', '--disable-features=Translate',
            '--disable-blink-features=AutomationControlled', '--start-maximized']
    if incognito: args.append('--incognito')
    args.append(url)
    try:
        proc = subprocess.Popen(args)
    except Exception:
        return None, None, tmp
    return proc, port, tmp
def close_chrome(proc, tmpdir):
    try:
        if proc: proc.terminate()
    except Exception: pass
    try:
        if tmpdir: shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception: pass

# --- Chrome that (profile thuc cua nguoi dung, da dang nhap / da qua Cloudflare) ---
def chrome_user_data_dir():
    """Thu muc 'User Data' cua Chrome that (chua phien dang nhap san)."""
    cands = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\User Data"),
        os.path.join(os.environ.get('PROGRAMFILES', ''), r"Google\Chrome\User Data"),
    ]
    for c in cands:
        if c and os.path.isdir(c): return c
    return None

def chrome_running():
    try:
        out = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/NH'],
                                      stderr=subprocess.DEVNULL)
        return 'chrome.exe' in out.decode('utf-8', 'replace').lower()
    except Exception:
        return False

def kill_chrome():
    try:
        subprocess.run(['taskkill', '/IM', 'chrome.exe', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception: pass

# Cac file/thu muc quan trong cua 1 profile Chrome (de clone "đủ tham số")
CLONE_ITEMS = [
    "Local State",
    r"Default\Preferences",
    r"Default\Secure Preferences",
    r"Default\Network\Cookies",
    r"Default\Cookies",
    r"Default\Login Data",
    r"Default\Web Data",
    r"Default\Local Storage",
    r"Default\Session Storage",
    r"Default\IndexedDB",
]

def _copy_tree_best_effort(src, dst, log=print):
    """Copy từng file, bỏ qua file đang bị Chrome khoá (để copy được khi Chrome đang mở)."""
    n_ok = n_skip = 0
    for root, _dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        d = os.path.join(dst, rel) if rel != '.' else dst
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            continue
        for fn in files:
            try:
                shutil.copy2(os.path.join(root, fn), os.path.join(d, fn)); n_ok += 1
            except Exception:
                n_skip += 1
    return n_ok, n_skip

def clone_profile(src, dst, log=print):
    """Copy profile Chrome thật (cookie/localStorage) sang dst — chạy được cả khi Chrome ĐANG MỞ (best-effort)."""
    os.makedirs(os.path.join(dst, "Default"), exist_ok=True)
    for rel in CLONE_ITEMS:
        s = os.path.join(src, rel)
        d = os.path.join(dst, rel)
        try:
            if os.path.isdir(s):
                ok, skip = _copy_tree_best_effort(s, d, log)
                log("  · %s: %d file%s" % (rel, ok, (" (bỏ %d đang khoá)" % skip) if skip else ""))
            elif os.path.isfile(s):
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
                log("  · %s" % rel)
        except Exception as e:
            try: log("  (không copy được %s: %s)" % (rel, e))
            except Exception: pass

def rmtree_hard(path, tries=10):
    if not path: return
    for _ in range(tries):
        try:
            shutil.rmtree(path, ignore_errors=True)
            if not os.path.exists(path): return
        except Exception: pass
        time.sleep(0.5)

def close_chrome_via_cdp(port, timeout=5):
    """Đóng CHỈ instance Chrome của cổng debug này (không đụng Chrome khác người dùng đang mở)."""
    try:
        import websocket
        v = _http_json(port, '/json/version')
        wsurl = v.get('webSocketDebuggerUrl') if isinstance(v, dict) else None
        if not wsurl: return False
        ws = websocket.create_connection(wsurl, max_size=None, suppress_origin=True, timeout=timeout)
        ws.send(json.dumps({'id': 1, 'method': 'Browser.close'}))
        try: ws.close()
        except Exception: pass
        return True
    except Exception:
        return False

def close_our_chrome(proc, port):
    """Đóng instance ta vừa mở (ưu tiên CDP) — KHÔNG kill toàn bộ chrome.exe của người dùng."""
    if port and close_chrome_via_cdp(port):
        time.sleep(1.5)
    try:
        if proc: proc.terminate()
    except Exception: pass

# ----------------------------- capture auth -----------------------------
def _http_json(port, path, method='GET', timeout=5):
    try:
        req = urllib.request.Request("http://127.0.0.1:%s%s" % (port, path), method=method)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8', 'replace'))
    except Exception:
        return None

def open_new_tab(port):
    for method in ('PUT', 'GET'):
        t = _http_json(port, "/json/new?" + GAME, method=method)
        if t and t.get('webSocketDebuggerUrl'):
            return t
        time.sleep(0.5)
    return None

def _page_targets(port):
    data = _http_json(port, "/json")
    out = []
    if isinstance(data, list):
        for t in data:
            if not t.get('webSocketDebuggerUrl'):
                continue
            ty = t.get('type')
            u = (t.get('url') or '').lower()
            if ty == 'page' or (ty == 'iframe' and 'sunwin' in u):
                out.append(t)
    return out

AUTO_LOGIN = ("(function(){try{var cc=window.cc;if(!cc)return 'no-cc';var s=cc.director.getScene();"
    "function cn(c){try{return cc.js.getClassName(c);}catch(e){return '';}}"
    "var lob=null,seen=new Set();(function w(n,d){if(!n||d>30||seen.has(n)||lob)return;seen.add(n);"
    "var cs=[];try{cs=n.getComponents?n.getComponents(cc.Component):(n.components||[]);}catch(e){}"
    "cs.forEach(function(c){if(cn(c)==='LobbyViewController')lob=c;});"
    "(n.children||[]).forEach(function(k){w(k,d+1);});})(s,0);if(!lob)return 'no-lobby';var d=[];"
    "['autoLoginAcc','processLoginAcc','loginFromLPCompleted','reloginCompleted'].forEach(function(m){"
    "try{if(typeof lob[m]==='function'){lob[m]();d.push(m);}}catch(e){}});"
    "return 'login:'+d.join(',');})()")

def capture_auth(port, seconds=180, log=print):
    """Bắt gói auth [1,'Simms',...]. Gắn vào MỌI tab game (kể cả tab/popup mở sau)."""
    import websocket, msgpack
    state = {'auth': None}
    seen = set()
    deadline = time.time() + seconds

    def attach(target):
        tid = target.get('id'); wsurl = target.get('webSocketDebuggerUrl')
        page = target.get('url') or ''
        if not wsurl or tid in seen:
            return
        seen.add(tid)
        try:
            ws = websocket.create_connection(wsurl, max_size=None, suppress_origin=True)
        except Exception as e:
            log("  (không gắn được tab: %s)" % e); return
        mid = [0]
        def cmd(m, p=None):
            mid[0] += 1
            try: ws.send(json.dumps({'id': mid[0], 'method': m, 'params': p or {}}))
            except Exception: pass
        cmd('Network.enable')
        cmd('Runtime.enable')
        cmd('Log.enable')
        log("Đã gắn tab: %s" % (page or tid))
        is_game = 'sunwin' in page.lower()

        def loop():
            ws.settimeout(1.0)
            last_auto = 0.0
            auto_n = 0
            while not state['auth'] and time.time() < deadline:
                try: raw = ws.recv()
                except Exception: raw = None
                if is_game and auto_n < 2 and time.time() - last_auto > 8:
                    auto_n += 1
                    last_auto = time.time()
                    cmd('Runtime.evaluate', {'expression': AUTO_LOGIN, 'returnByValue': True})
                if not raw:
                    continue
                try: msg = json.loads(raw)
                except Exception:
                    continue
                if isinstance(msg.get('result'), dict):
                    val = (msg['result'].get('result') or {}).get('value')
                    if isinstance(val, str) and (val.startswith('login:') or val.startswith('no-')):
                        log("  [auto-login] %s" % val)
                meth = msg.get('method'); p = msg.get('params') or {}
                if meth == 'Network.webSocketCreated':
                    log("  ⟶ socket: %s" % (p.get('url', '').split('?')[0]))
                elif meth == 'Network.webSocketFrameSent':
                    resp = p.get('response') or {}
                    if resp.get('opcode') != 2: continue
                    try: obj = msgpack.unpackb(base64.b64decode(resp.get('payloadData', '')), raw=False, strict_map_key=False)
                    except Exception: continue
                    if isinstance(obj, list) and len(obj) >= 5 and obj[1] == 'Simms' and isinstance(obj[4], dict) and 'signature' in obj[4]:
                        info = obj[4].get('info')
                        try: username = json.loads(info).get('username')
                        except Exception: username = '?'
                        log("  ✔ BẮT ĐƯỢC AUTH (user=%s)" % username)
                        state['auth'] = {'info': info, 'signature': obj[4].get('signature'), 'username': username}
                elif meth == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = (r.get('url') or '').lower()
                    if p.get('type') in ('XHR', 'Fetch') and any(k in u for k in ('login', 'auth', 'signin', 'user')):
                        log("  [API %s] %s" % (r.get('status'), r.get('url', '').split('?')[0]))
                elif meth == 'Runtime.consoleAPICalled':
                    if p.get('type') in ('error', 'warning'):
                        txt = ' '.join(str(a.get('value', a.get('description', ''))) for a in (p.get('args') or []))
                        log("  [console.%s] %s" % (p.get('type'), txt[:300]))
                elif meth == 'Runtime.exceptionThrown':
                    det = p.get('exceptionDetails') or {}
                    txt = det.get('text') or ((det.get('exception') or {}).get('description', ''))
                    log("  [JS error] %s" % str(txt)[:300])
                elif meth == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    if e.get('level') in ('error', 'warning'):
                        log("  [browser.%s] %s" % (e.get('level'), (e.get('text') or '')[:300]))
                elif meth == 'Network.loadingFailed':
                    log("  [net fail] %s %s" % (p.get('errorText'), p.get('type')))
        threading.Thread(target=loop, daemon=True).start()

    initial = set(t.get('id') for t in _page_targets(port))
    if not any('sunwin' in (t.get('url') or '').lower() for t in _page_targets(port)):
        log("Đang mở tab game...")
        if not open_new_tab(port):
            log("!! Không mở được tab game (/json/new bị chặn?) — hãy tự mở https://web.sunwin.villas")
    log("Chờ đăng nhập (tối đa %ds) — hãy ĐĂNG NHẬP trong cửa sổ Chrome..." % seconds)
    while time.time() < deadline and not state['auth']:
        for t in _page_targets(port):
            u = (t.get('url') or '').lower()
            if t.get('id') in initial and 'sunwin' not in u:
                continue
            attach(t)
        time.sleep(1.5)
    return state['auth']

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

def _conn(url, tries=5):
    import websocket
    last = None
    for i in range(tries):
        try:
            return websocket.create_connection(url, max_size=None, origin=ORIGIN)
        except websocket.WebSocketBadStatusException as e:
            last = e
            code = getattr(e, 'status_code', None)
            if not (code and 500 <= code < 600):
                raise  # 4xx (token sai...) -> thử lại vô ích
            time.sleep(3)
        except Exception as e:
            last = e
            time.sleep(3)
    raise last

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
            try:
                s = str(m).lower()
                if 'error' in s or 'not_enough' in s or 'insufficient' in s:
                    log("%s: ⚠ server báo: %s" % (self.tag, _brief(m)))
            except Exception:
                pass

def _brief(o, n=300):
    try:
        s = o if isinstance(o, str) else json.dumps(o, ensure_ascii=False, default=str)
    except Exception:
        s = str(o)
    s = s.replace('\n', ' ')
    return s if len(s) <= n else s[:n] + '...'

def _create_room(auth1, gid, bet, mu, pwd, log):
    import msgpack
    tok1 = json.loads(auth1['info'])['wsToken']
    try:
        l1 = Acc('acc1-lobby', LOBBY + '?token=' + tok1); l1.auth(auth1)
    except Exception as e:
        log("[Tìm bàn] Kết nối lobby lỗi (%s)" % e); return None, None
    time.sleep(1.0)
    try:
        l1.send([6, 'Simms', 'channelPlugin', {'cmd': 308, 'gid': gid, 'aid': 1, 'b': bet, 'Mu': mu, 'pwd': pwd, 'iJ': False}])
    except Exception as e:
        log("[Tìm bàn] Gửi tạo bàn lỗi (%s)" % e); return None, None
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
        # In moi phan hoi khac de thay LOI THAT (het tien, sai cuoc, ...)
        if isinstance(m, list) and len(m) >= 2 and m[0] == 1 and m[1] is True:
            continue  # ack dang nhap
        log("[Tạo bàn] Server trả về: %s" % _brief(m))
    return None, None

def do_pair(auth1, auth2, bet, gid, mu, log, stop, pwd=''):
    log("[Tìm bàn] Bắt đầu ghép 2 acc — bàn SOLO (%s người), cược %s, gid %s, không pass" % (mu, bet, gid))
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
        try:
            rid, sid = _create_room(auth1, gid, bet, mu, pwd, log)
        except Exception as e:
            log("[Tìm bàn] Máy chủ lỗi (522/Cloudflare?) (%s) — thử lại sau 3s..." % e); time.sleep(3); continue
        if not rid:
            log("[Tìm bàn] Server chưa cho tạo bàn (có thể HẾT TIỀN/không đủ cược, sai gid, hoặc server bận) — thử lại..."); time.sleep(2); continue
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
    rows = Signal()

class Row(object):
    def __init__(self, acc):
        self.acc = acc
        self.chk = None; self.status = None; self.name_lbl = None; self.btn = None

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.accounts = load_accounts()
        self.stop = [False]
        self.bus = LogBus()
        self.bus.msg.connect(self.append_log)
        self.bus.rows.connect(self.refresh_rows)
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
        rowm = QHBoxLayout()
        rowm.addWidget(QLabel("Profile Chrome:"))
        self.chrome_mode = QComboBox()
        self.chrome_mode.addItems([
            "Riêng (giữ lại)",
            "Đồng bộ Chrome chính (xoá sau)",
            "Chrome thật (đóng Chrome)",
            "Mới tạm (xoá sau)",
        ])
        self.chrome_mode.setToolTip(
            "Riêng: profile riêng cho từng acc, giữ lại để lần sau tự đăng nhập. KHÔNG cần đóng Chrome chính.\n"
            "Đồng bộ Chrome chính: copy cookie/localStorage từ Chrome bạn ĐANG MỞ (không cần đóng) ra bản tạm -> login -> tự xoá.\n"
            "Chrome thật (đóng Chrome): dùng đúng profile Chrome chính — PHẢI đóng Chrome trước.\n"
            "Mới tạm: profile mới hoàn toàn -> login -> tự xoá.")
        rowm.addWidget(self.chrome_mode, 1)
        cl.addLayout(rowm)
        self.acc_box = QVBoxLayout(); self.acc_box.setSpacing(6); cl.addLayout(self.acc_box)
        root.addWidget(card)
        self.rebuild_rows()

        # toolbar
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Cược:"))
        self.bet = QComboBox(); self.bet.addItems(BET_LABELS); self.bet.setCurrentText('100'); bar.addWidget(self.bet)
        bar.addWidget(QLabel("Sảnh game:"))
        self.game = QComboBox(); self.game.setEditable(True); self.game.setMinimumWidth(210)
        for _name, _gid in GID_MAP:
            self.game.addItem("%s  (gid %s)" % (_name, _gid if _gid is not None else "?"), _gid)
        self.game.setToolTip("Chọn sảnh theo TÊN — tool tự map ra gid.\n"
                             "Sảnh nào còn 'gid ?' thì gõ số gid vào ô này (vd: 1).")
        bar.addWidget(self.game)
        bar.addSpacing(8)
        self.btn_add = QPushButton("➕ Thêm acc"); self.btn_add.clicked.connect(self.add_account); bar.addWidget(self.btn_add)
        self.btn_check = QPushButton("Kiểm tra auth"); self.btn_check.setObjectName("blue"); self.btn_check.clicked.connect(self.check_auth); bar.addWidget(self.btn_check)
        self.btn_pair = QPushButton("⚡ GHÉP BÀN SOLO"); self.btn_pair.setObjectName("primary"); self.btn_pair.clicked.connect(self.run_pair); bar.addWidget(self.btn_pair)
        self.btn_stop = QPushButton("Dừng"); self.btn_stop.setObjectName("danger"); self.btn_stop.clicked.connect(self.stop_run); bar.addWidget(self.btn_stop)
        bar.addStretch(1)
        root.addLayout(bar)

        # log
        lc = QFrame(); lc.setObjectName("card"); ll = QVBoxLayout(lc); ll.setContentsMargins(10, 10, 10, 10)
        self.log_view = QPlainTextEdit(); self.log_view.setReadOnly(True); self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ll.addWidget(self.log_view)
        root.addWidget(lc, 1)

        self.append_log("Sẵn sàng. Thêm acc (mở Chrome để đăng nhập) hoặc GHÉP BÀN SOLO.")

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
            r.name_lbl = QLabel(self.display_name(a)); row.addWidget(r.name_lbl)
            r.status = QLabel(self.status_text(a)); row.addWidget(r.status)
            row.addStretch(1)
            r.btn = QPushButton("Gia hạn auth" if load_auth(a) else "Đăng nhập")
            r.btn.clicked.connect(lambda _=False, aa=a: self.login_account(aa))
            row.addWidget(r.btn)
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

    def display_name(self, a):
        u = a.get('username') or ''
        n = a.get('name', '?')
        if u:
            return "<b>%s</b> <span style='color:#94a3b8'>(%s)</span>" % (u, n)
        return "<b>%s</b>" % n

    def refresh_rows(self):
        """Cập nhật tên/ trạng thái / nút cho từng dòng (chạy ở luồng GUI)."""
        for r in self.rows:
            try:
                if r.name_lbl: r.name_lbl.setText(self.display_name(r.acc))
                if r.status: r.status.setText(self.status_text(r.acc))
                if r.btn: r.btn.setText("Gia hạn auth" if load_auth(r.acc) else "Đăng nhập")
            except Exception:
                pass

    def refresh_status(self):
        self.refresh_rows()

    def selected(self):
        return [r.acc for r in self.rows if r.chk.isChecked()]

    def current_gid(self):
        """Lay gid tu o 'Sảnh game': uu tien item data, neu nguoi dung tu go so thi lay so dau tien."""
        d = self.game.currentData()
        if isinstance(d, int):
            return d
        m = re.search(r'(\d+)', self.game.currentText() or '')
        return int(m.group(1)) if m else None

    # ---- logging ----
    def append_log(self, m):
        line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
        self.log_view.appendPlainText(line)
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
        mode = self.chrome_mode.currentText()
        need_real = mode in ("Đồng bộ Chrome chính (xoá sau)", "Chrome thật (đóng Chrome)")
        need_close = mode == "Chrome thật (đóng Chrome)"
        real_dir = chrome_user_data_dir() if need_real else None
        if need_real and not real_dir:
            QMessageBox.warning(self, "Chrome thật", "Không tìm thấy profile Chrome thật (thư mục User Data).")
            return
        if need_close and chrome_running():
            r = QMessageBox.question(
                self, "Cần đóng Chrome",
                "Chế độ 'Chrome thật' dùng đúng profile Chrome chính nên phải ĐÓNG toàn bộ Chrome.\n\n"
                "Nếu KHÔNG muốn đóng Chrome, hãy chọn 'Đồng bộ Chrome chính (xoá sau)'.\n\n"
                "Tự động đóng Chrome bây giờ? (Lưu việc đang làm trước!)",
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                self.log("Đã huỷ. Hãy đóng Chrome, hoặc chọn 'Đồng bộ Chrome chính (xoá sau)'.")
                return

        def close_and_wait():
            kill_chrome()
            for _ in range(20):
                if not chrome_running(): break
                time.sleep(0.5)

        def work():
            existing = load_auth(a) is not None
            tmpdir = None
            proc = port = None
            try:
                if mode == "Riêng (giữ lại)":
                    pdir = prof_dir(a.get('name'))
                elif mode == "Đồng bộ Chrome chính (xoá sau)":
                    tmpdir = tempfile.mkdtemp(prefix='sunwin_sync_')
                    self.log("Đang copy cookie/localStorage từ Chrome chính (KHÔNG cần đóng Chrome)...")
                    clone_profile(real_dir, tmpdir, log=lambda m: self.log(m))
                    pdir = tmpdir
                elif mode == "Chrome thật (đóng Chrome)":
                    self.log("Đang đóng Chrome để dùng profile thật cho %s..." % a.get('name'))
                    close_and_wait()
                    pdir = real_dir
                else:  # Mới tạm (xoá sau)
                    tmpdir = tempfile.mkdtemp(prefix='sunwin_tmp_')
                    pdir = tmpdir

                self.log(("Gia hạn auth" if existing else "Đăng nhập") + " cho %s — mở Chrome..." % a.get('name'))
                proc, port, _ = launch_chrome(GAME, profile=pdir, incognito=False)
                if not port:
                    self.log("!! Không tìm thấy Chrome (chrome.exe)."); return
                # Xac nhan cong debug thuc su mo (Chrome 136+ chan debug tren profile mac dinh)
                dbg_ok = False
                for _ in range(10):
                    if _http_json(port, '/json/version') is not None: dbg_ok = True; break
                    time.sleep(0.5)
                if not dbg_ok:
                    self.log("!! Không mở được cổng debug %s." % port)
                    if mode == "Chrome thật (đóng Chrome)":
                        self.log("   Chrome 136+ CHẶN debug trên profile mặc định → chọn 'Đồng bộ Chrome chính (xoá sau)'.")
                    self.log("   Thử lại với 'Đồng bộ Chrome chính (xoá sau)' hoặc 'Mới tạm (xoá sau)'.")
                    return
                self.log("Chrome đã mở (debug %s). Nếu đã lưu đăng nhập, chờ tự vào game; nếu chưa thì đăng nhập." % port)
                au = capture_auth(port, 180, log=lambda m: self.log(m))
                if not au:
                    self.log("!! Chưa lấy được auth. Thử lại (đăng nhập đầy đủ)."); return
                open(auth_path(a), 'w', encoding='utf-8').write(json.dumps(au, ensure_ascii=False))
                if au.get('username'):
                    a['username'] = au.get('username')
                    save_accounts(self.accounts)
                self.log("✔ Đã lưu auth cho %s (user=%s)" % (a.get('name'), au.get('username')))
                self.bus.rows.emit()
            finally:
                close_our_chrome(proc, port)
                if tmpdir and mode in ("Đồng bộ Chrome chính (xoá sau)", "Mới tạm (xoá sau)"):
                    rmtree_hard(tmpdir)
                    self.log("Đã xoá profile tạm.")
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
        gid = self.current_gid()
        if gid is None:
            QMessageBox.warning(self, "Thiếu gid", "Sảnh này chưa có gid.\nHãy gõ số gid vào ô 'Sảnh game' (ví dụ: 1).")
            return
        self.stop[0] = False
        def run():
            try:
                do_pair(au1, au2, bet, gid, 2, log=lambda m: self.log(m), stop=self.stop)
            except Exception as e:
                self.log("!! Lỗi ghép bàn: %s" % e)
                self.log("   (Nếu là 522/Cloudflare — máy chủ game đang quá tải, chờ 1-2 phút rồi bấm GHÉP lại.)")
        threading.Thread(target=run, daemon=True).start()

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
