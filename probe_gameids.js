/* ============================================================================
 * Sunwin - Probe GAME-ID (danh sach game o SANH CHON GAME)
 * Chay trong DevTools Console (context top) KHI DANG O SANH CHON GAME.
 *
 * Muc dich: liet ke TAT CA o game (Tiến Lên, Sâm Lốc, ...) kem gameID tuong ung.
 *   -> Tim dong co ten "Sâm Lốc" => do chinh la gid can dung.
 * Kiem chung: dong "Tiến Lên Miền Nam" phai ra gameID = 1.
 *
 * Ket qua: in bang (console.table) + JSON + copy clipboard.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) {
    try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {}
    try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; }
  }

  var scene = safe(function () { return cc.director.getScene(); }, null);
  var out = { scene: scene && scene.name, games: [], lobbyKeys: [], lobbyProps: {} };
  if (!scene) { console.log(out); return out; }

  var all = [], seen = new Set();
  (function walk(n, d) {
    if (!n || d > 40 || seen.has(n)) return; seen.add(n);
    var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {}
    for (var i = 0; i < cs.length; i++) if (cs[i]) all.push({ c: cs[i], n: n, cn: cname(cs[i]) });
    (n.children || []).forEach(function (k) { walk(k, d + 1); });
  })(scene, 0);

  function labelsOf(node, maxDepth) {
    var res = [];
    (function rec(n, d) {
      if (!n || d > maxDepth) return;
      var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {}
      for (var i = 0; i < cs.length; i++) {
        if (cname(cs[i]) === 'cc.Label') {
          var s = safe(function () { return cs[i].string; });
          if (s) res.push(String(s).trim());
        }
      }
      (n.children || []).forEach(function (k) { rec(k, d + 1); });
    })(node, 0);
    var u = []; res.forEach(function (s) { if (s && u.indexOf(s) < 0) u.push(s); });
    return u;
  }

  for (var i = 0; i < all.length; i++) {
    var e = all[i], c = e.c;
    var gid = safe(function () {
      if (c.gameID !== undefined) return c.gameID;
      if (c.gameId !== undefined) return c.gameId;
      return undefined;
    });
    if (typeof gid === 'number' || typeof gid === 'string') {
      var labels = labelsOf(e.n, 6);
      if (!labels.length && e.n.parent) labels = labelsOf(e.n.parent, 4);
      out.games.push({ gameID: gid, cls: e.cn, node: e.n.name, labels: labels.slice(0, 6) });
    }
    if (e.cn === 'LobbyViewController') {
      out.lobbyKeys = safe(function () { return Object.keys(c); }, []);
      ['gameID', 'gameId', 'gameList', 'listGame', 'games', 'lstGame', 'allGame', 'config'].forEach(function (k) {
        if (k in c) out.lobbyProps[k] = safe(function () {
          var v = c[k];
          if (v && v.length !== undefined) return '<len ' + v.length + '>';
          return (v && typeof v === 'object') ? '<obj>' : v;
        });
      });
    }
  }
  out.games.sort(function (a, b) { return (a.gameID > b.gameID) ? 1 : (a.gameID < b.gameID ? -1 : 0); });

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] GAME-ID probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  try {
    console.table(out.games.map(function (g) {
      return { gameID: g.gameID, cls: g.cls, node: g.node, ten: (g.labels || []).join(' | ') };
    }));
  } catch (e) {}
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunGameIds = out;
  console.log('%cTim dong ten "Sâm Lốc" -> gameID cua no la gid can dien.', 'color:#22c55e;font-weight:bold');
  return out;
})();
