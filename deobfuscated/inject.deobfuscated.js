/* ===== DEOBFUSCATED (string array + rotation removed) ===== */
(function() {
'use strict';
const _0x35ae04 = null /* decoder removed */;
if (window['__cardHookInstalled']) return;
window['__cardHookInstalled'] = !![];
const SUITS_HTML = ['♠', '♥', '♦', '♣'],
    RANK_LABEL = {
        0x1: 'A',
        0xb: 'J',
        0xc: 'Q',
        0xd: 'K'
    },
    SUITS_TXT = ['♠', '♥', '♦', '♣'],
    SUIT_CODE = {
        'B': 0x0,
        'C': 0x1,
        'R': 0x2,
        'T': 0x3
    },
    recordedCards = [],
    knownCardKeys = new Set();
let lastHudHtml = '',
    cachedGameView = null,
    cachedTopHeader = null,
    prevHandLen = 0x0,
    wasPlaying = ![],
    wasEnded = ![],
    prevHandSig = '',
    prevOppRemain = -0x1,
    lastHookedTable = null,
    armed = ![],
    playerState = {
        'name': '',
        'money': null,
        'phase': 'lobby',
        'phaseLabel': 'Đang ở sảnh'
    },
    bet = 0x64,
    hunting = ![],
    huntState = 'idle',
    huntTimer = 0x0,
    joinTimer = 0x0,
    sharedRoom = null,
    statusText = '',
    lastBrokenLabel = '',
    huntMode = '',
    tablePhase = 'idle',
    foundAt = 0x0,
    seatedAt = 0x0,
    xaStartAt = 0x0,
    passFlag = ![],
    teamNames = [],
    lastAutoPlayAt = 0x0,
    autoPlaySince = 0x0,
    xaDelay = 0x3e8,
    halted = ![],
    chongPha = ![],
    outGuest = ![],
    playedFirst = ![],
    tableBroken = ![],
    sawPlaying = ![],
    vsGuest = ![],
    autoPlayedVsGuest = ![],
    xaDecision = null,
    guestSeen = ![],
    guestReady = ![],
    leaveTimer = 0x0,
    brokenRetry = 0x0,
    exactJoinTries = 0x0;

function rankName(_0x5be424) {
    return RANK_LABEL[_0x5be424] || String(_0x5be424);
}

function cardKey(_0x3ef1e8, _0x49f52b) {
    return _0x3ef1e8 + '-' + _0x49f52b;
}

function classNameOf(_0x8799ff) {
    const _0x208ae5 = _0x35ae04;
    if (!_0x8799ff) return '';
    try {
        if (typeof cc !== 'undefined' && cc['js'] && cc['js']['getClassName']) {
            const _0x14d38d = cc['js']['getClassName'](_0x8799ff);
            if (_0x14d38d) return _0x14d38d;
        }
    } catch (_0x4847a9) {}
    return _0x8799ff['constructor'] && _0x8799ff['constructor']['name'] || '';
}

function childNodes(_0xcdcb38) {
    const _0x13cf55 = _0x35ae04;
    if (!_0xcdcb38) return [];
    const _0x200943 = _0xcdcb38['children'];
    if (!_0x200943 || !_0x200943['length']) return [];
    const _0xa84d1d = [];
    for (let _0x237c1a = 0x0; _0x237c1a < _0x200943['length']; _0x237c1a++)
        if (_0x200943[_0x237c1a]) _0xa84d1d['push'](_0x200943[_0x237c1a]);
    return _0xa84d1d;
}

function componentsOf(_0xd0370b) {
    const _0x50bf14 = _0x35ae04;
    if (!_0xd0370b) return [];
    if (typeof _0xd0370b['getComponents'] === 'function') try {
        const _0x2ef130 = _0xd0370b['getComponents'](typeof cc !== 'undefined' && cc['Component'] ? cc['Component'] : undefined);
        if (_0x2ef130 && _0x2ef130['length']) return _0x2ef130;
    } catch (_0xb6d59f) {}
    const _0x14b065 = _0xd0370b['components'];
    if (!_0x14b065 || !_0x14b065['length']) return [];
    const _0x2ee71f = [];
    for (let _0x53df0a = 0x0; _0x53df0a < _0x14b065['length']; _0x53df0a++)
        if (_0x14b065[_0x53df0a]) _0x2ee71f['push'](_0x14b065[_0x53df0a]);
    return _0x2ee71f;
}

function walkTree(_0x49a520, _0x1e13be, _0x5452de) {
    const _0x588289 = _0x35ae04;
    if (!_0x49a520 || _0x5452de > 0x32) return;
    _0x1e13be(_0x49a520);
    const _0x25ed30 = childNodes(_0x49a520);
    for (let _0x4d1da3 = 0x0; _0x4d1da3 < _0x25ed30['length']; _0x4d1da3++) walkTree(_0x25ed30[_0x4d1da3], _0x1e13be, _0x5452de + 0x1);
}

function getScene() {
    const _0x4bc1d5 = _0x35ae04;
    try {
        if (typeof cc !== 'undefined' && cc['director'] && cc['director']['getScene']) return cc['director']['getScene']();
    } catch (_0x379100) {}
    return null;
}

function mapSuit(_0x188100) {
    if (_0x188100 === 0x1) return 0x0;
    if (_0x188100 === 0x4) return 0x1;
    if (_0x188100 === 0x3) return 0x2;
    if (_0x188100 === 0x2) return 0x3;
    return null;
}

function mapRank(_0x57ff54) {
    _0x57ff54 = +_0x57ff54;
    if (_0x57ff54 === 0xe) return 0x1;
    if (_0x57ff54 === 0xf) return 0x2;
    if (_0x57ff54 >= 0x1 && _0x57ff54 <= 0xd) return _0x57ff54;
    return null;
}

function decodeSpriteCard(_0x249f12) {
    if (!_0x249f12) return null;
    const _0x101b33 = String(_0x249f12)['match'](/Card_(\d{1,2})([BCRT])/i);
    if (!_0x101b33) return null;
    const _0x33224b = mapRank(+_0x101b33[0x1]),
        _0x591458 = SUIT_CODE[_0x101b33[0x2]['toUpperCase']()];
    if (_0x33224b == null || _0x591458 == null) return null;
    return {
        'suit': _0x591458,
        'rank': _0x33224b
    };
}

function spriteNameOf(_0x44526f) {
    const _0xa89ee9 = _0x35ae04;
    try {
        const _0x121852 = _0x44526f['spr_card'],
            _0x1ae10c = _0x121852 && _0x121852['spriteFrame'];
        return _0x1ae10c && (_0x1ae10c['name'] || _0x1ae10c['_name']) || '';
    } catch (_0x2d8aec) {
        return '';
    }
}

function readCard(_0x48b8e7) {
    const _0x151b55 = _0x35ae04;
    if (!_0x48b8e7) return null;
    let _0x3b47c8 = null;
    try {
        _0x3b47c8 = typeof _0x48b8e7['getCard'] === 'function' ? _0x48b8e7['getCard']() : _0x48b8e7['card'];
    } catch (_0x5bc5f5) {
        _0x3b47c8 = _0x48b8e7['card'];
    }
    if (_0x3b47c8 && _0x3b47c8['N'] != null) {
        const _0x579287 = mapSuit(_0x3b47c8['S']),
            _0x5e77ee = mapRank(_0x3b47c8['N']);
        if (_0x579287 != null && _0x5e77ee != null) return {
            'suit': _0x579287,
            'rank': _0x5e77ee,
            'serverCode': _0x3b47c8['serverCode'],
            'rawS': _0x3b47c8['S'],
            'item': _0x48b8e7,
            'name': rankName(_0x5e77ee) + SUITS_HTML[_0x579287]
        };
    }
    const _0x508620 = decodeSpriteCard(spriteNameOf(_0x48b8e7));
    if (_0x508620) return {
        'suit': _0x508620['suit'],
        'rank': _0x508620['rank'],
        'serverCode': _0x3b47c8 && _0x3b47c8['serverCode'],
        'item': _0x48b8e7,
        'name': rankName(_0x508620['rank']) + SUITS_HTML[_0x508620['suit']]
    };
    return null;
}

function findGameView() {
    const _0x532f0c = _0x35ae04;
    if (cachedGameView && cachedGameView['node'] && cachedGameView['node']['isValid'] !== ![]) try {
        if (classNameOf(cachedGameView) === 'TienLenFullScreenGameView' || cachedGameView['btn_danhbai']) return cachedGameView;
    } catch (_0xbdeffc) {}
    cachedGameView = null;
    const _0x32b318 = getScene();
    if (!_0x32b318) return null;
    return walkTree(_0x32b318, function(_0x3c00b8) {
        const _0x463004 = _0x532f0c;
        if (cachedGameView) return;
        const _0xc49019 = componentsOf(_0x3c00b8);
        for (let _0x40bcb8 = 0x0; _0x40bcb8 < _0xc49019['length']; _0x40bcb8++) {
            const _0x32c496 = classNameOf(_0xc49019[_0x40bcb8]);
            if (_0x32c496 === 'TienLenFullScreenGameView' || _0xc49019[_0x40bcb8]['btn_danhbai'] && _0xc49019[_0x40bcb8]['cardPooling'] && _0xc49019[_0x40bcb8]['my_info']) {
                cachedGameView = _0xc49019[_0x40bcb8];
                return;
            }
        }
    }, 0x0), cachedGameView;
}

function dedupeCards(_0x2b4e4c) {
    const _0x43ec6a = _0x35ae04,
        _0x4ff7d5 = {},
        _0x56ce40 = [];
    for (let _0x1d02f7 = 0x0; _0x1d02f7 < _0x2b4e4c['length']; _0x1d02f7++) {
        const _0x548380 = readCard(_0x2b4e4c[_0x1d02f7]);
        if (!_0x548380) continue;
        const _0x314916 = cardKey(_0x548380['suit'], _0x548380['rank']);
        if (_0x4ff7d5[_0x314916]) continue;
        _0x4ff7d5[_0x314916] = 0x1, _0x56ce40['push'](_0x548380);
    }
    return _0x56ce40;
}

function myHandCards() {
    const _0x15efdb = _0x35ae04,
        _0x5e1a70 = findGameView();
    if (!_0x5e1a70 || !_0x5e1a70['my_info']) return [];
    let _0x542b3f = [];
    try {
        if (typeof _0x5e1a70['my_info']['getPlayerCard'] === 'function') _0x542b3f = _0x5e1a70['my_info']['getPlayerCard']() || [];
    } catch (_0x3207bc) {}
    return dedupeCards(_0x542b3f);
}

function oppRemainTotal(_0x305442) {
    const _0x502ac5 = _0x35ae04,
        _0x148995 = _0x305442 && _0x305442['opponent_info'];
    if (!_0x148995) return -0x1;
    const _0x9ac7cd = _0x148995['length'] || 0x0;
    let _0xa4504b = 0x0,
        _0x1349ed = ![];
    for (let _0x11caec = 0x0; _0x11caec < _0x9ac7cd; _0x11caec++) {
        const _0x583ebd = _0x148995[_0x11caec];
        if (!_0x583ebd) continue;
        try {
            if (typeof _0x583ebd['isEmpty'] === 'function' && _0x583ebd['isEmpty']()) continue;
        } catch (_0x48c820) {}
        let _0x5c761e = -0x1;
        try {
            const _0x539505 = typeof _0x583ebd['getPlayerCard'] === 'function' ? _0x583ebd['getPlayerCard']() : _0x583ebd['cards'];
            if (_0x539505 && _0x539505['length'] >= 0x0) _0x5c761e = _0x539505['length'];
        } catch (_0x17f34a) {}
        if (!(_0x5c761e >= 0x0)) try {
            if (typeof _0x583ebd['getRemainingCard'] === 'function') _0x5c761e = +_0x583ebd['getRemainingCard']();
        } catch (_0x4daf6b) {}
        if (!(_0x5c761e >= 0x0)) continue;
        _0x1349ed = !![], _0xa4504b += _0x5c761e;
    }
    return _0x1349ed ? _0xa4504b : -0x1;
}

function collectCardItems(_0x3b3846) {
    const _0x1c566f = [];
    if (!_0x3b3846) return _0x1c566f;
    return walkTree(_0x3b3846, function(_0x3ae58f) {
        const _0x2eab14 = null /* decoder removed */,
            _0xb8a9ad = componentsOf(_0x3ae58f);
        for (let _0x4577e1 = 0x0; _0x4577e1 < _0xb8a9ad['length']; _0x4577e1++) {
            const _0x586c40 = _0xb8a9ad[_0x4577e1];
            if (classNameOf(_0x586c40) === 'CardItem' || _0x586c40['spr_card'] && ('isSelected' in _0x586c40 || 'card' in _0x586c40)) _0x1c566f['push'](_0x586c40);
        }
    }, 0x0), _0x1c566f;
}

function oppLastTurnCards(_0x30e9fe, _0x4ea1d3) {
    const _0x3b7666 = _0x35ae04,
        _0x202d63 = _0x30e9fe['_lastTurnCards'] || [],
        _0xcb16b2 = {},
        _0x1be071 = [];
    for (let _0x148119 = 0x0; _0x148119 < _0x202d63['length']; _0x148119++) {
        const _0xf819ce = readCard(_0x202d63[_0x148119]);
        if (!_0xf819ce) continue;
        const _0x172a7c = cardKey(_0xf819ce['suit'], _0xf819ce['rank']);
        if (_0x4ea1d3['has'](_0x172a7c) || _0xcb16b2[_0x172a7c]) continue;
        _0xcb16b2[_0x172a7c] = 0x1, _0x1be071['push'](_0xf819ce);
    }
    return _0x1be071;
}

function handSignature(_0x8d06fa) {
    const _0x547154 = _0x35ae04;
    return _0x8d06fa['map'](function(_0x1d283c) {
        const _0x82ce6e = null /* decoder removed */;
        return cardKey(_0x1d283c['suit'], _0x1d283c['rank']);
    })['sort']()['join'](',');
}

function overlapCount(_0x23d330, _0x552d47) {
    const _0x5d65c1 = _0x35ae04;
    if (!_0x23d330 || !_0x552d47) return 0x0;
    const _0x37235a = {};
    _0x552d47['split'](',')['forEach'](function(_0x44528a) {
        if (_0x44528a) _0x37235a[_0x44528a] = 0x1;
    });
    let _0x1fff60 = 0x0;
    return _0x23d330['split'](',')['forEach'](function(_0x28481c) {
        if (_0x28481c && _0x37235a[_0x28481c]) _0x1fff60++;
    }), _0x1fff60;
}

function hookTable(_0x1074de) {
    const _0x185c66 = _0x35ae04;
    if (!_0x1074de || _0x1074de === lastHookedTable || _0x1074de['__hcRoundHooked']) return;
    _0x1074de['__hcRoundHooked'] = !![], lastHookedTable = _0x1074de, ['prepareNewGame', 'finishPhatBai']['forEach'](function(_0x2160eb) {
        if (typeof _0x1074de[_0x2160eb] !== 'function') return;
        const _0x46299f = _0x1074de[_0x2160eb];
        _0x1074de[_0x2160eb] = function() {
            const _0x27fad5 = null /* decoder removed */;
            return resetRound(_0x2160eb), _0x46299f['apply'](this, arguments);
        };
    });
    if (typeof _0x1074de['danhBai'] === 'function' && !_0x1074de['__hcDanhBaiHooked']) {
        _0x1074de['__hcDanhBaiHooked'] = !![];
        const _0x3f4e7b = _0x1074de['danhBai'];
        _0x1074de['danhBai'] = function(_0x2ef146) {
            const _0x41707c = _0x185c66,
                _0x19d7a5 = typeof this['isMe'] === 'function' && this['isMe'](_0x2ef146),
                _0x2a92da = _0x3f4e7b['apply'](this, arguments);
            if (!armed || _0x19d7a5) return _0x2a92da;
            const _0x25de78 = this['_lastTurnCards'] || [];
            for (let _0x162524 = 0x0; _0x162524 < _0x25de78['length']; _0x162524++) {
                const _0x27a131 = readCard(_0x25de78[_0x162524]);
                if (_0x27a131) recordCard(_0x27a131['suit'], _0x27a131['rank'], {
                    'zone': 'played',
                    'source': 'opp-danhBai',
                    'player': _0x2ef146
                });
            }
            return _0x2a92da;
        };
    }
}

function recordCard(_0x9c32c1, _0x407d1f, _0x2ea04b) {
    const _0x35f0b4 = _0x35ae04;
    _0x9c32c1 = +_0x9c32c1, _0x407d1f = +_0x407d1f;
    if (_0x9c32c1 < 0x0 || _0x9c32c1 > 0x3 || _0x407d1f < 0x1 || _0x407d1f > 0xd) return null;
    const _0x29b4c7 = _0x2ea04b && _0x2ea04b['zone'] || 'played',
        _0x4d06be = recordedCards['find'](function(_0x497ecb) {
            const _0x499af2 = _0x35f0b4;
            return _0x497ecb['suit'] === _0x9c32c1 && _0x497ecb['rank'] === _0x407d1f && _0x497ecb['zone'] === _0x29b4c7;
        });
    if (_0x4d06be) return _0x4d06be;
    const _0x586407 = {
        'suit': _0x9c32c1,
        'rank': _0x407d1f,
        'name': rankName(_0x407d1f) + SUITS_HTML[_0x9c32c1],
        'player': _0x2ea04b && _0x2ea04b['player'] != null ? _0x2ea04b['player'] : -0x1,
        'zone': _0x29b4c7,
        'source': _0x2ea04b && _0x2ea04b['source'] || 'sunwin',
        'ts': Date['now']()
    };
    return recordedCards['push'](_0x586407), _0x586407;
}

function resetRound(_0x27e837) {
    const _0x1c9926 = _0x35ae04;
    recordedCards['length'] = 0x0, knownCardKeys['clear'](), lastHudHtml = '', prevHandSig = '', prevOppRemain = -0x1, console['log']('[SUN]\x20reset\x20ván\x20mới\x20·\x20' + _0x27e837);
}

function injectHudStyle() {
    const _0x335f35 = _0x35ae04;
    let _0x45442e = document['getElementById']('hc-opp-hud-style');
    !_0x45442e && (_0x45442e = document['createElement']('style'), _0x45442e['id'] = 'hc-opp-hud-style', (document['head'] || document['documentElement'])['appendChild'](_0x45442e));
    if (_0x45442e['dataset']['hc'] === 'sw5') return;
    _0x45442e['dataset']['hc'] = 'sw5', _0x45442e['textContent'] = ['#hc-opp-hud{all:initial;position:fixed!important;top:clamp(6px,1vw,14px)!important;right:clamp(6px,1vw,14px)!important;left:auto!important;bottom:auto!important;', 'z-index:2147483647!important;pointer-events:none!important;box-sizing:border-box!important;width:auto!important;', '--hc-w:clamp(22px,3.4vw,44px)!important;--hc-h:clamp(30px,4.6vw,60px)!important;--hc-g:clamp(3px,.45vw,7px)!important;', 'padding:clamp(5px,.7vw,10px)!important;background:rgba(11,18,32,.94)!important;color:#fff!important;', 'border:1px\x20solid\x20#f0c040!important;border-radius:clamp(5px,.6vw,10px)!important;font-family:Segoe\x20UI,sans-serif!important;}', '#hc-opp-hud *{all:unset;box-sizing:border-box!important;}', '#hc-opp-hud .hc-title{display:block!important;color:#f0c040!important;font-weight:700!important;', 'font-size:clamp(10px,1.5vw,16px)!important;margin-bottom:clamp(3px,.5vw,8px)!important;}', '#hc-opp-hud .hc-cards{display:grid!important;grid-template-columns:repeat(5,var(--hc-w))!important;gap:var(--hc-g)!important;}', '#hc-opp-hud .hc-card{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;', 'width:var(--hc-w)!important;height:var(--hc-h)!important;background:#f8fafc!important;border-radius:clamp(3px,.4vw,6px)!important;font-weight:800!important;}', '#hc-opp-hud\x20.hc-card\x20b{font-size:clamp(10px,1.5vw,18px)!important;}', '#hc-opp-hud .hc-card i{font-size:clamp(9px,1.3vw,15px)!important;font-style:normal!important;}', '#hc-opp-hud .hc-card.red,#hc-opp-hud .hc-card.red b,#hc-opp-hud .hc-card.red i{color:#dc2626!important;}', '#hc-opp-hud .hc-card.black,#hc-opp-hud .hc-card.black b,#hc-opp-hud .hc-card.black i{color:#0f172a!important;}']['join']('');
}

function cardHtml(_0x3eb9ba) {
    const _0x28c8dc = _0x35ae04,
        _0xe83664 = _0x3eb9ba['suit'] === 0x1 || _0x3eb9ba['suit'] === 0x2,
        _0xe08acf = RANK_LABEL[_0x3eb9ba['rank']] || String(_0x3eb9ba['rank']);
    return '<span class="hc-card ' + (_0xe83664 ? 'red' : 'black') + '"><b>' + _0xe08acf + '</b><i>' + SUITS_TXT[_0x3eb9ba['suit']] + '</i></span>';
}

function renderOppHud(_0x173494, _0x51fe33, _0x514380) {
    const _0x46b7d3 = _0x35ae04;
    injectHudStyle();
    let _0xf58990 = document['getElementById']('hc-opp-hud');
    !_0xf58990 && (_0xf58990 = document['createElement']('div'), _0xf58990['id'] = 'hc-opp-hud', (document['documentElement'] || document['body'])['appendChild'](_0xf58990));
    const _0x3afac8 = _0x51fe33 != null ? _0x51fe33 : Math['max'](0x0, 0xd - _0x173494['length']),
        _0x19ab79 = '<div class="hc-title">Đối thủ - còn ' + _0x3afac8 + '/13</div>' + '<div class="hc-cards">' + _0x173494['map'](cardHtml)['join']('') + '</div>';
    if (_0x19ab79 === lastHudHtml) return;
    lastHudHtml = _0x19ab79, _0xf58990['innerHTML'] = _0x19ab79;
}

function removeOppHud() {
    const _0x45613b = _0x35ae04,
        _0x3469e2 = document['getElementById']('hc-opp-hud');
    if (_0x3469e2) _0x3469e2['remove']();
    lastHudHtml = '';
}

function labelString(_0x3385fe) {
    const _0x379786 = _0x35ae04;
    if (!_0x3385fe) return '';
    try {
        if (_0x3385fe['string'] != null && String(_0x3385fe['string'])['trim']()) return String(_0x3385fe['string'])['trim']();
    } catch (_0x57cfc7) {}
    return '';
}

function parseMoney(_0x3c3db4) {
    const _0x5de6a8 = _0x35ae04;
    if (_0x3c3db4 == null || _0x3c3db4 === '') return null;
    const _0xba5340 = String(_0x3c3db4)['replace'](/,/g, '')['replace'](/\s/g, ''),
        _0x9c04b7 = _0xba5340['match'](/^([\d.]+)([KMB])?$/i);
    if (!_0x9c04b7) {
        const _0x5e5e0b = parseFloat(_0xba5340['replace'](/[^0-9.]/g, ''));
        return isFinite(_0x5e5e0b) ? _0x5e5e0b : null;
    }
    let _0x17b386 = parseFloat(_0x9c04b7[0x1]);
    const _0x1c3869 = (_0x9c04b7[0x2] || '')['toUpperCase']();
    if (_0x1c3869 === 'K') _0x17b386 *= 0x3e8;
    if (_0x1c3869 === 'M') _0x17b386 *= 0xf4240;
    if (_0x1c3869 === 'B') _0x17b386 *= 0x3b9aca00;
    return isFinite(_0x17b386) ? _0x17b386 : null;
}

function topHeaderPlayer() {
    const _0x372d4d = _0x35ae04;
    if (!(cachedTopHeader && cachedTopHeader['node'] && cachedTopHeader['node']['isValid'] !== ![])) {
        cachedTopHeader = null;
        const _0x2c576e = getScene();
        if (!_0x2c576e) return null;
        walkTree(_0x2c576e, function(_0x3549b8) {
            const _0x4c28b2 = _0x372d4d;
            if (cachedTopHeader) return;
            const _0x11c3b4 = componentsOf(_0x3549b8);
            for (let _0x544f2c = 0x0; _0x544f2c < _0x11c3b4['length']; _0x544f2c++) {
                const _0x4c815d = _0x11c3b4[_0x544f2c];
                if (classNameOf(_0x4c815d) === 'TopHeaderPopup' || _0x4c815d['lb_name'] && _0x4c815d['lb_tien']) {
                    cachedTopHeader = _0x4c815d;
                    return;
                }
            }
        }, 0x0);
    }
    const _0x5bd475 = cachedTopHeader;
    if (!_0x5bd475) return null;
    const _0x1f5a02 = labelString(_0x5bd475['lb_name']),
        _0x49532d = parseMoney(labelString(_0x5bd475['lb_tien']));
    if (!_0x1f5a02 && _0x49532d == null) return null;
    return {
        'name': _0x1f5a02,
        'money': _0x49532d
    };
}

function buildPlayerState(_0x353e2e, _0x2a6d54) {
    const _0x305161 = _0x35ae04,
        _0x54c245 = {
            'name': playerState['name'] || '',
            'money': playerState['money'],
            'phase': 'lobby',
            'phaseLabel': 'Đang ở sảnh'
        },
        _0x102dfd = _0x353e2e && _0x353e2e['my_info'];
    if (_0x102dfd) {
        try {
            if (typeof _0x102dfd['getName'] === 'function') _0x54c245['name'] = _0x102dfd['getName']() || _0x54c245['name'];
        } catch (_0x5f3dcd) {}
        try {
            if (!_0x54c245['name'] && _0x102dfd['info']) _0x54c245['name'] = _0x102dfd['info']['displayName'] || _0x54c245['name'];
        } catch (_0x291a4a) {}
        try {
            if (typeof _0x102dfd['getMoney'] === 'function') {
                const _0xdacf21 = _0x102dfd['getMoney']();
                if (_0xdacf21 != null && _0xdacf21 !== '') _0x54c245['money'] = _0xdacf21;
            }
        } catch (_0xc7dd58) {}
        try {
            if ((_0x54c245['money'] == null || _0x54c245['money'] === '') && _0x102dfd['info'] && _0x102dfd['info']['gold'] != null) _0x54c245['money'] = _0x102dfd['info']['gold'];
        } catch (_0x4c8138) {}
    }
    if (!_0x54c245['name'] || _0x54c245['money'] == null) {
        const _0x2a805c = topHeaderPlayer();
        if (_0x2a805c) {
            if (!_0x54c245['name'] && _0x2a805c['name']) _0x54c245['name'] = _0x2a805c['name'];
            if (_0x54c245['money'] == null && _0x2a805c['money'] != null) _0x54c245['money'] = _0x2a805c['money'];
        }
    }
    const _0x207c83 = _0x353e2e && typeof _0x353e2e['isPlaying'] === 'function' && _0x353e2e['isPlaying'](),
        _0x380bf2 = _0x2a6d54 === 'tlmn' || !!_0x353e2e,
        occupied = _0x380bf2 && isOccupied(_0x353e2e),
        _0x37bda0 = _0x380bf2 && hasGuest(_0x353e2e),
        _0x2109cf = _0x380bf2 && allOppTeam(_0x353e2e);
    if (halted) return playerState['phase'] === 'table_broken' || playerState['phase'] === 'vs_guest_done' ? (_0x54c245['phase'] = playerState['phase'], _0x54c245['phaseLabel'] = playerState['phaseLabel']) : (_0x54c245['phase'] = 'halt', _0x54c245['phaseLabel'] = 'Đã\x20dừng'), playerState = _0x54c245, _0x54c245;
    if (tableBroken) return _0x54c245['phase'] = 'table_broken', _0x54c245['phaseLabel'] = 'Bàn bị phá', playerState = _0x54c245, _0x54c245;
    if (hunting && huntState !== 'found') return _0x54c245['phase'] = 'hunt', _0x54c245['phaseLabel'] = huntMode === 'join' && sharedRoom && sharedRoom['hostName'] ? 'Đang vào bàn của ' + sharedRoom['hostName'] : 'Đang tạo bàn $' + betLabel(), playerState = _0x54c245, _0x54c245;
    if (!_0x380bf2) {
        if (playerState['phase'] === 'vs_guest_done') _0x54c245['phase'] = 'vs_guest_done', _0x54c245['phaseLabel'] = 'Vừa đánh xong với khách';
        else lastBrokenLabel ? (_0x54c245['phase'] = 'table_broken', _0x54c245['phaseLabel'] = 'Bàn bị phá') : (_0x54c245['phase'] = 'lobby', _0x54c245['phaseLabel'] = 'Đang\x20ở\x20sảnh');
        return playerState = _0x54c245, _0x54c245;
    }
    if (vsGuest && _0x207c83) return _0x54c245['phase'] = 'vs_guest', _0x54c245['phaseLabel'] = 'Đang đánh bài với khách', playerState = _0x54c245, _0x54c245;
    if (_0x207c83) {
        _0x54c245['phase'] = 'xa';
        const _0x1700b6 = firstOppName(_0x353e2e);
        return _0x54c245['phaseLabel'] = _0x1700b6 && isTeammate(_0x1700b6) ? 'Đang xả với ' + _0x1700b6 : 'Đang\x20xả', playerState = _0x54c245, _0x54c245;
    }
    if (tablePhase === 'wait_guest') return _0x54c245['phase'] = 'wait_guest', _0x54c245['phaseLabel'] = 'Đang đợi khách', playerState = _0x54c245, _0x54c245;
    if (_0x2109cf || occupied) return _0x54c245['phase'] = 'ok', _0x54c245['phaseLabel'] = huntMode === 'join' ? 'Tìm\x20phòng\x20thành\x20công' : 'Đã tạo phòng thành công', playerState = _0x54c245, _0x54c245;
    return _0x54c245['phase'] = 'ok', _0x54c245['phaseLabel'] = huntMode === 'join' ? 'Tìm phòng thành công' : 'Đã\x20tạo\x20phòng\x20thành\x20công', playerState = _0x54c245, _0x54c245;
}

function postStateToIsolated(_0xfb6e2e) {
    const _0x5df7b4 = _0x35ae04,
        _0x33ffe3 = {
            '__cardHook': !![],
            'type': 'STATE',
            'armed': armed,
            'remain': _0xfb6e2e && _0xfb6e2e['remain'] != null ? _0xfb6e2e['remain'] : 0x0,
            'cards': _0xfb6e2e && _0xfb6e2e['cards'] ? _0xfb6e2e['cards'] : [],
            'player': playerState
        };
    window['postMessage'](_0x33ffe3, '*');
}

function findComponentByName(_0x1f8789) {
    const _0x54ff70 = getScene();
    let _0x561aee = null;
    if (!_0x54ff70) return null;
    return walkTree(_0x54ff70, function(_0x4c269b) {
        const _0x22fb8e = null /* decoder removed */;
        if (_0x561aee) return;
        const _0x26b3b2 = componentsOf(_0x4c269b);
        for (let _0x188cbd = 0x0; _0x188cbd < _0x26b3b2['length']; _0x188cbd++) {
            if (classNameOf(_0x26b3b2[_0x188cbd]) === _0x1f8789) {
                _0x561aee = _0x26b3b2[_0x188cbd];
                return;
            }
        }
    }, 0x0), _0x561aee;
}

function isOccupied(_0x252ab8) {
    const _0x57b11d = _0x35ae04;
    if (!_0x252ab8) return ![];
    let _0xe4dd7e = 0x0;
    forEachOpponent(_0x252ab8, function() {
        _0xe4dd7e += 0x1;
    });
    if (_0xe4dd7e > 0x0) return !![];
    try {
        if (typeof _0x252ab8['getNumPlayer'] === 'function' && +_0x252ab8['getNumPlayer']() > 0x1) return !![];
    } catch (_0x159373) {}
    try {
        if (_0x252ab8['numPlayer'] > 0x1) return !![];
    } catch (_0xbbe0bb) {}
    return ![];
}

function playerName(_0x39e27c) {
    const _0x1409c5 = _0x35ae04;
    if (!_0x39e27c) return '';
    try {
        if (typeof _0x39e27c['getName'] === 'function') {
            const _0x18bc16 = _0x39e27c['getName']();
            if (_0x18bc16) return String(_0x18bc16)['trim']();
        }
    } catch (_0x236706) {}
    try {
        if (_0x39e27c['displayName']) return String(_0x39e27c['displayName'])['trim']();
    } catch (_0x1eafa6) {}
    try {
        if (_0x39e27c['info'] && _0x39e27c['info']['displayName']) return String(_0x39e27c['info']['displayName'])['trim']();
    } catch (_0x4c4b5c) {}
    try {
        return labelString(_0x39e27c['lbl_displayName']);
    } catch (_0x48bb73) {}
    return '';
}

function nameEq(_0x20d096, _0x4f173e) {
    const _0x459c3e = _0x35ae04;
    return String(_0x20d096 || '')['trim']()['toLowerCase']() === String(_0x4f173e || '')['trim']()['toLowerCase']();
}

function isTeammate(_0x21249f) {
    const _0x44cfec = _0x35ae04,
        _0x2e2ef8 = String(_0x21249f || '')['trim']();
    if (!_0x2e2ef8) return ![];
    for (let _0x10fbc7 = 0x0; _0x10fbc7 < teamNames['length']; _0x10fbc7++) {
        if (nameEq(teamNames[_0x10fbc7], _0x2e2ef8)) return !![];
    }
    return ![];
}

function forEachOpponent(_0x3b4e57, _0x38be3d) {
    const _0x415692 = _0x35ae04,
        _0x455245 = _0x3b4e57 && _0x3b4e57['opponent_info'],
        _0x2c3766 = _0x455245 && _0x455245['length'] ? _0x455245['length'] : 0x0;
    for (let _0x404be6 = 0x0; _0x404be6 < _0x2c3766; _0x404be6++) {
        const _0x5c7f28 = _0x455245[_0x404be6];
        if (!_0x5c7f28) continue;
        try {
            if (typeof _0x5c7f28['isEmpty'] === 'function' && _0x5c7f28['isEmpty']()) continue;
        } catch (_0x28c9c5) {}
        _0x38be3d(_0x5c7f28);
    }
}

function hasOppNamed(_0x44277e, _0x49c9bc) {
    if (!_0x44277e || !_0x49c9bc) return ![];
    let _0x657e51 = ![];
    return forEachOpponent(_0x44277e, function(_0x5bb838) {
        if (nameEq(playerName(_0x5bb838), _0x49c9bc)) _0x657e51 = !![];
    }), _0x657e51;
}

function hasGuest(_0x5dabc3) {
    const _0x437886 = _0x35ae04;
    if (!teamNames['length']) return ![];
    let _0x46ed6e = ![];
    return forEachOpponent(_0x5dabc3, function(_0x407de8) {
        const _0x110c43 = playerName(_0x407de8);
        if (_0x110c43 && !isTeammate(_0x110c43)) _0x46ed6e = !![];
    }), _0x46ed6e;
}

function anyReady(_0x1def8d) {
    let _0x44540d = ![];
    return forEachOpponent(_0x1def8d, function(_0x196ead) {
        const _0x22d3e4 = null /* decoder removed */;
        try {
            if (_0x196ead['spr_ready'] && _0x196ead['spr_ready']['node'] && _0x196ead['spr_ready']['node']['active']) _0x44540d = !![];
        } catch (_0x2c87d7) {}
        try {
            if (_0x196ead['ready'] === !![]) _0x44540d = !![];
        } catch (_0x1afd99) {}
    }), _0x44540d;
}

function isBeginActive(_0x50d0b1) {
    const _0x413c67 = _0x35ae04;
    try {
        return !!(_0x50d0b1 && _0x50d0b1['btn_begin'] && _0x50d0b1['btn_begin']['node'] && _0x50d0b1['btn_begin']['node']['active']);
    } catch (_0x593ea4) {}
    return ![];
}

function canStartGame(_0xf4d906) {
    if (anyReady(_0xf4d906)) return !![];
    return isBeginActive(_0xf4d906);
}

function hasGuestSeated(_0x31e7fc) {
    if (!isOccupied(_0x31e7fc)) return ![];
    if (allOppTeam(_0x31e7fc)) return ![];
    return !![];
}

function firstOppName(_0x10d48c) {
    let _0x1d963e = '';
    return forEachOpponent(_0x10d48c, function(_0x394f67) {
        if (!_0x1d963e) _0x1d963e = playerName(_0x394f67);
    }), _0x1d963e;
}

function allOppTeam(_0x4afe5c) {
    let _0x36af78 = ![],
        _0x224407 = ![];
    return forEachOpponent(_0x4afe5c, function(_0x11d692) {
        const _0xfdac79 = playerName(_0x11d692);
        if (!_0xfdac79) _0x224407 = !![];
        else {
            if (isTeammate(_0xfdac79)) _0x36af78 = !![];
        }
    }), _0x36af78 && !_0x224407;
}

function markTableBroken() {
    const _0x11eec0 = _0x35ae04;
    tableBroken = !![], hunting = ![], huntState = 'idle', tablePhase = 'leave_set', playedFirst = ![], guestSeen = ![], guestReady = ![], leaveTimer = 0x0, brokenRetry = 0x0, playerState['phase'] = 'table_broken', playerState['phaseLabel'] = 'Bàn bị phá', lastBrokenLabel = playerState['phaseLabel'], statusText = '', leaveTable();
}

function markVsGuestDone() {
    const _0x5ca301 = _0x35ae04;
    hunting = ![], huntState = 'idle', tablePhase = 'idle', vsGuest = ![], halted = ![], playerState['phase'] = 'vs_guest_done', playerState['phaseLabel'] = 'Vừa đánh xong với khách', statusText = '';
}

function ensureSoloMode(_0x4e2b9b) {
    const _0xb77bec = _0x35ae04;
    if (!_0x4e2b9b) return;
    try {
        const _0x56d4f0 = _0x4e2b9b['tog_solo_mode'];
        if (_0x56d4f0 && _0x56d4f0['isChecked'] === ![]) _0x56d4f0['isChecked'] = !![];
    } catch (_0x2f3432) {}
}

function betLabel() {
    const _0x2e3cd8 = _0x35ae04,
        _0x51eb5a = +bet;
    if (!isFinite(_0x51eb5a) || _0x51eb5a <= 0x0) return '100';
    if (_0x51eb5a >= 0xf4240) return String(_0x51eb5a / 0xf4240) + 'M';
    if (_0x51eb5a >= 0x3e8) return String(_0x51eb5a / 0x3e8) + 'K';
    return String(_0x51eb5a);
}

function quickPlayByBet() {
    const _0x3d50ca = _0x35ae04,
        _0x114609 = findComponentByName('TableListView');
    ensureSoloMode(_0x114609);
    let _0x2b95f8 = null;
    const _0x14191c = getScene();
    if (!_0x14191c) return ![];
    walkTree(_0x14191c, function(_0x4f9b55) {
        const _0x571a63 = null /* decoder removed */,
            _0x3d66dc = componentsOf(_0x4f9b55);
        for (let _0x39cdb8 = 0x0; _0x39cdb8 < _0x3d66dc['length']; _0x39cdb8++) {
            const _0x9ca062 = _0x3d66dc[_0x39cdb8];
            if (classNameOf(_0x9ca062) !== 'TableItemView') continue;
            if (+_0x9ca062['bet'] !== +bet) continue;
            if (_0x9ca062['node'] && _0x9ca062['node']['active'] === ![]) continue;
            _0x2b95f8 = _0x9ca062;
        }
    }, 0x0);
    if (_0x2b95f8 && typeof _0x2b95f8['onQuickPlayWithBet'] === 'function') try {
        return _0x2b95f8['maxUser'] = 0x2, _0x2b95f8['onQuickPlayWithBet'](), !![];
    } catch (_0x28b00a) {}
    if (_0x114609 && typeof _0x114609['getPooledItem'] === 'function') try {
        const _0x5aa7c4 = _0x114609['getPooledItem'](!![]);
        if (_0x5aa7c4 && typeof _0x5aa7c4['show'] === 'function') {
            _0x5aa7c4['show'](0x2, bet, 0x0, _0x114609['gameID'] || 0x1);
            if (typeof _0x5aa7c4['onQuickPlayWithBet'] === 'function') return _0x5aa7c4['onQuickPlayWithBet'](), !![];
        }
    } catch (_0xe88a6) {}
    return ![];
}

function parseSoBan(_0x347a1a) {
    const _0x5e6512 = _0x35ae04,
        _0x28416b = String(_0x347a1a || '')['replace'](/\s/g, '');
    if (_0x28416b['length'] < 0x2 || _0x28416b['length'] > 0x7) return null;
    return {
        'soBan': _0x28416b,
        'serverId': _0x28416b['charAt'](0x0),
        'roomId': +_0x28416b['slice'](0x1)
    };
}

function readTableNo(_0x3023f3) {
    const _0x18fa39 = _0x35ae04;
    try {
        const _0x1a3dd8 = _0x3023f3 && _0x3023f3['lbl_info'] && _0x3023f3['lbl_info']['string'],
            _0x3629b0 = String(_0x1a3dd8 || '')['match'](/Bàn:\s*(\d+)/i);
        if (_0x3629b0) return _0x3629b0[0x1];
    } catch (_0x48d8cf) {}
    return '';
}

function joinExactRoom(_0x1f05c1) {
    const _0x1a06cb = _0x35ae04;
    if (!_0x1f05c1) return ![];
    const _0x19b8b1 = parseSoBan(_0x1f05c1['soBan']) || {
        'roomId': +_0x1f05c1['roomId'],
        'serverId': _0x1f05c1['serverId']
    };
    if (!_0x19b8b1 || !_0x19b8b1['roomId']) return ![];
    const _0x390a09 = findComponentByName('TableListView');
    ensureSoloMode(_0x390a09);
    let _0x10e74c = null;
    const _0x182b8c = getScene();
    _0x182b8c && walkTree(_0x182b8c, function(_0x525d63) {
        const _0x2f190b = _0x1a06cb;
        if (_0x10e74c) return;
        const _0x7d170a = componentsOf(_0x525d63);
        for (let _0x2950cb = 0x0; _0x2950cb < _0x7d170a['length']; _0x2950cb++) {
            if (classNameOf(_0x7d170a[_0x2950cb]) === 'TableItemView') {
                _0x10e74c = _0x7d170a[_0x2950cb];
                return;
            }
        }
    }, 0x0);
    if (!_0x10e74c && _0x390a09 && typeof _0x390a09['getPooledItem'] === 'function') try {
        _0x10e74c = _0x390a09['getPooledItem'](!![]);
    } catch (_0x481e05) {}
    if (!_0x10e74c || typeof _0x10e74c['onJoinRoom'] !== 'function') return ![];
    try {
        return _0x10e74c['roomID'] = _0x19b8b1['roomId'], _0x10e74c['serverID'] = _0x19b8b1['serverId'], _0x10e74c['hasPass'] = ![], _0x10e74c['bet'] = +(_0x1f05c1['bet'] || bet), _0x10e74c['maxUser'] = 0x2, _0x10e74c['gameID'] = _0x390a09 && _0x390a09['gameID'] || 0x1, _0x10e74c['onJoinRoom'](), !![];
    } catch (_0x6361a3) {}
    return ![];
}

function successText() {
    const _0x338820 = _0x35ae04;
    return huntMode === 'join' ? 'Tìm phòng thành công' : 'Đã tạo phòng thành công';
}

function onFoundRoom(_0x1d988d) {
    const _0x3a69b1 = _0x35ae04,
        _0x212ec2 = readTableNo(_0x1d988d) || '',
        _0x21be56 = parseSoBan(_0x212ec2) || {};
    let _0x4c4611 = '';
    if (huntMode === 'join') _0x4c4611 = sharedRoom && sharedRoom['hostName'] || '';
    else {
        try {
            _0x4c4611 = String(playerState && playerState['name'] || '')['trim']();
        } catch (_0x22526b) {}
        if (!_0x4c4611) try {
            _0x4c4611 = playerName(_0x1d988d && _0x1d988d['my_info']);
        } catch (_0x3112da) {}
        if (!_0x4c4611) {
            const _0x2d6b39 = topHeaderPlayer();
            if (_0x2d6b39 && _0x2d6b39['name']) _0x4c4611 = String(_0x2d6b39['name'])['trim']();
        }
    }
    hunting = ![], huntState = 'found', statusText = successText(), tablePhase = 'seated', foundAt = Date['now'](), passFlag = ![], playerState['phase'] = 'ok', playerState['phaseLabel'] = statusText, window['postMessage']({
        '__cardHook': !![],
        'type': 'HUNT_FOUND',
        'room': {
            'soBan': _0x212ec2,
            'roomId': _0x21be56['roomId'],
            'serverId': _0x21be56['serverId'],
            'bet': bet,
            'hostName': _0x4c4611
        }
    }, '*');
}

function leaveTable() {
    const _0x145ba0 = _0x35ae04,
        _0x18a33b = findGameView();
    if (!_0x18a33b) {
        try {
            if (typeof cc !== 'undefined') cc['director']['loadScene']('scene_tableView');
        } catch (_0x51424f) {}
        return ![];
    }
    let _0x2c15df = ![];
    try {
        _0x2c15df = !!(typeof _0x18a33b['isPlaying'] === 'function' && _0x18a33b['isPlaying']());
    } catch (_0x2450ac) {}
    if (_0x2c15df) {
        try {
            const _0x3b77e7 = _0x18a33b['tienLenOptionsPopup'];
            if (_0x3b77e7 && typeof _0x3b77e7['exitRoom'] === 'function' && !_0x3b77e7['isWillExit']) _0x3b77e7['exitRoom']();
        } catch (_0x434925) {}
        return !![];
    }
    try {
        _0x18a33b['leaveRoom'](![]);
    } catch (_0xa2f0ed) {}
    if (tableBroken) {
        brokenRetry += 0x1;
        if (brokenRetry >= 0x4) try {
            if (typeof cc !== 'undefined') cc['director']['loadScene']('scene_tableView');
        } catch (_0x3da67b) {}
    }
    return !![];
}

function isHost(_0xf2fc18) {
    const _0x371b98 = _0x35ae04;
    try {
        if (_0xf2fc18 && typeof _0xf2fc18['getIsHost'] === 'function') return !!_0xf2fc18['getIsHost']();
    } catch (_0x1aff60) {}
    return huntMode === 'create';
}

function gameActive(_0x3c9d36) {
    const _0x14f382 = _0x35ae04;
    if (isMyTurn(_0x3c9d36)) return !![];
    try {
        if (_0x3c9d36['currentTurnUserId'] != null && _0x3c9d36['currentTurnUserId'] !== '') return !![];
    } catch (_0x340731) {}
    try {
        const _0x3bb73c = _0x3c9d36['opponent_info'] || [],
            _0x400f9c = _0x3bb73c['length'] || 0x0;
        for (let _0xd5217a = 0x0; _0xd5217a < _0x400f9c; _0xd5217a++) {
            const _0x20cbc7 = _0x3bb73c[_0xd5217a];
            if (!_0x20cbc7) continue;
            if (typeof _0x20cbc7['isEmpty'] === 'function' && _0x20cbc7['isEmpty']()) continue;
            if (_0x20cbc7['nodeTimer'] && _0x20cbc7['nodeTimer']['active']) return !![];
        }
    } catch (_0x1c3721) {}
    return ![];
}

function isMyTurn(_0x4fe3fc) {
    const _0x4cb033 = _0x35ae04;
    try {
        if (_0x4fe3fc['btn_danhbai'] && _0x4fe3fc['btn_danhbai']['node'] && _0x4fe3fc['btn_danhbai']['node']['active']) return !![];
    } catch (_0x967d44) {}
    try {
        if (_0x4fe3fc['currentTurnUserId'] != null && typeof _0x4fe3fc['isMe'] === 'function' && _0x4fe3fc['isMe'](_0x4fe3fc['currentTurnUserId'])) return !![];
    } catch (_0x3a985a) {}
    return ![];
}

function _0x41cea1(_0x36abb9) {
    const _0x2a0a6d = _0x35ae04;
    if (!_0x36abb9 || typeof _0x36abb9['sendReady'] !== 'function') return ![];
    const _0x2d7ba2 = isHost(_0x36abb9);
    try {
        if (_0x2d7ba2) {
            if (!isOccupied(_0x36abb9)) return ![];
            if (allOppTeam(_0x36abb9) && !canStartGame(_0x36abb9)) try {
                if (!(_0x36abb9['btn_begin'] && _0x36abb9['btn_begin']['node'] && _0x36abb9['btn_begin']['node']['active'])) return ![];
            } catch (_0x2fb130) {
                return ![];
            }
            if (_0x36abb9['btn_begin'] && _0x36abb9['btn_begin']['node'] && _0x36abb9['btn_begin']['node']['active']) {
                _0x36abb9['sendReady']();
                try {
                    _0x36abb9['btn_begin']['node']['active'] = ![];
                } catch (_0x50af78) {}
                return !![];
            }
            if (hasGuest(_0x36abb9) && canStartGame(_0x36abb9)) {
                _0x36abb9['sendReady']();
                try {
                    if (_0x36abb9['btn_begin'] && _0x36abb9['btn_begin']['node']) _0x36abb9['btn_begin']['node']['active'] = ![];
                } catch (_0xb3b8cb) {}
                return !![];
            }
            return ![];
        }
        return _0x36abb9['sendReady'](), !![];
    } catch (_0x26dab7) {}
    return ![];
}

function tryAutoPlay(_0x41ae3c) {
    const _0x2e260e = _0x35ae04;
    try {
        if (!_0x41ae3c['isPlaying'] || !_0x41ae3c['isPlaying']()) return ![];
        const _0x50b9f8 = _0x41ae3c['tienLenOptionsPopup'];
        if (!_0x50b9f8 || typeof _0x50b9f8['exitRoom'] !== 'function') return ![];
        if (_0x50b9f8['isWillExit']) return !![];
        return _0x50b9f8['exitRoom'](), !!_0x50b9f8['isWillExit'];
    } catch (_0x4c433a) {}
    return ![];
}
const _0x3b981d = [0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0x1];

function _0x5c8f31(_0x50e629) {
    if (_0x50e629 === 0x2) return 0xf;
    if (_0x50e629 === 0x1) return 0xe;
    return +_0x50e629;
}

function suitOrder(_0x711231) {
    const _0x197796 = _0x35ae04;
    if (_0x711231 && _0x711231['rawS'] != null) return +_0x711231['rawS'];
    const _0x42f0fe = {
        0x0: 0x1,
        0x3: 0x2,
        0x2: 0x3,
        0x1: 0x4
    };
    return _0x42f0fe[_0x711231 && _0x711231['suit']] || 0x0;
}

function compareCards(_0x555878, _0x5ca642) {
    const _0x8c1b3 = _0x35ae04,
        _0x34a0ae = _0x5c8f31(_0x555878['rank']) - _0x5c8f31(_0x5ca642['rank']);
    if (_0x34a0ae) return _0x34a0ae;
    return suitOrder(_0x555878) - suitOrder(_0x5ca642);
}

function _0x168310(_0x1f21c2) {
    const _0x5cb98e = _0x35ae04;
    return _0x3b981d['indexOf'](_0x1f21c2);
}

function myHandItems() {
    const _0x543b6d = _0x35ae04,
        _0x1f8784 = findGameView();
    if (!_0x1f8784 || !_0x1f8784['my_info'] || typeof _0x1f8784['my_info']['getPlayerCard'] !== 'function') return [];
    let _0x30fdc9 = [];
    try {
        _0x30fdc9 = _0x1f8784['my_info']['getPlayerCard']() || [];
    } catch (_0x2c1460) {
        return [];
    }
    const _0x48a070 = [];
    for (let _0x122196 = 0x0; _0x122196 < _0x30fdc9['length']; _0x122196++) {
        const _0xa1336e = readCard(_0x30fdc9[_0x122196]);
        if (_0xa1336e && _0xa1336e['item']) _0x48a070['push'](_0xa1336e);
    }
    return _0x48a070;
}

function groupByRank(_0x448b41) {
    const _0x38c5fc = _0x35ae04,
        _0x21fd23 = {};
    for (let _0x480888 = 0x0; _0x480888 < _0x448b41['length']; _0x480888++) {
        const _0x49e36a = _0x448b41[_0x480888]['rank'];
        if (!_0x21fd23[_0x49e36a]) _0x21fd23[_0x49e36a] = [];
        _0x21fd23[_0x49e36a]['push'](_0x448b41[_0x480888]);
    }
    return Object['keys'](_0x21fd23)['forEach'](function(_0x18221a) {
        const _0x5dfbc0 = _0x38c5fc;
        _0x21fd23[_0x18221a]['sort'](function(_0x1f21ee, _0x11e69b) {
            return suitOrder(_0x11e69b) - suitOrder(_0x1f21ee);
        });
    }), _0x21fd23;
}

function comboScore(_0x434c7f, _0x5d2107) {
    const _0x28252d = _0x35ae04;
    let _0x4695a4 = _0x5d2107[0x0];
    for (let _0x168d92 = 0x1; _0x168d92 < _0x5d2107['length']; _0x168d92++)
        if (compareCards(_0x5d2107[_0x168d92], _0x4695a4) > 0x0) _0x4695a4 = _0x5d2107[_0x168d92];
    const _0x21d838 = {
        'loc': 0x4,
        'trips': 0x3,
        'pair': 0x2,
        'single': 0x1
    };
    return (_0x21d838[_0x434c7f] || 0x0) * 0xf4240 + _0x5c8f31(_0x4695a4['rank']) * 0x64 + suitOrder(_0x4695a4) + _0x5d2107['length'];
}

function findStrafes(_0x4ddfd3) {
    const _0x2589fa = _0x35ae04,
        _0x3ba5a9 = groupByRank(_0x4ddfd3),
        _0x2edabe = [];
    for (let _0x526943 = 0x0; _0x526943 < _0x3b981d['length']; _0x526943++) {
        const _0x420850 = _0x3b981d[_0x526943];
        if (_0x3ba5a9[_0x420850] && _0x3ba5a9[_0x420850]['length']) _0x2edabe['push'](_0x420850);
    }
    const _0x54451b = [];
    for (let _0x5d61ba = 0x0; _0x5d61ba < _0x2edabe['length']; _0x5d61ba++) {
        const _0x14e4f1 = [_0x2edabe[_0x5d61ba]];
        while (_0x5d61ba + 0x1 < _0x2edabe['length'] && _0x168310(_0x2edabe[_0x5d61ba + 0x1]) === _0x168310(_0x2edabe[_0x5d61ba]) + 0x1) {
            _0x5d61ba++, _0x14e4f1['push'](_0x2edabe[_0x5d61ba]);
        }
        if (_0x14e4f1['length'] < 0x3) continue;
        for (let _0x431e82 = _0x14e4f1['length']; _0x431e82 >= 0x3; _0x431e82--) {
            for (let _0x299847 = 0x0; _0x299847 + _0x431e82 <= _0x14e4f1['length']; _0x299847++) {
                const _0x5a8db9 = _0x14e4f1['slice'](_0x299847, _0x299847 + _0x431e82),
                    _0x51157d = _0x5a8db9['map'](function(_0x2c12c7) {
                        return _0x3ba5a9[_0x2c12c7][0x0];
                    });
                _0x54451b['push']({
                    'type': 'loc',
                    'cards': _0x51157d,
                    'score': comboScore('loc', _0x51157d)
                });
            }
        }
    }
    return _0x54451b['sort'](function(_0x287589, _0x48475f) {
        const _0x3b52c9 = _0x2589fa;
        return _0x48475f['score'] - _0x287589['score'];
    }), _0x54451b;
}

function findGroups(_0x127d26, _0x3673fe, _0x3f95ad) {
    const _0xe55b83 = _0x35ae04,
        _0x1ecf97 = groupByRank(_0x127d26),
        _0x123c6f = [];
    return Object['keys'](_0x1ecf97)['forEach'](function(_0x2f2eaf) {
        const _0x13a977 = _0xe55b83;
        if (_0x1ecf97[_0x2f2eaf]['length'] >= _0x3673fe) {
            const _0x53e538 = _0x1ecf97[_0x2f2eaf]['slice'](0x0, _0x3673fe);
            _0x123c6f['push']({
                'type': _0x3f95ad,
                'cards': _0x53e538,
                'score': comboScore(_0x3f95ad, _0x53e538)
            });
        }
    }), _0x123c6f['sort'](function(_0x14e7f6, _0x56dfd0) {
        const _0x5ded85 = _0xe55b83;
        return _0x56dfd0['score'] - _0x14e7f6['score'];
    }), _0x123c6f;
}

function findSingles(_0xd25533) {
    const _0x552996 = _0x35ae04;
    return _0xd25533['slice']()['sort'](compareCards)['reverse']()['map'](function(_0xf9e401) {
        const _0x525c0a = _0x552996;
        return {
            'type': 'single',
            'cards': [_0xf9e401],
            'score': comboScore('single', [_0xf9e401])
        };
    });
}

function pickAnyPlay(_0x1a6980) {
    const _0x577d53 = _0x35ae04,
        _0x47f982 = findStrafes(_0x1a6980);
    if (_0x47f982['length']) return _0x47f982[0x0];
    const _0x237afa = findGroups(_0x1a6980, 0x3, 'trips');
    if (_0x237afa['length']) return _0x237afa[0x0];
    const _0x585704 = findGroups(_0x1a6980, 0x2, 'pair');
    if (_0x585704['length']) return _0x585704[0x0];
    const _0x1a564f = findSingles(_0x1a6980);
    return _0x1a564f[0x0] || null;
}

function lastTurnCards(_0x45e67b) {
    const _0x1de3d5 = _0x35ae04,
        _0x4371a4 = _0x45e67b && _0x45e67b['_lastTurnCards'] || [],
        _0x43eca2 = [];
    for (let _0x19188f = 0x0; _0x19188f < _0x4371a4['length']; _0x19188f++) {
        const _0x30dfcb = readCard(_0x4371a4[_0x19188f]);
        if (_0x30dfcb) _0x43eca2['push'](_0x30dfcb);
    }
    return _0x43eca2;
}

function lastPlayWasMine(_0xc17402) {
    const _0x5345eb = _0x35ae04;
    try {
        if (_0xc17402['lastPlayingUserId'] != null && typeof _0xc17402['isMe'] === 'function' && _0xc17402['isMe'](_0xc17402['lastPlayingUserId'])) return !![];
    } catch (_0x209065) {}
    return ![];
}

function _0x369f28(_0x23365e) {
    const _0x20e07a = _0x35ae04;
    if (!_0x23365e['length']) return ![];
    const _0x27906a = _0x23365e[0x0]['rank'];
    for (let _0x86d78a = 0x1; _0x86d78a < _0x23365e['length']; _0x86d78a++)
        if (_0x23365e[_0x86d78a]['rank'] !== _0x27906a) return ![];
    return !![];
}

function _0x30c6d6(_0x3600c3) {
    const _0x5cdb74 = _0x35ae04;
    if (!_0x3600c3 || _0x3600c3['length'] < 0x3) return ![];
    const _0xa2b643 = _0x3600c3['map'](function(_0x4c690c) {
            const _0x1c217d = _0x5cdb74;
            return _0x4c690c['rank'];
        }),
        _0x37d54b = {};
    for (let _0x43ab4f = 0x0; _0x43ab4f < _0xa2b643['length']; _0x43ab4f++) {
        if (_0xa2b643[_0x43ab4f] === 0x2) return ![];
        if (_0x37d54b[_0xa2b643[_0x43ab4f]]) return ![];
        _0x37d54b[_0xa2b643[_0x43ab4f]] = 0x1;
    }
    const _0x3bb577 = _0xa2b643['map'](_0x168310)['filter'](function(_0x3bd449) {
        return _0x3bd449 >= 0x0;
    })['sort'](function(_0x260757, _0x5b1c8f) {
        return _0x260757 - _0x5b1c8f;
    });
    if (_0x3bb577['length'] !== _0x3600c3['length']) return ![];
    for (let _0x4b2839 = 0x1; _0x4b2839 < _0x3bb577['length']; _0x4b2839++)
        if (_0x3bb577[_0x4b2839] !== _0x3bb577[_0x4b2839 - 0x1] + 0x1) return ![];
    return !![];
}

function parseCombo(_0x27d225) {
    const _0x2ca422 = _0x35ae04,
        _0x15e23a = _0x27d225['length'];
    if (!_0x15e23a) return null;
    if (_0x15e23a === 0x1) return {
        'type': 'single',
        'cards': _0x27d225,
        'hi': _0x27d225[0x0]
    };
    if (_0x15e23a === 0x2 && _0x369f28(_0x27d225)) return {
        'type': 'pair',
        'cards': _0x27d225,
        'hi': _0x27d225['slice']()['sort'](compareCards)[0x1]
    };
    if (_0x15e23a === 0x3 && _0x369f28(_0x27d225)) return {
        'type': 'trips',
        'cards': _0x27d225,
        'hi': _0x27d225['slice']()['sort'](compareCards)[0x2]
    };
    if (_0x30c6d6(_0x27d225)) {
        let _0x41ae03 = _0x27d225[0x0];
        for (let _0x4e37ee = 0x1; _0x4e37ee < _0x27d225['length']; _0x4e37ee++)
            if (compareCards(_0x27d225[_0x4e37ee], _0x41ae03) > 0x0) _0x41ae03 = _0x27d225[_0x4e37ee];
        return {
            'type': 'loc',
            'cards': _0x27d225,
            'hi': _0x41ae03,
            'len': _0x15e23a
        };
    }
    return null;
}

function comboBeats(_0x3bac86, _0x470da0) {
    const _0x1f9056 = _0x35ae04;
    if (!_0x3bac86 || !_0x470da0 || _0x3bac86['type'] !== _0x470da0['type']) return ![];
    if (_0x3bac86['type'] === 'loc' && _0x3bac86['cards']['length'] !== _0x470da0['cards']['length']) return ![];
    const _0x2ec22f = compareCards(_0x3bac86['hi'] || _0x3bac86['cards'][_0x3bac86['cards']['length'] - 0x1], _0x470da0['hi']);
    return _0x2ec22f > 0x0;
}

function findCounterPlay(_0x5139a4, _0x2c2929) {
    const _0x2aea07 = _0x35ae04,
        _0x1adc9b = parseCombo(_0x2c2929);
    if (!_0x1adc9b) return null;
    let _0x576a4c = [];
    if (_0x1adc9b['type'] === 'loc') _0x576a4c = findStrafes(_0x5139a4)['filter'](function(_0x2c8e01) {
        const _0x418de3 = _0x2aea07;
        return _0x2c8e01['cards']['length'] === _0x1adc9b['cards']['length'];
    });
    else {
        if (_0x1adc9b['type'] === 'trips') _0x576a4c = findGroups(_0x5139a4, 0x3, 'trips');
        else {
            if (_0x1adc9b['type'] === 'pair') _0x576a4c = findGroups(_0x5139a4, 0x2, 'pair');
            else _0x576a4c = findSingles(_0x5139a4);
        }
    }
    for (let _0x280a83 = 0x0; _0x280a83 < _0x576a4c['length']; _0x280a83++) {
        const _0x27a223 = parseCombo(_0x576a4c[_0x280a83]['cards']);
        if (_0x27a223 && comboBeats(_0x27a223, _0x1adc9b)) return _0x576a4c[_0x280a83];
    }
    return null;
}

function deselectAll(_0x1aac17) {
    const _0x2805fe = _0x35ae04;
    for (let _0x30e564 = 0x0; _0x30e564 < _0x1aac17['length']; _0x30e564++) {
        try {
            if (_0x1aac17[_0x30e564]['item'] && typeof _0x1aac17[_0x30e564]['item']['selected'] === 'function') _0x1aac17[_0x30e564]['item']['selected'](![]);
        } catch (_0x4bc534) {}
    }
}

function selectAll(_0x3e18bb) {
    const _0x4194ec = _0x35ae04;
    for (let _0x5221e5 = 0x0; _0x5221e5 < _0x3e18bb['length']; _0x5221e5++) {
        try {
            if (_0x3e18bb[_0x5221e5]['item'] && typeof _0x3e18bb[_0x5221e5]['item']['selected'] === 'function') _0x3e18bb[_0x5221e5]['item']['selected'](!![]);
        } catch (_0x3e9314) {}
    }
}

function autoPlay(_0xcb404e) {
    const _0x17e93a = _0x35ae04;
    if (!_0xcb404e || !isMyTurn(_0xcb404e)) {
        autoPlaySince = 0x0;
        return;
    }
    const _0x25a04b = Date['now']();
    if (!autoPlaySince) autoPlaySince = _0x25a04b;
    const _0x2d837d = xaDelay > 0x0 ? xaDelay : 0x0;
    if (_0x25a04b - autoPlaySince < _0x2d837d) return;
    if (_0x25a04b - lastAutoPlayAt < 0xfa) return;
    const _0x2cfd3f = myHandItems();
    if (!_0x2cfd3f['length']) return;
    const _0x28679c = lastTurnCards(_0xcb404e);
    let _0x26d491 = null;
    if (!_0x28679c['length'] || lastPlayWasMine(_0xcb404e)) _0x26d491 = pickAnyPlay(_0x2cfd3f);
    else _0x26d491 = findCounterPlay(_0x2cfd3f, _0x28679c);
    lastAutoPlayAt = _0x25a04b, autoPlaySince = 0x0;
    if (!_0x26d491 || !_0x26d491['cards'] || !_0x26d491['cards']['length']) {
        try {
            if (typeof _0xcb404e['onBoLuot'] === 'function') _0xcb404e['onBoLuot']();
        } catch (_0x5af7e9) {}
        return;
    }
    try {
        deselectAll(_0x2cfd3f), selectAll(_0x26d491['cards']);
        if (typeof _0xcb404e['onDanhBai'] === 'function') _0xcb404e['onDanhBai']();
    } catch (_0x47b730) {
        try {
            if (typeof _0xcb404e['onBoLuot'] === 'function') _0xcb404e['onBoLuot']();
        } catch (_0x443d26) {}
    }
}

function mainTick() {
    const _0x243281 = _0x35ae04;
    if (!armed) return;
    const _0x2f89b0 = getScene(),
        _0x3c50a6 = _0x2f89b0 && _0x2f89b0['name'] ? _0x2f89b0['name'] : '',
        _0x1397c7 = findGameView(),
        _0x41b89d = _0x3c50a6 === 'tlmn' || !!_0x1397c7,
        _0x3c330e = Date['now']();
    if (!_0x41b89d) {
        vsGuest && (markVsGuestDone(), vsGuest = ![]);
        if (tableBroken) tableBroken = ![];
        if (huntState === 'found') huntState = 'idle';
        if (playerState['phase'] === 'table_broken' || playerState['phase'] === 'vs_guest_done') halted = ![], hunting = ![], tablePhase = 'idle';
        else !halted && (tablePhase === 'xa' || tablePhase === 'wait_deal' || tablePhase === 'seated' || tablePhase === 'wait_guest' || tablePhase === 'leave_set' || tablePhase === 'vs_guest') && (tablePhase = 'idle', statusText = '', xaDecision = null);
        return;
    }
    if (!_0x1397c7) return;
    if (halted && !tableBroken) return;
    if (tableBroken) {
        _0x3c330e >= leaveTimer && (leaveTimer = _0x3c330e + 0x258, leaveTable());
        return;
    }
    let _0x5acb32 = 0x0;
    try {
        _0x5acb32 = myHandCards()['length'];
    } catch (_0x3afaee) {}
    let _0x2b451c = ![],
        _0x191c26 = ![];
    try {
        _0x2b451c = !!(typeof _0x1397c7['isPlaying'] === 'function' && _0x1397c7['isPlaying']());
    } catch (_0x356889) {}
    try {
        _0x191c26 = !!(typeof _0x1397c7['isEnded'] === 'function' && _0x1397c7['isEnded']());
    } catch (_0x2e1f2d) {}
    if (tablePhase === 'leave_set') {
        _0x3c330e >= leaveTimer && (leaveTimer = _0x3c330e + 0x1f4, leaveTable());
        return;
    }
    if (tablePhase === 'seated' || tablePhase === 'wait_deal') {
        if (!sawPlaying && huntMode === 'create' && hasGuest(_0x1397c7)) {
            markTableBroken();
            return;
        }
    }
    if (tablePhase === 'seated') {
        if (huntMode === 'join') {
            if (_0x3c330e - foundAt < 0x190) return;
            _0x41cea1(_0x1397c7) && (tablePhase = 'wait_deal', seatedAt = _0x3c330e);
            return;
        }
        if (_0x3c330e - foundAt < 0x190) return;
        if (isHost(_0x1397c7) && !isOccupied(_0x1397c7)) return;
        allOppTeam(_0x1397c7) && canStartGame(_0x1397c7) && (_0x41cea1(_0x1397c7) && (tablePhase = 'wait_deal', seatedAt = _0x3c330e));
        return;
    }
    if (tablePhase === 'wait_deal') {
        if (vsGuest) {
            if (_0x2b451c || _0x5acb32 >= 0x1) {
                tablePhase = 'vs_guest', playerState['phase'] = 'vs_guest', playerState['phaseLabel'] = 'Đang đánh bài với khách';
                return;
            }
            _0x3c330e - seatedAt > 0x190 && (_0x41cea1(_0x1397c7), seatedAt = _0x3c330e);
            return;
        }
        if (_0x5acb32 >= 0xa || _0x2b451c && _0x5acb32 >= 0x1) {
            if (hasGuest(_0x1397c7) || vsGuest) {
                vsGuest = !![], tablePhase = 'vs_guest', playerState['phase'] = 'vs_guest', playerState['phaseLabel'] = 'Đang đánh bài với khách';
                return;
            }
            if (!allOppTeam(_0x1397c7) && isOccupied(_0x1397c7)) return;
            tablePhase = 'xa', xaStartAt = _0x3c330e, passFlag = ![], xaDecision = null, statusText = 'Đang xả', playerState['phase'] = 'xa', playerState['phaseLabel'] = 'Đang xả';
            return;
        }
        _0x3c330e - seatedAt > 0x190 && (_0x41cea1(_0x1397c7), seatedAt = _0x3c330e);
        return;
    }
    if (tablePhase === 'xa') {
        if (_0x191c26 || !_0x2b451c && _0x5acb32 === 0x0) {
            sawPlaying = !![], guestSeen = ![], guestReady = ![], playedFirst = ![];
            if (xaDecision === !![]) {
                tablePhase = 'leave_set', leaveTable();
                return;
            }
            tablePhase = 'wait_guest', statusText = 'Đang đợi khách', playerState['phase'] = 'wait_guest', playerState['phaseLabel'] = 'Đang đợi khách';
            return;
        }
        const _0x3b28c3 = firstOppName(_0x1397c7);
        statusText = _0x3b28c3 && isTeammate(_0x3b28c3) ? 'Đang xả với ' + _0x3b28c3 : 'Đang xả', playerState['phase'] = 'xa', playerState['phaseLabel'] = statusText;
        if (_0x2b451c && isMyTurn(_0x1397c7) && allOppTeam(_0x1397c7)) autoPlay(_0x1397c7);
        if (_0x2b451c && xaDecision == null && allOppTeam(_0x1397c7)) {
            const _0x2e9c6b = lastTurnCards(_0x1397c7)['length'];
            if (isMyTurn(_0x1397c7) && _0x2e9c6b === 0x0) xaDecision = !![];
            else {
                if (_0x2e9c6b > 0x0 && !lastPlayWasMine(_0x1397c7)) xaDecision = ![];
                else {
                    if (gameActive(_0x1397c7) && !isMyTurn(_0x1397c7)) xaDecision = ![];
                }
            }
        }
        xaDecision === !![] && _0x2b451c && !passFlag && (passFlag = !![], tryAutoPlay(_0x1397c7));
        if (xaDecision === ![]) passFlag = !![];
        return;
    }
    if (tablePhase === 'vs_guest') {
        playerState['phase'] = 'vs_guest', playerState['phaseLabel'] = 'Đang đánh bài với khách';
        const _0x506cf5 = hasGuest(_0x1397c7);
        if (outGuest && sawPlaying && _0x506cf5 && _0x2b451c && !autoPlayedVsGuest) {
            if (tryAutoPlay(_0x1397c7)) autoPlayedVsGuest = !![];
        }
        if (!_0x2b451c || _0x191c26) {
            if (outGuest && sawPlaying && (_0x506cf5 || autoPlayedVsGuest)) {
                leaveTable();
                if (!_0x1397c7['isPlaying'] || !_0x1397c7['isPlaying']()) markVsGuestDone();
            } else tablePhase = 'wait_guest', vsGuest = ![];
        }
        return;
    }
    if (tablePhase === 'wait_guest' || sawPlaying && !_0x2b451c && !vsGuest && tablePhase === 'idle') {
        tablePhase = 'wait_guest', playerState['phase'] = 'wait_guest', playerState['phaseLabel'] = 'Đang đợi khách';
        const _0x578c64 = hasGuestSeated(_0x1397c7),
            _0x21b612 = isBeginActive(_0x1397c7);
        if (chongPha) {
            if (_0x578c64) {
                guestSeen = !![];
                if (_0x21b612) guestReady = !![];
            } else {
                if (guestSeen) {
                    const _0x3fd4de = !guestReady;
                    guestSeen = ![];
                    const _0x167ad9 = guestReady;
                    guestReady = ![];
                    if (_0x3fd4de && !_0x167ad9) {
                        markTableBroken();
                        return;
                    }
                }
            }
        } else guestSeen = ![], guestReady = ![];
        if (_0x578c64 && _0x21b612) {
            _0x41cea1(_0x1397c7) && (tablePhase = 'wait_deal', seatedAt = _0x3c330e, vsGuest = !![], autoPlayedVsGuest = ![], guestSeen = ![], guestReady = ![], playerState['phase'] = 'vs_guest', playerState['phaseLabel'] = 'Đang đánh bài với khách');
            return;
        }
    }
}

function joinHuntTick() {
    const _0xb39f81 = _0x35ae04;
    if (!armed || !hunting || halted || tableBroken) return;
    if (tablePhase === 'seated' || tablePhase === 'wait_deal' || tablePhase === 'xa' || tablePhase === 'wait_guest' || tablePhase === 'leave_set' || tablePhase === 'vs_guest') return;
    const _0x28e632 = Date['now'](),
        _0x5a730e = getScene(),
        _0x20a335 = _0x5a730e && _0x5a730e['name'] ? _0x5a730e['name'] : '',
        _0x2dc853 = findGameView(),
        _0x1b4c41 = _0x20a335 === 'tlmn' || !!_0x2dc853,
        _0x588913 = sharedRoom && sharedRoom['hostName'] ? String(sharedRoom['hostName'])['trim']() : '';
    if (huntMode === 'join') {
        if (!_0x588913) return;
        if (_0x1b4c41) {
            if (huntState !== 'checking') {
                huntState = 'checking', huntTimer = _0x28e632;
                return;
            }
            if (hasOppNamed(_0x2dc853, _0x588913)) {
                onFoundRoom(_0x2dc853);
                return;
            }
            const occupied = isOccupied(_0x2dc853),
                _0x366738 = firstOppName(_0x2dc853);
            if (occupied && !_0x366738) {
                _0x28e632 - huntTimer >= 0x3e8 && (leaveTable(), huntState = 'leaving', huntTimer = _0x28e632);
                return;
            }
            if (occupied && !nameEq(_0x366738, _0x588913)) {
                leaveTable(), huntState = 'leaving', huntTimer = _0x28e632;
                return;
            }!occupied && _0x28e632 - huntTimer >= 0x320 && (leaveTable(), huntState = 'leaving', huntTimer = _0x28e632);
            return;
        }
        if (huntState === 'leaving' && _0x28e632 - huntTimer < 0x320) return;
        if (huntState === 'joining' && _0x28e632 - joinTimer < 0x3e8) return;
        let _0x100c03 = ![];
        if (sharedRoom && (sharedRoom['soBan'] || sharedRoom['roomId']) ) {
            _0x100c03 = joinExactRoom(sharedRoom);
            if (_0x100c03) exactJoinTries += 0x1;
        }
        if (!_0x100c03) _0x100c03 = quickPlayByBet();
        _0x100c03 && (huntState = 'joining', joinTimer = _0x28e632);
        return;
    }
    if (_0x1b4c41) {
        if (huntState !== 'checking') {
            huntState = 'checking', huntTimer = _0x28e632;
            return;
        }
        const occupied = isOccupied(_0x2dc853);
        if (occupied) {
            leaveTable(), huntState = 'leaving', huntTimer = _0x28e632;
            return;
        }!occupied && _0x28e632 - huntTimer >= 0x640 && onFoundRoom(_0x2dc853);
        return;
    }
    if (huntState === 'leaving' && _0x28e632 - huntTimer < 0x320) return;
    if (huntState === 'joining' && _0x28e632 - joinTimer < 0x3e8) return;
    quickPlayByBet() && (huntState = 'joining', joinTimer = _0x28e632);
}

function stateTick() {
    const _0xda7fd0 = _0x35ae04;
    if (!armed) {
        removeOppHud();
        return;
    }
    const _0x581e67 = getScene(),
        _0x118766 = _0x581e67 && _0x581e67['name'] ? _0x581e67['name'] : '',
        _0x57c54a = findGameView(),
        _0x3b5655 = _0x118766 === 'tlmn' || !!_0x57c54a;
    !_0x3b5655 && !halted && (tablePhase === 'xa' || tablePhase === 'wait_deal' || tablePhase === 'seated' || tablePhase === 'wait_guest' || tablePhase === 'leave_set' || tablePhase === 'vs_guest') && (tablePhase = 'idle', statusText = '');
    playerState = buildPlayerState(_0x57c54a, _0x118766);
    if (!_0x57c54a) {
        if (_0x118766 === 'scene_tableView' || _0x118766 === 'tlmn') renderOppHud([], 0xd, 'Chờ ván mới');
        else !_0x581e67 && removeOppHud();
        postStateToIsolated({
            'remain': 0xd,
            'cards': []
        });
        return;
    }
    hookTable(_0x57c54a);
    const _0x2d1b44 = myHandCards(),
        _0x5e53f4 = handSignature(_0x2d1b44),
        _0x4ec453 = typeof _0x57c54a['isPlaying'] === 'function' && _0x57c54a['isPlaying'](),
        _0x10045d = typeof _0x57c54a['isEnded'] === 'function' && _0x57c54a['isEnded']();
    let _0x42368d = oppRemainTotal(_0x57c54a);
    const _0x13b227 = _0x2d1b44['length'] >= 0xa && prevHandLen < 0x5,
        _0x1f223b = _0x2d1b44['length'] >= 0xa && prevHandSig && _0x5e53f4 !== prevHandSig && overlapCount(prevHandSig, _0x5e53f4) <= 0x5,
        _0x5d14a9 = prevOppRemain >= 0x0 && _0x42368d >= prevOppRemain + 0x6;
    (_0x13b227 || _0x1f223b || _0x5d14a9) && resetRound(_0x13b227 ? 'chia bài' : _0x1f223b ? 'đổi tay' : 'còn lá+');
    prevHandLen = _0x2d1b44['length'], wasPlaying = _0x4ec453, wasEnded = _0x10045d, prevHandSig = _0x5e53f4;
    if (_0x42368d >= 0x0) prevOppRemain = _0x42368d;
    for (let _0x1e34fe = 0x0; _0x1e34fe < _0x2d1b44['length']; _0x1e34fe++) knownCardKeys['add'](cardKey(_0x2d1b44[_0x1e34fe]['suit'], _0x2d1b44[_0x1e34fe]['rank']));
    const _0x127c0d = oppLastTurnCards(_0x57c54a, knownCardKeys);
    for (let _0xe3fcb4 = 0x0; _0xe3fcb4 < _0x127c0d['length']; _0xe3fcb4++) {
        recordCard(_0x127c0d[_0xe3fcb4]['suit'], _0x127c0d[_0xe3fcb4]['rank'], {
            'zone': 'played',
            'source': 'opp'
        });
    }
    const _0x4b1c2f = recordedCards['filter'](function(_0x20fb85) {
        const _0x4d1150 = _0xda7fd0;
        return _0x20fb85['zone'] === 'played';
    });
    let _0xa6bc29 = _0x42368d;
    if (_0xa6bc29 < 0x0) _0xa6bc29 = Math['max'](0x0, 0xd - _0x4b1c2f['length']);
    const _0x317bb1 = _0xa6bc29 === 0x0 || _0x10045d ? 'Hết ván' : _0x4ec453 || _0x2d1b44['length'] >= 0x1 ? 'Đang ván' : 'Chờ ván mới';
    renderOppHud(_0x4b1c2f, _0xa6bc29, _0x317bb1), postStateToIsolated({
        'remain': _0xa6bc29,
        'cards': _0x4b1c2f
    });
}
window['cardHook'] = {
    'played': function() {
        const _0x291ae0 = _0x35ae04;
        return recordedCards['filter'](function(_0x8518d6) {
            const _0x4e2f44 = _0x291ae0;
            return _0x8518d6['zone'] === 'played';
        });
    },
    'findGame': findGameView,
    'hand': myHandCards,
    'tableNow': function() {
        const _0x4b353f = _0x35ae04,
            _0x118dff = findGameView();
        return _0x118dff && _0x118dff['_lastTurnCards'] ? dedupeCards(_0x118dff['_lastTurnCards']) : [];
    },
    'reset': function() {
        const _0x12c594 = _0x35ae04;
        recordedCards['length'] = 0x0, knownCardKeys['clear'](), lastHudHtml = '', prevHandLen = 0x0, prevHandSig = '', prevOppRemain = -0x1;
    }
}, window['addEventListener']('message', function(_0x37d554) {
    const _0x4df65f = _0x35ae04,
        _0x21440b = _0x37d554['data'];
    if (!_0x21440b || !_0x21440b['__cardHook']) return;
    if (_0x21440b['type'] === 'ARM') armed = !![];
    _0x21440b['type'] === 'DISARM' && (armed = ![], hunting = ![], halted = ![], huntState = 'idle', statusText = '', tablePhase = 'idle', passFlag = ![], lastBrokenLabel = '', removeOppHud());
    _0x21440b['type'] === 'HALT' && (halted = !![], hunting = ![], huntState = 'idle', playerState['phase'] !== 'table_broken' && playerState['phase'] !== 'vs_guest_done' && (statusText = '', tablePhase = 'idle', playerState['phase'] = 'halt', playerState['phaseLabel'] = 'Đã dừng'), passFlag = ![]);
    if (_0x21440b['type'] === 'XA_CFG') {
        const _0x427c3c = +_0x21440b['delay'];
        if (isFinite(_0x427c3c) && _0x427c3c >= 0x0) xaDelay = _0x427c3c;
        _0x21440b['chongPha'] != null && (chongPha = !!_0x21440b['chongPha'], !chongPha && (guestSeen = ![], guestReady = ![]));
        if (_0x21440b['outGuest'] != null) outGuest = !!_0x21440b['outGuest'];
    }
    if (_0x21440b['type'] === 'TEAM') {
        if (Array['isArray'](_0x21440b['names'])) teamNames = _0x21440b['names'];
    }
    if (_0x21440b['type'] === 'HUNT_START') {
        halted = ![];
        if (Array['isArray'](_0x21440b['names'])) teamNames = _0x21440b['names'];
        const _0x2d323c = _0x21440b['mode'] === 'join';
        if (_0x2d323c && _0x21440b['sharedRoom'] && _0x21440b['sharedRoom']['hostName']) {
            sharedRoom = _0x21440b['sharedRoom'];
            if (sharedRoom['bet']) bet = +sharedRoom['bet'] || bet;
        } else {
            const _0x29f9c9 = +_0x21440b['bet'];
            if (_0x29f9c9 > 0x0) bet = _0x29f9c9;
        }
        const _0x19f803 = tableBroken || tablePhase === 'seated' || tablePhase === 'wait_deal' || tablePhase === 'xa' || tablePhase === 'wait_guest' || tablePhase === 'leave_set' || tablePhase === 'vs_guest' || huntState === 'found';
        if (_0x19f803) return;
        if (hunting && huntMode === (_0x2d323c ? 'join' : 'create')) return;
        tableBroken = ![], playedFirst = ![], guestSeen = ![], guestReady = ![], sawPlaying = ![], vsGuest = ![], autoPlayedVsGuest = ![], xaDecision = null, exactJoinTries = 0x0;
        if (_0x2d323c) {
            sharedRoom = _0x21440b['sharedRoom'] && _0x21440b['sharedRoom']['hostName'] ? _0x21440b['sharedRoom'] : sharedRoom, huntMode = 'join';
            if (sharedRoom && sharedRoom['bet']) bet = +sharedRoom['bet'] || bet;
        } else sharedRoom = null, huntMode = 'create';
        hunting = !![], huntState = 'idle', huntTimer = 0x0, joinTimer = 0x0, statusText = '', tablePhase = 'idle', passFlag = ![], lastBrokenLabel = '', playerState['phase'] = 'hunt', playerState['phaseLabel'] = _0x2d323c ? 'Đang\x20vào\x20bàn\x20của\x20' + (sharedRoom && sharedRoom['hostName'] || '') : 'Đang\x20tạo\x20bàn\x20$' + betLabel();
    }
    _0x21440b['type'] === 'HUNT_STOP' && (hunting && (hunting = ![], huntState = 'idle'));
}), setInterval(function() {
    stateTick(), joinHuntTick(), mainTick();
}, 0x190), console['log']('%c[SUN] hook · chờ Control Connect', 'color:#f0c040;font-weight:bold');
}()));