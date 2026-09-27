/* ===== DEOBFUSCATED (string array + rotation removed) ===== */
const SUIT_GLYPH = ['♠', '♥', '♦', '♣'],
    RANK_FACE = {
        0x1: 'A',
        0xb: 'J',
        0xc: 'Q',
        0xd: 'K'
    };

function render(_0x29541e) {
    const _0x56d92c = null /* decoder removed */,
        _0x4f91f5 = document['getElementById']('played');
    if (!_0x29541e || !_0x29541e['length']) {
        _0x4f91f5['innerHTML'] = '<span class="empty">Chưa có</span>';
        return;
    }
    _0x4f91f5['innerHTML'] = _0x29541e['map'](function(_0x3d835a) {
        const _0x49288a = _0x56d92c,
            _0x33d8e5 = _0x3d835a['suit'] === 0x1 || _0x3d835a['suit'] === 0x2,
            _0x243eb5 = RANK_FACE[_0x3d835a['rank']] || String(_0x3d835a['rank']);
        return '<span class="card ' + (_0x33d8e5 ? 'r' : 'b') + '\x22>' + _0x243eb5 + (SUIT_GLYPH[_0x3d835a['suit']] || '') + '</span>';
    })['join']('');
}
async function poll() {
    const _0x4a0271 = null /* decoder removed */,
        [_0x578090] = await chrome['tabs']['query']({
            'active': !![],
            'currentWindow': !![]
        });
    if (!_0x578090 || !_0x578090['id']) return;
    try {
        const _0x18b99c = await chrome['tabs']['sendMessage'](_0x578090['id'], {
            'type': 'GET_STATE'
        });
        if (!_0x18b99c || !_0x18b99c['ok']) {
            document['getElementById']('remain')['textContent'] = 'Còn — lá', render([]);
            return;
        }
        document['getElementById']('remain')['textContent'] = 'Còn ' + (_0x18b99c['remain'] != null ? _0x18b99c['remain'] : '—') + '/13 lá', render(_0x18b99c['cards']);
    } catch (_0x40adce) {
        document['getElementById']('remain')['textContent'] = 'Còn — lá';
    }
}
poll(), setInterval(poll, 0x320);