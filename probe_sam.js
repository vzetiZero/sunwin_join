/* ============================================================================
 * Sunwin - Probe SAM (Sâm Lốc)
 * Chay 2 noi:
 *   (1) O SANH bau Sam Loc (scene_tableView, gameID cua Sam)
 *   (2) TRONG BAN Sam Loc (de thay class game view + fields)
 * DevTools Console (context top) -> dan -> Enter. Ket qua copy clipboard.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) { try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {} try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; } }
  var scene = safe(function () { return cc.director.getScene(); }, null);
  var out = { scene: scene && scene.name, counts: {}, games: [], popups: {}, gameView: null, labels: [] };
  if (!scene) { console.log(out); return out; }

  var seen = new Set(), all = [];
  (function walk(n, d) { if (!n || d > 40 || seen.has(n)) return; seen.add(n); var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {} cs.forEach(function (c) { if (!c) return; all.push({ c: c, n: n, cn: cname(c) }); out.counts[cname(c)] = (out.counts[cname(c)] || 0) + 1; }); (n.children || []).forEach(function (k) { walk(k, d + 1); }); })(scene, 0);

  for (var i = 0; i < all.length; i++) {
    var e = all[i], cn = e.cn;
    if (/GameView|FullScreen/i.test(cn)) out.games.push(cn);
    if (cn === 'TableListView' || cn === 'TableViewController' || cn === 'CreateTablePopup' || cn === 'JoinTablePopup') {
      var o = { cls: cn, node: e.n.name, gameID: safe(function () { return e.c.gameID; }), gameId: safe(function () { return e.c.gameId; }) };
      if (cn === 'CreateTablePopup') { o.bet_mapping_2 = safe(function () { return JSON.stringify(e.c.bet_mapping_2); }); o.tog1 = safe(function () { return e.c.tog_1 && e.c.tog_1.isChecked; }); }
      out.popups[cn] = o;
    }
    // game view Sâm: co my_info/opponent_info/btn_danhbai
    if (!out.gameView && (e.c.my_info || e.c.opponent_info || e.c.btn_danhbai)) {
      var g = e.c, go = { cls: cn, node: e.n.name, keys: safe(function () { return Object.keys(g); }, []) };
      go.gameID = safe(function () { return g.gameID; });
      go.lbl_info = safe(function () { return g.lbl_info && g.lbl_info.string; });
      go.my_infoKeys = g.my_info ? safe(function () { return Object.keys(g.my_info); }) : null;
      go.opponentCount = g.opponent_info ? safe(function () { return g.opponent_info.length; }) : null;
      go.hasHand = safe(function () { return typeof g.my_info.getPlayerCard === 'function' ? (g.my_info.getPlayerCard() || []).length : null; });
      out.gameView = go;
    }
    if (cn === 'cc.Label' && typeof e.c.string === 'string' && e.c.string) {
      if (/Bàn|Cược|Sâm|Sẵn sàng|Bắt đầu/i.test(e.c.string)) out.labels.push(e.n.name + ' = ' + e.c.string);
    }
  }
  out.games = Array.from(new Set(out.games));
  out.labels = out.labels.slice(0, 30);
  delete out.counts;

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] SAM probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunSam = out;
  return out;
})();
