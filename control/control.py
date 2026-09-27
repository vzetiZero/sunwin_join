# -*- coding: utf-8 -*-
"""
Sunwin Control — Nhiều extension, mỗi kết nối một hàng ngang.
ĐÃ HỦY BỎ BẢN QUYỀN & XÁC THỰC PHẦN CỨNG (CRACKED / DEV BYPASS)
"""

import csv
import io
import json
import os
import socket
import ssl
import sys
import threading
import time
import urllib.parse as urllib_parse
import urllib.request as urllib_request
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tkinter import BooleanVar, Button, Checkbutton, Entry, Frame, Label, PhotoImage, StringVar, Tk, messagebox, ttk

BET_LABELS = [
    '100', '500', '1K', '2K', '5K', '10K', '20K', '50K',
    '100K', '200K', '500K', '1M', '2M', '5M', '10M'
]

BET_MAP = {
    '100': 100,
    '500': 500,
    '1K': 1000,
    '2K': 2000,
    '5K': 5000,
    '10K': 10000,
    '20K': 20000,
    '50K': 50000,
    '100K': 100000,
    '200K': 200000,
    '500K': 500000,
    '1M': 1000000,
    '2M': 2000000,
    '5M': 5000000,
    '10M': 10000000,
}

HOST = '127.0.0.1'
PORT = 17831
STALE_SEC = 12
LICENSE_CHECK_SEC = 999999
CLOSE_DELAY_MS = 15000

BG = '#070b14'
CARD = '#0f172a'
MUTED = '#64748b'
LINE = '#1e293b'


def app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = app_dir()
KNOWN_PATH = os.path.join(BASE_DIR, 'known_names.json')
KEYS_PATH = os.path.join(BASE_DIR, 'keys.json')
SERVER_PATH = os.path.join(BASE_DIR, 'license_server.json')
SAVED_KEY_PATH = os.path.join(BASE_DIR, 'saved_key.json')
BIND_PATH = os.path.join(BASE_DIR, 'device_bind.json')

# RLock (re-entrant): set_action() giữ lock rồi gọi capture_shared_from_clients()
# -> list_clients() xin lại cùng lock. Lock thường sẽ gây DEADLOCK khi bấm "Tìm phòng".
state_lock = threading.RLock()
clients = {}
known_names = []
xa_delay_ms = 1000
chong_pha = False
out_guest = False
test_one_round = False

# BYPASS LICENSE: Mặc định luôn là TRUE và vĩnh viễn
licensed = True
license_status = 'Bản quyền vĩnh viễn (Đã kích hoạt)'
license_max_clients = 999
pending_key = 'VIP-BYPASS-ACTIVE'
last_license_check = 0
license_checking = False
license_gen = 0
http_server = None
ui_root = None
control_closing = False
close_job = None

shared_room = {
    'soBan': '',
    'roomId': None,
    'serverId': '',
    'bet': 100,
    'hostName': '',
}

event_log = []

sniff_log = []


def log_event(msg):
    try:
        event_log.append(time.strftime('%H:%M:%S') + ' ' + str(msg))
        if len(event_log) > 200:
            del event_log[:-200]
    except Exception:
        pass


def format_money(n):
    if n is None or n == '':
        return '—'
    try:
        x = float(n)
    except (TypeError, ValueError):
        return str(n)
    ax = abs(x)
    if ax >= 1000000:
        return '{:.2f}M'.format(x / 1000000)
    if ax >= 1000:
        s = '{:.2f}'.format(x / 1000).rstrip('0').rstrip('.')
        return s + 'K'
    if x == int(x):
        return '{:,}'.format(int(x)).replace(',', '.')
    return '{:,.2f}'.format(x)


