# TLDT Sunwin — Trạng thái dự án (Đã làm / Chưa làm)

Repo: https://github.com/vzetiZero/sunwin_join

---

## Cấu trúc thư mục

| Thư mục / file | Mô tả |
|---|---|
| `control/` | App Control (Python) + `TLDT_Sunwin.exe`. Giao tiếp với extension qua HTTP `127.0.0.1:17831`. |
| `extension_auto/` | Chrome extension hook game (bản có extension). |
| `headless/` | Script CLI: `capture_auth.py`, `sunwin_headless.py`. |
| `pair_tool/` | **Tool chính (PySide6, nền trắng)** — ghép 2 acc headless. |
| `deobfuscated/` | Source `inject.js`/`popup.js` đã giải mã + README. |
| `probe_*.js` | Script chẩn đoán chạy trong Console game. |

---

## ✅ ĐÃ LÀM

### 1. Giải mã & sửa lỗi nền
- Giải mã `extension_auto/inject.js` và `popup.js` (javascript-obfuscator: mảng base64 + xoay 25/9 vị trí) → `deobfuscated/`.
- Vá **deadlock `state_lock`** trong `control/control.py` → đổi `threading.Lock()` → `threading.RLock()`; test PASS.
- Build lại `control/TLDT_Sunwin.exe` (PyInstaller).

### 2. Extension
- Thêm domain `sunwin.villas` vào `manifest.json` (host_permissions + content_scripts).
- Thêm nút ghép 2 acc, check auth, tạo bàn trống (CreateTablePopup.taoBan), join chính xác, auto-xả (theo logic cũ).

### 3. Reverse-engineer protocol (headless) — XONG
| Việc | Gói / Endpoint |
|---|---|
| Socket lobby | `wss://ws-lby.azhkthg1.net/wsbinary?token=<JWT>` |
| Socket bàn | `wss://ws-card04.azhkthg1.net/wsbinary<sid>?token=<JWT>` |
| Auth | `[1,"Simms","","",{"info":"<json>","signature":"<256 hex>"}]` |
| **Tạo bàn** | `[6,"Simms","channelPlugin",{"cmd":308,"gid":1,"aid":1,"b":<bet>,"Mu":<số người>,"pwd":"","iJ":false}]` |
| **Vào bàn** | `[3,"Simms",<rid>,<pwd>]` |
| **Rời bàn** | `[4,"Simms",<rid>]` |
| **READY** | `[5,"Simms",<rid>,{"cmd":5}]` |
| Số bàn | `sid + rid` (vd sid=3, rid=14892 → `314892`) |

### 4. Tool `pair_tool/` — CHẠY ĐƯỢC
- **PySide6, nền trắng** (`sunwin_pair_tool_pyside.py`).
- **Bỏ GPM**: mở **Chrome ẩn danh** + remote-debug → vào trang đăng nhập → tự bắt auth → tự đóng Chrome.
- **➕ Thêm acc** (đăng nhập acc mới) và **Đăng nhập lại** (acc hết hạn).
- **Kiểm tra auth** trước khi ghép; **chọn tài khoản** (checkbox).
- **⚡ GHÉP BÀN SOLO**: acc1 tạo bàn **2 người, không pass** → acc2 vào; tự thử lại; tự LEAVE bàn cũ; lọc ack đúng rid; xác minh chặt.
- Log gọn: `[Tìm bàn] Server đang tìm...` → `✅ ĐÃ GHÉP 2 ACC VÀO BÀN SOLO <soBan>`.
- ✅ Đã kiểm chứng thật: 2 acc vào cùng bàn solo.

---

## ❌ CHƯA LÀM (TODO)

- [ ] **Start ván**: sau khi 2 acc vào bàn solo → gửi READY cho cả 2 để bắt đầu.
- [ ] **Auto-xả (tự đánh) 2 người**: bắt frame `DEAL_CARDS` (cmd 250) để đọc **bài mình**, áp logic TLMN → gửi `DANH_BAI`/`PASS` (251/253/254), lặp tới `FINISH_GAME` (252).
- [ ] **Gia hạn auth bằng `refreshToken`** (khỏi mở Chrome): cần bắt endpoint refresh `api.azhkthg1.com` 1 lần.
- [ ] Dọn file rác (`.bak*`, `__pycache__`, probe tạm).
- [ ] (Tùy chọn) Gộp bản Tk cũ (`sunwin_pair_tool.py`) vào bản PySide6.

### Lệnh game đã biết (để làm auto-xả)
```
DemLa_Message : DEAL_CARDS=250, DANH_BAI=251, FINISH_GAME=252, SEND_DANH_BAI=253, PASS=254
Sam_Message   : DEAL_CARDS=700, DANH_BAI=703, BAO_SAM=704, SEND_DANH_BAI=705, PASS=706
```
Điều kiện: phải chờ `ps` đủ 2 người rồi mới READY (nếu không server báo
`cardgame.error.not_enough_player_to_start`).

---

## Cách chạy

### Tool chính (headless, khuyến nghị)
```
pip install websocket-client msgpack PySide6
pair_tool\run_tool.bat
```

### CLI headless
```
python headless\capture_auth.py <PORT_debug> headless\auth_acc1.json
python headless\sunwin_headless.py headless\auth_acc1.json headless\auth_acc2.json 100 1 2
```

### Bản Control + Extension (cũ)
```
control\run_control.bat      (hoặc control\TLDT_Sunwin.exe)
```
Nạp extension `extension_auto/` vào Chrome, mở game, bấm Connect.

---

## Lưu ý
- Server game hay lỗi **522 (Cloudflare)** → đôi lúc phải chạy lại.
- Bàn **2 người mở** dễ bị khách chen; bàn **4 người** thì chắc ghế hơn (nhưng auto-xả cần 2 người).
- Game **không có lệnh bỏ/đổi mật khẩu** phòng → không dùng pass.
- **Dùng client ngoài trình duyệt có rủi ro ban tài khoản.**
- File `auth_*.json` chứa token → **không nên public**.
