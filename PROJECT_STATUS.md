# TLDT Sunwin — Trạng thái dự án (Đã làm / Chưa làm)

Repo: https://github.com/vzetiZero/sunwin_join

> Đã tinh gọn: chỉ giữ **lõi logic ghép/join bàn headless**. Đã xoá bản Tk cũ,
> các probe chẩn đoán không dùng, cùng nhánh `control/` + `extension_auto/` + `deobfuscated/`.

---

## Cấu trúc thư mục

| File | Mô tả |
|---|---|
| `install_deps.bat` | **Cài thư viện** (`websocket-client`, `msgpack`, `PySide6`). |
| `requirements.txt` | Danh sách thư viện cho `install_deps.bat`. |
| `pair_tool/sunwin_pair_tool_pyside.py` | **Tool chính (PySide6)** — ghép 2 acc vào bàn solo. |
| `pair_tool/run_tool.bat` | Chạy tool chính. |
| `pair_tool/accounts.json` | Danh sách acc + đường dẫn auth. |
| `headless/sunwin_headless.py` | CLI ghép 2 acc không cần trình duyệt. |
| `headless/capture_auth.py` | Bắt auth (info+signature) qua CDP. |
| `headless/run_pair.bat` | Chạy CLI ghép. |
| `headless/record_frames.py` | **Recorder CDP** — ghi mọi frame WebSocket, tìm gói join ngay. |
| `headless/run_record.bat` | Chạy recorder. |
| `probe_quickjoin.js` | Probe client đọc gid sảnh + source hàm quick-join. |

---

## ✅ ĐÃ LÀM

### 1. Reverse-engineer protocol (headless) — XONG
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

### 2. Tool `pair_tool/` — CHẠY ĐƯỢC
- **PySide6, nền trắng** (`sunwin_pair_tool_pyside.py`).
- Mở **Chrome ẩn danh** + remote-debug → vào trang đăng nhập → tự bắt auth → tự đóng Chrome.
- **➕ Thêm acc** + **Gia hạn auth** (mỗi acc 1 profile Chrome lưu phiên → tự đăng nhập lại, tự bắt auth mới).
- **Chế độ "Profile Chrome"** (dropdown) khi đăng nhập/bắt auth:
  - `Riêng (giữ lại)` — profile riêng từng acc, giữ để lần sau tự đăng nhập. **Không cần đóng Chrome chính.**
  - `Đồng bộ Chrome chính (xoá sau)` — copy cookie/localStorage từ Chrome **đang mở** (không cần đóng) ra bản tạm → login → **tự xoá**.
  - `Chrome thật (đóng Chrome)` — dùng đúng profile Chrome chính (phải đóng Chrome trước).
  - `Mới tạm (xoá sau)` — profile mới hoàn toàn → login → **tự xoá**.
  Tool chỉ đóng **instance Chrome nó tự mở** (qua CDP `Browser.close`), **không đụng Chrome chính** của bạn.
  (Không dùng ChromeDriver vì bật `navigator.webdriver` dễ bị phát hiện.)
- **Kiểm tra auth** trước khi ghép; **chọn tài khoản** (checkbox).
- **⚡ GHÉP BÀN SOLO**: acc1 tạo bàn **2 người, không pass** → acc2 vào; tự thử lại; tự LEAVE bàn cũ; lọc ack đúng rid; xác minh chặt.
- ✅ Đã kiểm chứng thật: 2 acc vào cùng bàn solo.

---

## 🔄 ĐANG LÀM — Sảnh Sâm/Lốc: tìm "method join bàn ngay lập tức"

Mục tiêu: quick-join **bàn trống có sẵn theo mức cược** (không tạo bàn) cho các acc được chọn,
áp dụng cho sảnh **Sâm Lốc** (và mọi sảnh khác). Hiện `pair_tool` chỉ hardcode `gid=1` (TLMN) và
**chưa biết** gid Sâm Lốc lẫn gói socket quick-play.

Công cụ bắt phương thức:
- `headless/record_frames.py` — recorder CDP ghi mọi frame ra/vào, giải mã msgpack, đánh dấu mốc
  (`Enter`) trước/sau khi bấm "Chơi nhanh" → in ra gói join + ứng viên `gid`.
- `probe_quickjoin.js` — đọc `TableListView.gameID` (= gid sảnh), liệt kê `TableItemView`
  (roomID/serverID/bet/số người) và **source hàm `onQuickPlayWithBet` / `onJoinRoom`**.

**Bước tiếp theo:** chờ dữ liệu bắt được → suy ra gói quick-join ở tầng socket → cài vào `pair_tool`.

---

## ❌ CHƯA LÀM (TODO)

- [ ] **Quick-join sảnh Sâm Lốc** (join bàn trống theo cược, không tạo bàn): đang bắt gói — xem mục "ĐANG LÀM".
- [ ] **Start ván**: sau khi 2 acc vào bàn solo → gửi READY cho cả 2 để bắt đầu.
- [ ] **Auto-xả (tự đánh) 2 người**: bắt frame `DEAL_CARDS` (250) đọc **bài mình**, áp logic TLMN → gửi `DANH_BAI`/`PASS` (251/253/254), lặp tới `FINISH_GAME` (252).
- [ ] **Gia hạn auth headless 100% bằng `refresh_token`** (không mở Chrome): cần bắt endpoint
      refresh/token (luồng OAuth/PKCE) 1 lần.

### Lệnh game đã biết (để làm auto-xả)
```
DemLa_Message : DEAL_CARDS=250, DANH_BAI=251, FINISH_GAME=252, SEND_DANH_BAI=253, PASS=254
Sam_Message   : DEAL_CARDS=700, DANH_BAI=703, BAO_SAM=704, SEND_DANH_BAI=705, PASS=706
```
Điều kiện: phải chờ `ps` đủ 2 người rồi mới READY (nếu không server báo
`cardgame.error.not_enough_player_to_start`).

---

## Cách chạy

### 1) Cài thư viện (1 lần)
```
install_deps.bat
```

### 2) Tool chính (headless, khuyến nghị)
```
pair_tool\run_tool.bat
```

### 3) CLI headless
```
python headless\capture_auth.py <PORT_debug> headless\auth_acc1.json
python headless\sunwin_headless.py headless\auth_acc1.json headless\auth_acc2.json 100 1 2
```

### 4) Bắt gói join ngay (khi cần tìm sảnh mới)
```
headless\run_record.bat
```

---

## Lưu ý
- Server game hay lỗi **522 (Cloudflare)** → đôi lúc phải chạy lại.
- Bàn **2 người mở** dễ bị khách chen; bàn **4 người** thì chắc ghế hơn (nhưng auto-xả cần 2 người).
- Game **không có lệnh bỏ/đổi mật khẩu** phòng → không dùng pass.
- **Dùng client ngoài trình duyệt có rủi ro ban tài khoản.**
- File `auth_*.json` và `frames_*.jsonl` chứa token → **không nên public** (đã có trong `.gitignore`).
