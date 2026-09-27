# Deobfuscate toàn bộ dự án TLDT_Sunwin MH

Tài liệu này ghi lại cách giải mã các file bị obfuscate trong dự án và liệt kê
các file đã giải mã.

## 1. Hiện trạng từng file

| File | Trạng thái | Ghi chú |
|---|---|---|
| `control/control.py` | **Đã là plaintext** | Python, đọc trực tiếp được |
| `control/run_control.bat` | Plaintext | |
| `control/*.json` | Plaintext | cấu hình |
| `extension_auto/background.js` | **Đã là plaintext** | |
| `extension_auto/isolated.js` | **Đã là plaintext** | |
| `extension_auto/manifest.json` | Plaintext | |
| `extension_auto/inject.js` | **Bị obfuscate** | javascript-obfuscator: mảng string base64 + xoay + control-flow |
| `extension_auto/popup.js` | **Bị obfuscate** | cùng loại, chỉ các string literal bị che |
| `control/TLDT_Sunwin.exe` | **Không phải mã nguồn** | Bundle **PyInstaller** (onefile, Python 3.12) chứa `control.py` đã biên dịch |

## 2. Cách giải mã (tóm tắt)

Cả `inject.js` và `popup.js` dùng chung kỹ thuật của `javascript-obfuscator`:

1. **Mảng string** được mã hoá base64 bằng bảng chữ cái
   `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=`
   (khác base64 chuẩn).
2. **Hàm decoder** (`_0x4cf9` trong inject, `_0x286a` trong popup) giải mã theo
   chỉ số: `index = arg - OFFSET` (inject `0x1a2`, popup `0x1ea`).
3. **Vòng xoay mảng** (rotation IIFE) xoay `arr.push(arr.shift())` cho tới khi
   một biểu thức checksum bằng hằng số mục tiêu:
   - inject: `0x23ac9` → xoay **25** vị trí
   - popup:  `0x8683b` → xoay **9** vị trí
4. Thay mọi lời gọi `alias(0xNNN)` bằng **chuỗi đã giải mã** (alias được truy
   vết bắc cầu: `X=_0x4cf9`, `Y=X`, …).
5. Xoá phần boilerplate (mảng + decoder + rotation) ở đầu file.

Toàn bộ các bước trên được thực hiện bằng script Python (đã dùng, không kèm lại
trong thư mục này).

## 3. File đã giải mã trong thư mục này

- `inject.deobfuscated.js` — bản đầy đủ của `inject.js`, đã thay hết string +
  đổi tên 81 hàm và 49 biến toàn cục sang tên có nghĩa.
- `popup.deobfuscated.js` — bản đầy đủ của `popup.js`.
- `inject.strings.txt` — bảng 225 chuỗi đã giải mã (index → giá trị).
- `popup.strings.txt` — bảng 28 chuỗi đã giải mã.

> Lưu ý: các file `*.deobfuscated.js` **dùng để ĐỌC**, không chạy trực tiếp
> được vì đã lược bỏ mảng/decoder. Những dòng dạng
> `const _0x35ae04 = null /* decoder removed */;` chỉ còn là tàn dư alias, vô hại.

## 4. Bảng đổi tên chính (inject.js)

Các hàm:

| Tên gốc | Tên mới | Ý nghĩa |
|---|---|---|
| `_0x42e2e8` | `classNameOf` | lấy tên class component (qua `cc.js.getClassName`) |
| `_0x572281` | `componentsOf` | lấy components của node |
| `_0x482af1` | `walkTree` | duyệt đệ quy cây node |
| `_0x268a31` | `getScene` | `cc.director.getScene()` |
| `_0x10a5b3` | `readCard` | đọc 1 lá: `card.S/N` hoặc `spr_card.spriteFrame` |
| `_0x21abe8` | `findGameView` | tìm `TienLenFullScreenGameView` |
| `_0x553d54` | `myHandCards` | bài trên tay MÌNH |
| `_0x437685` | `oppRemainTotal` | tổng SỐ LÁ còn lại của đối thủ |
| `_0x4089f9` | `oppLastTurnCards` | lá vừa đánh ra (không tính bài mình) |
| `_0x1ba726` | `playerName` | tên người chơi |
| `_0x43514b` | `isTeammate` | tên có trong danh sách team |
| `_0x6e255f` | `hasGuest` | có đối thủ không thuộc team |
| `_0x4190fe` | `hookTable` | hook `prepareNewGame` / `finishPhatBai` / `danhBai` |
| `_0x25a8f7` | `recordCard` | ghi 1 lá vào danh sách đã đánh |
| `_0x3d2698` | `renderOppHud` | vẽ HUD "Đối thủ – còn X/13" |
| `_0x89116e` | `buildPlayerState` | dựng state nhân vật gửi về Control |
| `_0x3781c8` | `postStateToIsolated` | `postMessage` STATE sang isolated.js |
| `_0x34c7e9` | `quickPlayByBet` | vào bàn nhanh theo mức cược |
| `_0x4891fe` | `joinExactRoom` | vào bàn CHÍNH XÁC theo `roomId/serverId` |
| `_0x19a8da` | `parseSoBan` | tách `soBan` → `serverId` + `roomId` |
| `_0x27c15c` | `onFoundRoom` | báo tìm được bàn (`HUNT_FOUND`) |
| `_0x378e65` | `joinHuntTick` | vòng lặp join bàn |
| `_0x2a655a` | `mainTick` | vòng lặp trạng thái bàn |
| `_0x30be95` | `stateTick` | cập nhật state + HUD + gửi isolated |

Các biến toàn cục:

| Tên gốc | Tên mới |
|---|---|
| `_0x5bb433` | `armed` |
| `_0x316a2f` | `hunting` |
| `_0x282e8a` | `huntMode` (`'join'`/`'create'`) |
| `_0x304bb0` | `sharedRoom` |
| `_0x12cf53` | `bet` |
| `_0x68b2f2` | `huntState` (`idle`/`checking`/`joining`/`leaving`/`found`) |
| `_0x4d657d` | `tablePhase` |
| `_0x51d999` | `recordedCards` |
| `_0x30660f` | `knownCardKeys` |
| `_0x2d40c7` | `teamNames` |
| `_0x17aa5f` | `xaDelay` |
| `_0x222f63` | `chongPha` |
| `_0x1d4439` | `outGuest` |
| `_0x5e0ad4` | `halted` |
| `_0x11974b` | `playerState` |

(danh sách đầy đủ nằm trong mã nguồn; xem thêm `inject.strings.txt`.)

## 5. Về `control/TLDT_Sunwin.exe`

`TLDT_Sunwin.exe` là **PyInstaller onefile** (Python 3.12, có `_internal`,
`PYZ.pyz`, `python312.dll`). Nó không chứa mã nguồn dạng đọc được; muốn lấy lại
`control.py` phải trích PYZ rồi decompile bytecode 3.12 (khó/không cần thiết) —
mà bản `control.py` gốc đã có sẵn trong dự án nên không cần làm lại.
