/* ============================================================================
 * Sunwin - Probe QUICK JOIN (Chơi nhanh / Vào bàn ngay)
 * Dung duoc cho MOI SANH: TLMN, Sam Loc, ...
 *
 * >>> QUAN TRONG: phai DANG O TRONG SANH BAI (man danh sach ban), KHONG phai
 *     sanh chinh. Neu scene la 'game' va tableListView = null thi chua vao sanh.
 *
 * Chay trong DevTools Console (context top). Ket qua in ra + copy clipboard.
 *
 * Muc dich:
 *   - Doc gameID cua sanh hien tai (= gid de tao/join ban).
 *   - Doc source ham onQuickPlayWithBet / onJoinRoom  ("method join ngay").
 *   - Neu chua dung sanh: liet ke cac component 'table/room/lobby' de tim dung ten.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) {
    try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {}
    try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; }
  }
  function src(fn, n) { return safe(function () { return String(fn); }, '').slice(0, n || 2000); }

  var scene = safe(function () { return cc.director.getScene(); }, null);
  var out = {
    scene: scene && scene.name,
    tableListView: null,
    gameIdHolders: {},
    tableish: [],
    items: [],
    components: {},
    sources: {},
    hint: ''
  };
  if (!scene) { console.log(out); return out; }

  var all = [], seen = new Set();
  (function walk(node, depth) {
    if (!node || depth > 40 || seen.has(node)) return;
    seen.add(node);
    var cs = [];
    try { cs = node.getComponents ? (node.getComponents(cc.Component) || []) : (node.components || []); } catch (e) {}
    for (var i = 0; i < cs.length; i++) if (cs[i]) all.push({ c: cs[i], n: node, cn: cname(cs[i]) });
    (node.children || []).forEach(function (k) { walk(k, depth + 1); });
  })(scene, 0);

  function pick(obj, keys) {
    var r = {};
    keys.forEach(function (k) {
      if (obj && (k in obj)) {
        r[k] = safe(function () {
          var v = obj[k];
          return (v && typeof v === 'object') ? ('<' + (v.node ? v.node.name : (v.constructor && v.constructor.name)) + '>') : v;
        });
      }
    });
    return r;
  }

  for (var i = 0; i < all.length; i++) {
    var c = all[i].c, cn = all[i].cn, node = all[i].n;
    out.components[cn] = (out.components[cn] || 0) + 1;

    // Bat ky component nao giu gameID -> ung vien gid cua sanh
    ['gameID', 'gameId', 'tableGameID', 'game_id'].forEach(function (k) {
      if (c && (k in c)) out.gameIdHolders[cn + '.' + k] = safe(function () { return c[k]; });
    });

    // Liet ke component lien quan table/room/lobby + gameID/keys
    if (/table|room|lobby|list|item|hall|sanh/i.test(cn)) {
      var o = { cls: cn, node: node.name, gameID: safe(function () { return c.gameID; }) };
      if (c && (c.gameID === undefined)) o.gameID = safe(function () { return c.gameId; });
      o.hasJoin = safe(function () { return typeof c.onJoinRoom === 'function'; });
      o.hasQuick = safe(function () { return typeof c.onQuickPlayWithBet === 'function'; });
      if (o.gameID !== undefined || o.hasJoin || o.hasQuick) out.tableish.push(o);
    }

    if (cn === 'TableListView') {
      out.tableListView = {
        node: node.name,
        props: pick(c, ['gameID', 'gameId', 'bet', 'betList', 'bets', 'bet_mapping', 'bet_mapping_2',
                        'bet_position_mapping_1', 'bet_position_mapping_2', 'curBet', 'current_bet_index',
                        'selectBetIndex', 'solo_mode', 'tog_solo_mode']),
        keys: safe(function () { return Object.keys(c); }, []),
        methods: safe(function () {
          return Object.getOwnPropertyNames(Object.getPrototypeOf(c)).filter(function (k) { return typeof c[k] === 'function'; });
        }, [])
      };
      ['getPooledItem', 'onQuickPlay', 'onQuickPlayWithBet', 'quickPlay', 'onJoinRoom', 'showWithGame', 'createRoom'].forEach(function (m) {
        if (typeof c[m] === 'function') out.sources['TableListView.' + m] = src(c[m]);
      });
    }

    if (cn === 'TableItemView') {
      out.items.push({
        node: node.name,
        active: safe(function () { return node.active; }),
        fields: pick(c, ['roomID', 'roomId', 'serverID', 'serverId', 'bet', 'maxUser', 'numPlayer', 'num_player',
                         'hasPass', 'gameID', 'gameId', 'soBan', 'password', 'hostName', 'userCount']),
        numPlayer: safe(function () { return (typeof c.getNumPlayer === 'function') ? c.getNumPlayer() : c.numPlayer; }),
        keys: safe(function () { return Object.keys(c); }, []),
        methods: safe(function () {
          return Object.getOwnPropertyNames(Object.getPrototypeOf(c)).filter(function (k) { return typeof c[k] === 'function'; });
        }, [])
      });
      ['onQuickPlayWithBet', 'onJoinRoom', 'onBookRoom', 'onCreateRoom', 'show'].forEach(function (m) {
        if (typeof c[m] === 'function' && !out.sources['TableItemView.' + m]) out.sources['TableItemView.' + m] = src(c[m]);
      });
    }
  }
  out.tableish = out.tableish.slice(0, 60);
  out.items = out.items.slice(0, 80);

  if (!out.tableListView) {
    out.hint = "Chua o trong sanh ban (tableListView=null). Hay vao SANH cua game (man danh sach ban) " +
               "roi chay lai. Xem 'tableish' de doan ten component dung.";
  } else {
    out.hint = "tableListView.props.gameID = " + JSON.stringify(
      (out.tableListView.props || {}).gameID) + "  <-- day la gid can dien.";
  }

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] QUICK-JOIN probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunQuickJoin = out;
  return out;
})();
