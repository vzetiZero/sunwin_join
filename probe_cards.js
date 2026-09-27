/* ============================================================================
 * Sunwin TLMN - Runtime Card Access Probe  (chỉ để CHẨN ĐOÁN, không tấn công)
 * ----------------------------------------------------------------------------
 * Mục đích: kiểm chứng client có đang chứa DANH TÍNH (lá gì) bài trên tay
 *           của đối thủ hay không.
 *
 * Cách dùng:
 *   1. Mở tab game TLMN Sunwin, vào một bàn đang chơi (đã chia bài).
 *   2. F12 -> tab Console -> chọn context "top" (main world, KHÔNG phải
 *      extension context) -> dán toàn bộ file này rồi Enter.
 *   3. Đọc report in ra. Biến `window.__sunProbe` giữ kết quả để soi lại.
 *
 * Cách đọc nhanh:
 *   - findings.verdict.opponentsExposeIdentity = true  -> client CÓ lộ bài đối thủ
 *   - findings.verdict.opponentsExposeIdentity = false -> client KHÔNG chứa bài đối thủ
 *   - So sánh findings.mine.cardSamples vs findings.opponents[x].cardSamples
 * ==========================================================================*/
(function () {
    'use strict';

    var R = { ts: new Date().toISOString(), findings: {}, errors: [] };

    function safe(label, fn) {
        try { return fn(); }
        catch (e) { R.errors.push(label + ': ' + (e && e.message ? e.message : String(e))); return undefined; }
    }

    var cc = window.cc;

    /* ---------- 1. cardHook mà extension đã cài ---------- */
    R.findings.cardHookPresent = !!(window.cardHook && typeof window.cardHook === 'object');
    if (R.findings.cardHookPresent) {
        R.findings.cardHookKeys = Object.keys(window.cardHook);
        R.findings.hand = safe('cardHook.hand', function () { return window.cardHook.hand && window.cardHook.hand(); });
        R.findings.tableNow = safe('cardHook.tableNow', function () { return window.cardHook.tableNow && window.cardHook.tableNow(); });
        R.findings.played = safe('cardHook.played', function () { return window.cardHook.played && window.cardHook.played(); });
    }

    /* ---------- 2. duyệt cây scene ---------- */
    R.findings.hasCC = !!(cc && cc.director);
    var scene = safe('getScene', function () { return cc.director.getScene(); });
    R.findings.sceneName = scene && scene.name;

    var visited = new Set();
    var components = [];
    var cardNodes = [];

    function compName(c) {
        try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {}
        try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; }
    }

    function cardBrief(item) {
        if (!item) return null;
        try {
            var c = (typeof item.getCard === 'function') ? item.getCard() : item.card;
            if (c) return { S: c.S, N: c.N, serverCode: c.serverCode };
        } catch (e) {}
        try {
            var sf = item.spr_card && item.spr_card.spriteFrame;
            if (sf) return { sprite: sf.name || sf._name };
        } catch (e) {}
        return null;
    }

    function walk(node, depth) {
        if (!node || depth > 40 || visited.has(node)) return;
        visited.add(node);
        var comps = [];
        try {
            if (typeof node.getComponents === 'function') {
                comps = node.getComponents(cc && cc.Component ? cc.Component : undefined) || [];
            } else {
                comps = node.components || [];
            }
        } catch (e) {}
        for (var i = 0; i < comps.length; i++) {
            var c = comps[i];
            if (!c) continue;
            components.push(c);
            var cn = compName(c);
            if (cn === 'CardItem' || c.spr_card || ('card' in c) || ('isSelected' in c)) {
                cardNodes.push({ node: node, comp: c, cn: cn });
            }
        }
        var kids = node.children || [];
        for (var k = 0; k < kids.length; k++) walk(kids[k], depth + 1);
    }
    safe('walk', function () { walk(scene, 0); });
    R.findings.nodeCount = visited.size;
    R.findings.componentCount = components.length;

    /* ---------- 3. tìm view bàn chơi ---------- */
    var gameView = null;
    for (var i = 0; i < components.length; i++) {
        if (compName(components[i]) === 'TienLenFullScreenGameView') { gameView = components[i]; break; }
    }
    if (!gameView) {
        for (var j = 0; j < components.length; j++) {
            if (components[j].btn_danhbai && components[j].my_info) { gameView = components[j]; break; }
        }
    }
    R.findings.gameViewFound = !!gameView;

    function describePlayer(tag, info) {
        var out = { tag: tag };
        if (!info) { out.present = false; return out; }
        out.present = true;
        out.isEmpty = safe(tag + '.isEmpty', function () {
            return typeof info.isEmpty === 'function' ? info.isEmpty() : undefined;
        });
        out.keys = safe(tag + '.keys', function () { return Object.keys(info); });
        out.name = safe(tag + '.getName', function () {
            return typeof info.getName === 'function' ? info.getName() : undefined;
        });
        out.remaining = safe(tag + '.getRemainingCard', function () {
            return typeof info.getRemainingCard === 'function' ? info.getRemainingCard() : undefined;
        });
        var cards = safe(tag + '.getPlayerCard', function () {
            return typeof info.getPlayerCard === 'function' ? info.getPlayerCard() : undefined;
        });
        out.getPlayerCardType = Array.isArray(cards) ? ('array[' + cards.length + ']') : typeof cards;
        if (Array.isArray(cards)) {
            out.cardSamples = cards.slice(0, 20).map(cardBrief);
            out.cardsHaveIdentity = out.cardSamples.some(function (s) {
                return s && (s.S != null || s.N != null || s.sprite);
            });
        }
        if (info.cards) {
            out.cardsPropType = Array.isArray(info.cards) ? ('array[' + info.cards.length + ']') : typeof info.cards;
            if (Array.isArray(info.cards)) {
                out.cardsPropSamples = info.cards.slice(0, 20).map(cardBrief);
                out.cardsPropHasIdentity = out.cardsPropSamples.some(function (s) {
                    return s && (s.S != null || s.N != null || s.sprite);
                });
            }
        }
        return out;
    }

    if (gameView) {
        R.findings.gameViewType = compName(gameView);
        R.findings.myInfoKeys = gameView.my_info ? safe('my_info.keys', function () { return Object.keys(gameView.my_info); }) : null;
        R.findings.opponentInfoLen = Array.isArray(gameView.opponent_info)
            ? gameView.opponent_info.length
            : (gameView.opponent_info ? 1 : 0);
        R.findings.lastTurnCards = safe('_lastTurnCards', function () {
            return (gameView._lastTurnCards || []).map(cardBrief);
        });

        R.findings.mine = describePlayer('me', gameView.my_info);

        R.findings.opponents = [];
        var opps = gameView.opponent_info || [];
        for (var o = 0; o < opps.length; o++) {
            R.findings.opponents.push(describePlayer('opp' + o, opps[o]));
        }
    }

    /* ---------- 4. mọi node bài trong scene ---------- */
    R.findings.cardNodeCount = cardNodes.length;
    R.findings.cardNodeSamples = cardNodes.slice(0, 40).map(function (cn) {
        return {
            cls: cn.cn,
            node: cn.node && cn.node.name,
            brief: cardBrief(cn.comp)
        };
    });

    /* ---------- 5. kết luận ---------- */
    var oppList = R.findings.opponents || [];
    R.findings.verdict = {
        opponentsExposeIdentity: oppList.some(function (x) {
            return x.cardsHaveIdentity || x.cardsPropHasIdentity;
        }),
        mineHasIdentity: !!(R.findings.mine && R.findings.mine.cardsHaveIdentity),
        note: 'opponentsExposeIdentity=false => client không chứa danh tính bài trên tay đối thủ.'
    };

    console.group('%c[SUN] Runtime card probe', 'color:#f0c040;font-weight:bold');
    console.log(JSON.stringify(R.findings, null, 2));
    console.groupEnd();

    window.__sunProbe = R;
    return R;
})();