def bet_text(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 100
    for label, val in BET_MAP.items():
        if val == n:
            return label
    return format_money(n)


def parse_delay_sec(raw):
    try:
        n = float(str(raw).strip().replace(',', '.'))
    except (TypeError, ValueError):
        n = 1.0
    if n < 0:
        n = 0.0
    elif n > 60:
        n = 60.0
    return n


def parse_bet(label):
    return BET_MAP.get(str(label).strip().upper(), 100)


def reset_session_data():
    global known_names
    known_names = []
    save_known_names()
    shared_room['hostName'] = ''
    shared_room['soBan'] = ''
    shared_room['roomId'] = None
    shared_room['serverId'] = ''
    shared_room['bet'] = 100


def save_known_names():
    try:
        with open(KNOWN_PATH, 'w', encoding='utf-8') as f:
            json.dump(known_names, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def remember_name(name):
    if not name:
        return
    n = str(name).strip()
    if not n:
        return
    key = n.lower()
    for existing in known_names:
        if existing.lower() == key:
            return
    known_names.append(n)
    save_known_names()


def machine_id():
    """Bỏ qua lấy HWID máy"""
    return 'BYPASS-MACHINE-ID'


def load_saved_key():
    return 'VIP-BYPASS-ACTIVE'


def save_saved_key(key):
    pass


def clear_saved_key():
    pass


def license_url():
    return ''


def current_key():
    return 'VIP-BYPASS-ACTIVE'


def is_licensed():
    """Bypass hoàn toàn kiểm tra license"""
    return True


def drop_license(msg):
    """Không bao giờ drop license"""
    pass


def grant_license(msg='Bản quyền vĩnh viễn (Đã kích hoạt)', max_clients=999):
    global licensed, license_status, license_max_clients, control_closing
    with state_lock:
        licensed = True
        license_status = msg
        license_max_clients = max_clients
        control_closing = False


def parse_expires(s):
    return None


def as_bool(v):
    return True


def take_device_slot(key, device, max_machines=999):
    """Bỏ qua kiểm tra giới hạn máy"""
    return True


def eval_key_row(row, device):
    return {'ok': True, 'expires': 'Vĩnh viễn', 'max_clients': 999}


def check_key_local(key, device):
    return {'ok': True, 'expires': 'Vĩnh viễn', 'max_clients': 999}


def parse_csv_keys(text):
    return []


def fetch_url_text(url):
    return ''


def check_key_remote(key, device):
    return {'ok': True, 'expires': 'Vĩnh viễn', 'max_clients': 999}


def apply_check_result(key, res):
    grant_license('Bản quyền vĩnh viễn (Đã kích hoạt)', 999)


def close_control_ui(msg):
    """Bỏ qua đóng ứng dụng"""
    pass


def verify_current_key():
    """Bỏ qua xác thực từ xa"""
    grant_license('Bản quyền vĩnh viễn (Đã kích hoạt)', 999)


def client_id(body):
    if not body:
        return ''
    cid = body.get('id')
    if cid is None:
        return ''
    return str(cid).strip()


def prune_locked():
    now = time.time()
    dead = [k for k, c in clients.items() if now - c.get('ts', 0) > STALE_SEC]
    for k in dead:
        clients.pop(k, None)


def list_clients():
    with state_lock:
        prune_locked()
        rows = list(clients.values())
        rows.sort(key=lambda x: x.get('order', 0))
        return rows


def fill_shared_room(host_name, so_ban, room_id, server_id, bet):
    host_name = str(host_name or '').strip()
    so_ban = str(so_ban or '').strip()
    if not host_name or not so_ban:
        return False
    shared_room['hostName'] = host_name
    shared_room['soBan'] = so_ban
    shared_room['roomId'] = room_id
    shared_room['serverId'] = server_id
    try:
        shared_room['bet'] = int(bet) if bet is not None else 100
    except (TypeError, ValueError):
        shared_room['bet'] = 100
    return True


def capture_shared_from_clients():
    for c in list_clients():
        lab = str(c.get('phase_label') or '')
        if 'Đã tạo phòng thành công' in lab:
            if fill_shared_room(
                c.get('name'),
                c.get('soBan') or '',
                c.get('roomId'),
                c.get('serverId') or '',
                c.get('bet')
            ):
                return True
    return False


def clear_shared_room():
    shared_room['hostName'] = ''
    shared_room['soBan'] = ''
    shared_room['roomId'] = None
    shared_room['serverId'] = ''
    shared_room['bet'] = 100


def activate_pending_joins_locked():
    """Gọi khi ĐANG giữ state_lock. Khi đã có phòng chung, kích hoạt mọi client
    đang xếp hàng chờ join để lao vào đúng bàn của host."""
    if not shared_room.get('hostName'):
        capture_shared_from_clients()
    if not shared_room.get('hostName'):
        return
    host = str(shared_room.get('hostName') or '')
    room_bet = shared_room.get('bet', 100)
    for c in clients.values():
        if c.get('pendingJoin') and not c.get('hunt'):
            c['pendingJoin'] = False
            c['hunt'] = True
            c['halt'] = False
            c['action'] = 'join'
            c['bet'] = room_bet
            c['phase'] = 'hunt'
            c['phase_label'] = 'Đang vào bàn của ' + host
            log_event('activate_join %s -> %s' % (str(c.get('id'))[-6:], host))


def set_pair(create_cid, join_cid, bet=None, test=False):
    """1 thao tác cho 2 tài khoản: acc create_cid tạo bàn, acc join_cid vào đúng bàn đó."""
    with state_lock:
        cur_create = clients.get(create_cid)
        if not cur_create:
            return False
        creator_name = str(cur_create.get('name') or '').strip()
        # Phòng chung cũ không phải của acc sẽ tạo -> xoá để chờ phòng mới
        if shared_room.get('hostName') and shared_room.get('hostName') != creator_name:
            clear_shared_room()
        if test:
            for _a, _b in ((create_cid, join_cid), (join_cid, create_cid)):
                _c = clients.get(_a)
                if _c:
                    _c['pairTest'] = True
                    _c['pairMate'] = _b
                    _c['sawPlaying'] = False
                    _c['pairDone'] = False
    set_action(create_cid, 'create', bet)
    set_action(join_cid, 'join', bet)
    with state_lock:
        activate_pending_joins_locked()
    log_event('pair create=%s join=%s bet=%s test=%s' % (str(create_cid)[-6:], str(join_cid)[-6:], bet, test))
    return True


def set_action(cid, action, bet=None):
    with state_lock:
        cur = clients.get(cid)
        if not cur:
            return
        log_event('act %s %s bet=%s' % (str(cid)[-6:], action, bet))
        cur['ts'] = time.time()
        cur['halt'] = False
        if action == 'join':
            capture_shared_from_clients()
            if not shared_room.get('hostName'):
                # Chưa có phòng chung -> xếp hàng chờ, khi host tạo xong sẽ tự vào
                cur['hunt'] = False
                cur['pendingJoin'] = True
                cur['action'] = 'join'
                if bet is not None:
                    try:
                        cur['bet'] = int(bet)
                    except (TypeError, ValueError):
                        cur['bet'] = 100
                cur['phase'] = 'idle'
                cur['phase_label'] = 'Chờ phòng chung…'
                return
        cur['pendingJoin'] = False
        cur['hunt'] = True
        cur['action'] = action
        if bet is not None:
            try:
                cur['bet'] = int(bet)
            except (TypeError, ValueError):
                cur['bet'] = 100
        cur['phase'] = 'hunt'
        cur['phase_label'] = f"Đang {'tạo' if action == 'create' else 'tìm'} bàn {bet_text(cur.get('bet', 100))}"


def stop_action(cid):
    with state_lock:
        cur = clients.get(cid)
        if not cur:
            return
        log_event('stop %s' % (str(cid)[-6:],))
        cur['ts'] = time.time()
        cur['hunt'] = False
        cur['pendingJoin'] = False
        cur['action'] = ''
        cur['halt'] = True
        cur['phase'] = 'halt'
        cur['phase_label'] = 'Đã dừng'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Tắt log console cho sạch
        return

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Request-Private-Network')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def _json(self, code, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _body(self):
        try:
            length = int(self.headers.get('Content-Length', 0) or 0)
            if length > 0:
                raw = self.rfile.read(length)
                return json.loads(raw.decode('utf-8', errors='ignore'))
        except Exception:
            pass
        return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/health'):
            self._json(200, {'ok': True, 'licensed': True, 'clients': len(list_clients())})
        elif path == '/state':
            self._json(200, {'ok': True, 'clients': list_clients(), 'sharedRoom': shared_room, 'events': event_log[-100:]})
        elif path == '/sniff':
            self._json(200, {'ok': True, 'count': len(sniff_log), 'frames': sniff_log[-1500:]})
        elif path == '/sniff/clear':
            del sniff_log[:]
            self._json(200, {'ok': True})
        else:
            self._json(404, {'ok': False, 'error': 'not_found'})

    def do_POST(self):
        path = self.path.split('?')[0]
        body = self._body()
        cid = client_id(body)

        if not cid:
            self._json(400, {'ok': False, 'error': 'missing_id'})
            return

        now = time.time()

        if path == '/connect':
            with state_lock:
                prune_locked()
                prev = clients.get(cid)
                order = prev.get('order') if prev else (max([c.get('order', 0) for c in clients.values()] or [0]) + 1)
                clients[cid] = {
                    'id': cid,
                    'order': order,
                    'host': body.get('host', ''),
                    'ts': now,
                    'player': None,
                    'name': '',
                    'money': None,
                    'phase': 'idle',
                    'phase_label': 'Đang ở sảnh',
                    'remain': 0,
                    'cards': [],
                    'hunt': False,
                    'action': '',
                    'bet': 100,
                    'halt': False,
                    'soBan': '',
                    'roomId': None,
                    'serverId': '',
                }
            self._json(200, {'ok': True})

        elif path == '/disconnect':
            with state_lock:
                clients.pop(cid, None)
            self._json(200, {'ok': True})

        elif path == '/state':
            player = body.get('player') or {}
            pname = str(player.get('name') or '').strip()
            pmoney = player.get('money')
            pphase = str(player.get('phase') or 'idle')
            pphase_label = str(player.get('phaseLabel') or 'Đang ở sảnh')

            hunt_found = bool(body.get('huntFound'))
            so_ban = str(body.get('soBan') or '')
            room_id = body.get('roomId')
            server_id = str(body.get('serverId') or '')
            found_bet = body.get('bet')
            host_name = str(body.get('hostName') or pname or '')

            pair_stop = []
            with state_lock:
                cur = clients.get(cid)
                if not cur:
                    order = max([c.get('order', 0) for c in clients.values()] or [0]) + 1
                    cur = {
                        'id': cid,
                        'order': order,
                        'host': body.get('host', ''),
                        'bet': 100,
                        'hunt': False,
                        'action': '',
                        'halt': False,
                    }
                    clients[cid] = cur

                cur['ts'] = now
                cur['player'] = player
                cur['name'] = pname
                cur['money'] = pmoney
                cur['remain'] = body.get('remain', 0)
                cur['cards'] = body.get('cards', [])
                cur['soBan'] = so_ban
                cur['roomId'] = room_id
                cur['serverId'] = server_id

                cur['dbg'] = body.get('dbg')
                try:
                    _d = body.get('dbg') or {}
                    _dstr = ''
                    if _d:
                        _dstr = ' mode=%s hs=%s tp=%s tm=%s opp=%s host=%s guest=%s occ=%s hn=%s saw=%s' % (
                            _d.get('mode'), _d.get('hs'), _d.get('tp'), _d.get('tm'), _d.get('opp'),
                            _d.get('host'), _d.get('guest'), _d.get('occ'), _d.get('hn'), _d.get('saw'))
                    _hk = str(player.get('phase') or '') + '|' + str(player.get('phaseLabel') or '') + _dstr
                    if cur.get('_histKey') != _hk:
                        cur['_histKey'] = _hk
                        _h = cur.setdefault('hist', [])
                        _h.append(time.strftime('%H:%M:%S') + ' ' + _hk)
                        if len(_h) > 80:
                            del _h[:-80]
                except Exception:
                    pass

                if hunt_found and so_ban:
                    fill_shared_room(host_name, so_ban, room_id, server_id, found_bet or cur.get('bet', 100))
                    remember_name(host_name)
                    log_event('HUNT_FOUND %s soBan=%s roomId=%s serverId=%s bet=%s' % (host_name, so_ban, room_id, server_id, found_bet))
                    activate_pending_joins_locked()

                if pname:
                    remember_name(pname)

                # Trạng thái hiện tại
                if not cur.get('hunt'):
                    cur['phase'] = pphase
                    cur['phase_label'] = pphase_label

                hunt_on = bool(cur.get('hunt'))
                hunt_mode = str(cur.get('action') or 'create')
                hunt_bet = cur.get('bet', 100)
                halted = bool(cur.get('halt'))

                # Chế độ Test 1 ván: acc đã đánh xong 1 ván -> dừng cả cặp
                if cur.get('pairTest'):
                    _pp = str(player.get('phase') or '')
                    if _pp in ('xa', 'vs_guest'):
                        cur['sawPlaying'] = True
                    elif cur.get('sawPlaying') and _pp in ('wait_guest', 'vs_guest_done', 'lobby', 'table_broken', 'leave_set'):
                        cur['pairDone'] = True
                        pair_stop.append(cid)
                        mate = cur.get('pairMate')
                        if mate:
                            pair_stop.append(mate)

            if pair_stop:
                for _cid in set(pair_stop):
                    stop_action(_cid)
                with state_lock:
                    for _cid in set(pair_stop):
                        _c = clients.get(_cid)
                        if _c:
                            _c['pairTest'] = False
                            _c['pairMate'] = None
                            _c['sawPlaying'] = False
                            _c['pairDone'] = False

            self._json(200, {
                'ok': True,
                'hunt': hunt_on,
                'mode': hunt_mode,
                'bet': hunt_bet,
                'sharedRoom': shared_room,
                'knownNames': list(known_names),
                'xaDelay': xa_delay_ms,
                'chongPha': chong_pha,
                'outGuest': out_guest,
                'roomPass': '',
                'halt': halted,
            })
        elif path == '/sniff':
            try:
                sniff_log.append({
                    't': body.get('t'),
                    'dir': str(body.get('dir') or ''),
                    'url': str(body.get('url') or ''),
                    'len': body.get('len'),
                    'data': body.get('data'),
                })
                if len(sniff_log) > 4000:
                    del sniff_log[:-4000]
            except Exception:
                pass
            self._json(200, {'ok': True})
        else:
            self._json(404, {'ok': False, 'error': 'unknown_path'})


class App:
    def __init__(self, root):
        global ui_root
        self.root = root
        ui_root = root

        root.title('Sunwin Control — Tool Gom Bàn & Xả Bài')
        root.geometry('980x400')
        root.configure(bg=BG)
        root.minsize(900, 300)

        # Icon window
        try:
            icon_file = os.path.join(BASE_DIR, 'sunwin_icon.png')
            if os.path.isfile(icon_file):
                self.win_icon = PhotoImage(file=icon_file)
                root.iconphoto(True, self.win_icon)
        except Exception:
            pass

        pad = Frame(root, bg=BG)
        pad.pack(fill='both', expand=True, padx=16, pady=14)

        # Top Bar
        top = Frame(pad, bg=BG)
        top.pack(fill='x')

        try:
            logo_file = os.path.join(BASE_DIR, 'sunwin_logo.png')
            if os.path.isfile(logo_file):
                self.logo_img = PhotoImage(file=logo_file)
                h = self.logo_img.height()
                if h > 48:
                    sub = max(1, int(round(h / 48.0)))
                    self.logo_img = self.logo_img.subsample(sub, sub)
                Label(top, image=self.logo_img, bg=BG).pack(side='left', padx=(0, 10))
        except Exception:
            pass

        Label(
            top,
            text='TLDT Sunwin — Điều Khiển Gom Bàn',
            fg='#f0c040',
            bg=BG,
            font=('Segoe UI', 16, 'bold')
        ).pack(side='left')

        self.lbl_count = Label(top, text='0 kết nối', fg=MUTED, bg=BG, font=('Segoe UI', 10))
        self.lbl_count.pack(side='right', padx=(10, 0))

        # License Row (Đã chuyển thành thông báo vĩnh viễn)
        key_row = Frame(pad, bg=BG)
        key_row.pack(fill='x', pady=(8, 4))

        Label(key_row, text='Bản quyền:', fg=MUTED, bg=BG, font=('Segoe UI', 9)).pack(side='left', padx=(0, 6))

        self.lbl_key = Label(
            key_row,
            text='Bản quyền vĩnh viễn (Đã kích hoạt / Bypass)',
            fg='#4ade80',
            bg=BG,
            font=('Segoe UI', 9, 'bold')
        )
        self.lbl_key.pack(side='left', padx=(0, 12))

        # Setting Bar: Delay, Chống phá, Thoát khách
        bar = Frame(pad, bg=BG)
        bar.pack(fill='x', pady=(4, 10))

        Label(bar, text='Delay xả (s):', fg=MUTED, bg=BG, font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))
        self.delayvar = StringVar(value='1.0')
        self.ent_delay = Entry(
            bar,
            textvariable=self.delayvar,
            width=5,
            bg='#111827',
            fg='#e2e8f0',
            insertbackground='#e2e8f0',
            relief='flat',
            font=('Segoe UI', 9)
        )
        self.ent_delay.pack(side='left', padx=(0, 16), ipady=2)

        self.chong_on = False
        self.btn_chong = Button(
            bar,
            text='Chống phá: Off',
            command=self._toggle_chong,
            bg='#334155',
            fg='#e2e8f0',
            font=('Segoe UI', 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=2
        )
        self.btn_chong.pack(side='left', padx=(0, 10))

        self.out_on = False
        self.btn_out = Button(
            bar,
            text='Out khi gặp khách: Off',
            command=self._toggle_out,
            bg='#334155',
            fg='#e2e8f0',
            font=('Segoe UI', 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=2
        )
        self.btn_out.pack(side='left', padx=(0, 10))

        self.btn_pair = Button(
            bar,
            text='⚡ Ghép bàn (2 acc)',
            command=self._pair_selected,
            bg='#f0c040',
            fg='#111827',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=2
        )
        self.btn_pair.pack(side='left', padx=(0, 10))

        self.test_var = BooleanVar(value=False)
        self.chk_test = Checkbutton(
            bar,
            text='Test 1 ván (tự dừng)',
            variable=self.test_var,
            command=self._toggle_test,
            bg='#334155',
            fg='#e2e8f0',
            activebackground='#334155',
            activeforeground='#ffffff',
            selectcolor='#f0c040',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=6,
            pady=2
        )
        self.chk_test.pack(side='left', padx=(0, 10))

        # Table Grid
        table = Frame(pad, bg=CARD, highlightthickness=1, highlightbackground=LINE)
        table.pack(fill='both', expand=True)

        widths = (36, 120, 100, 220, 80, 90, 90, 75, 78)
        for i, w in enumerate(widths):
            table.grid_columnconfigure(i, minsize=w, weight=1 if i == 3 else 0)

        headers = ('#', 'Nhân vật', 'Số tiền', 'Trạng thái', 'Cược', '', '', '', 'Ghép')
        for i, title in enumerate(headers):
            Label(
                table,
                text=title,
                fg=MUTED,
                bg=CARD,
                font=('Segoe UI', 9, 'bold'),
                anchor='center' if i == 0 else ('e' if i == 2 else 'w')
            ).grid(row=0, column=i, sticky='nsew', padx=4, pady=6)

        self.table = table
        self.row_widgets = {}
        self.pair_order = []

        # Bắt đầu vòng lặp tick
        self.tick()

    def _toggle_chong(self):
        global chong_pha
        self.chong_on = not self.chong_on
        chong_pha = self.chong_on
        if self.chong_on:
            self.btn_chong.configure(text='Chống phá: On', bg='#16a34a', fg='#ecfdf5')
        else:
            self.btn_chong.configure(text='Chống phá: Off', bg='#334155', fg='#e2e8f0')

    def _toggle_out(self):
        global out_guest
        self.out_on = not self.out_on
        out_guest = self.out_on
        if self.out_on:
            self.btn_out.configure(text='Out khi gặp khách: On', bg='#16a34a', fg='#ecfdf5')
        else:
            self.btn_out.configure(text='Out khi gặp khách: Off', bg='#334155', fg='#e2e8f0')

    def _toggle_test(self):
        global test_one_round
        test_one_round = bool(self.test_var.get())

    def _bet(self, cid):
        row = self.row_widgets.get(cid)
        if not row:
            return 100
        return parse_bet(row['betvar'].get())

    def _on_tick(self, cid):
        row = self.row_widgets.get(cid)
        if not row:
            return
        try:
            on = row['checkvar'].get()
        except Exception:
            return
        if on:
            if cid not in self.pair_order:
                self.pair_order.append(cid)
        else:
            if cid in self.pair_order:
                self.pair_order.remove(cid)
        self._paint_row(cid, on)

    def _paint_row(self, cid, on):
        row = self.row_widgets.get(cid)
        if not row:
            return
        hl = '#1d4ed8' if on else row.get('bg', '#0f172a')
        for lbl in row['labels']:
            try:
                lbl.configure(bg=hl)
            except Exception:
                pass
        try:
            row['checkbox'].configure(bg=hl, activebackground=hl)
        except Exception:
            pass

    def _create(self, cid):
        set_action(cid, 'create', self._bet(cid))

    def _join(self, cid):
        set_action(cid, 'join', self._bet(cid))

    def _pair_selected(self):
        selected = [cid for cid in self.pair_order
                    if cid in self.row_widgets and self.row_widgets[cid]['checkvar'].get()]
        if len(selected) != 2:
            messagebox.showwarning('Ghép bàn', 'Hãy tick chọn ĐÚNG 2 tài khoản ở cột "Ghép".\nAcc tick TRƯỚC sẽ là acc TẠO bàn.')
            return
        creator, joiner = selected[0], selected[1]
        bet = self._bet(creator)
        jrow = self.row_widgets.get(joiner)
        if jrow:
            jrow['betvar'].set(bet_text(bet))
        set_pair(creator, joiner, bet, test=bool(self.test_var.get()))

    def _stop(self, cid):
        stop_action(cid)

    def _ensure_row(self, cid, index):
        if cid in self.row_widgets:
            return self.row_widgets[cid]

        bg = '#0f172a' if index % 2 == 0 else '#0b1220'
        row = index + 1

        labels = []
        fgs = ('#94a3b8', '#ffffff', '#4ade80', '#93c5fd')
        anchors = ('center', 'w', 'e', 'w')

        for col in range(4):
            lbl = Label(
                self.table,
                text='—',
                fg=fgs[col],
                bg=bg,
                font=('Segoe UI', 10, 'bold' if col in (1, 2) else 'normal'),
                anchor=anchors[col]
            )
            lbl.grid(row=row, column=col, sticky='nsew', padx=4, pady=3)
            labels.append(lbl)

        betvar = StringVar(value='100')
        combo = ttk.Combobox(
            self.table,
            textvariable=betvar,
            values=BET_LABELS,
            state='readonly',
            width=6,
            font=('Segoe UI', 9)
        )
        combo.grid(row=row, column=4, sticky='ew', padx=4, pady=3)

        btn_create = Button(
            self.table,
            text='Tạo phòng',
            command=lambda: self._create(cid),
            font=('Segoe UI', 8, 'bold'),
            bg='#f0c040',
            fg='#111827',
            relief='flat',
            cursor='hand2',
            padx=4,
            pady=2
        )
        btn_create.grid(row=row, column=5, sticky='ew', padx=3, pady=3)

        btn_join = Button(
            self.table,
            text='Tìm phòng',
            command=lambda: self._join(cid),
            font=('Segoe UI', 8, 'bold'),
            bg='#3b82f6',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=4,
            pady=2
        )
        btn_join.grid(row=row, column=6, sticky='ew', padx=3, pady=3)

        btn_stop = Button(
            self.table,
            text='Dừng',
            command=lambda: self._stop(cid),
            font=('Segoe UI', 8, 'bold'),
            bg='#ef4444',
            fg='#ffffff',
            relief='flat',
            cursor='hand2',
            padx=4,
            pady=2
        )
        btn_stop.grid(row=row, column=7, sticky='ew', padx=3, pady=3)

        checkvar = BooleanVar(value=False)
        chk = Checkbutton(
            self.table,
            text='Ghép',
            variable=checkvar,
            command=lambda cid=cid: self._on_tick(cid),
            bg=bg,
            fg='#e2e8f0',
            activebackground=bg,
            activeforeground='#ffffff',
            selectcolor='#f0c040',
            font=('Segoe UI', 9, 'bold'),
            highlightthickness=0,
            bd=0,
            cursor='hand2',
            anchor='center',
            padx=2,
            pady=2
        )
        chk.grid(row=row, column=8, sticky='nsew', padx=3, pady=3)

        res = {
            'bg': bg,
            'labels': labels,
            'betvar': betvar,
            'combo': combo,
            'btn_create': btn_create,
            'btn_join': btn_join,
            'btn_stop': btn_stop,
            'checkvar': checkvar,
            'checkbox': chk,
        }
        self.row_widgets[cid] = res
        return res

    def tick(self):
        # Update delay
        try:
            sec = parse_delay_sec(self.delayvar.get())
            global xa_delay_ms
            xa_delay_ms = int(sec * 1000)
        except Exception:
            pass

        client_list = list_clients()
        self.lbl_count.configure(text=f'{len(client_list)} kết nối')

        current_cids = set()
        for idx, c in enumerate(client_list):
            cid = c.get('id')
            current_cids.add(cid)
            row = self._ensure_row(cid, idx)

            name = c.get('name') or 'Chưa có tên'
            money_str = format_money(c.get('money'))
            phase_label = c.get('phase_label') or 'Đang chờ'

            row['labels'][0].configure(text=str(idx + 1))
            row['labels'][1].configure(text=name)
            row['labels'][2].configure(text=money_str)
            row['labels'][3].configure(text=phase_label)

            # Đổi màu trạng thái nếu đang săn hoặc xả
            if c.get('hunt'):
                row['labels'][3].configure(fg='#f0c040')
            elif 'thành công' in phase_label.lower():
                row['labels'][3].configure(fg='#4ade80')
            else:
                row['labels'][3].configure(fg='#93c5fd')

        # Xóa các dòng của client đã ngắt kết nối
        to_remove = [cid for cid in self.row_widgets if cid not in current_cids]
        for cid in to_remove:
            row = self.row_widgets.pop(cid)
            if cid in self.pair_order:
                self.pair_order.remove(cid)
            for lbl in row['labels']:
                lbl.destroy()
            row['combo'].destroy()
            row['btn_create'].destroy()
            row['btn_join'].destroy()
            row['btn_stop'].destroy()
            row['checkbox'].destroy()

        self.root.after(300, self.tick)


def main():
    reset_session_data()

    global http_server
    try:
        http_server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            'Sunwin Control',
            f'Không mở được: cổng {PORT} đang bị chiếm.\nĐóng Control cũ hoặc tắt tiến trình rồi mở lại.'
        )
        root.destroy()
        return

    # Chạy HTTP Server ngầm
    t = threading.Thread(target=http_server.serve_forever, daemon=True)
    t.start()

    # Chạy giao diện Tkinter
    root = Tk()
    app = App(root)

    def on_close():
        try:
            if http_server:
                http_server.shutdown()
        except Exception:
            pass
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
