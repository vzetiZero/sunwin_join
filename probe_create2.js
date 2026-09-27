/* ============================================================================
 * Sunwin TLMN - Probe #2: doc source ham tao/vao ban + mapping muc cuoc
 * Chay trong DevTools Console (context top) khi DANG O SANH BAN TLMN.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) { try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {} try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; } }

  var scene = cc.director.getScene();
  var all = [], seen = new Set();
  (function walk(n, d) { if (!n || d > 40 || seen.has(n)) return; seen.add(n); var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {} cs.forEach(function (c) { if (c) all.push({ c: c, cn: cname(c) }); }); (n.children || []).forEach(function (k) { walk(k, d + 1); }); })(scene, 0);
  function find(name) { for (var i = 0; i < all.length; i++) if (all[i].cn === name) return all[i].c; return null; }

  function src(fn) { return safe(function () { return String(fn); }, '').slice(0, 2500); }

  var pop = find('CreateTablePopup');
  var jp = find('JoinTablePopup');
  var out = { createBefore: {}, createAfter: {}, fn: {}, join: {} };

  function snap() {
    if (!pop) return null;
    var r = {};
    ['bet', 'current_bet_index', 'gameId'].forEach(function (k) { r[k] = safe(function () { return pop[k]; }); });
    ['bet_mapping', 'bet_mapping_2', 'bet_position_mapping_1', 'bet_position_mapping_2'].forEach(function (k) { r[k] = safe(function () { return JSON.stringify(pop[k]); }); });
    ['tog_9', 'tog_50', 'tog_1', 'tog_2'].forEach(function (k) { r[k] = safe(function () { return pop[k] && pop[k].isChecked; }); });
    return r;
  }

  out.createBefore = snap();
  safe(function () { if (pop && pop.showWithGame) pop.showWithGame(1); });
  out.createAfter = snap();

  if (pop) {
    out.fn.taoBan = src(pop.taoBan);
    out.fn.selectBet = src(pop.selectBet);
    out.fn.showWithGame = src(pop.showWithGame);
    out.fn.betNode2focusToIndex = src(pop.betNode2focusToIndex);
    // dong popup lai cho an toan
    safe(function () { if (pop.onCancel) pop.onCancel(); else if (pop.hide) pop.hide(); });
  }
  if (jp) {
    out.join.vaoBan = src(jp.vaoBan);
    out.join.setSoBan = src(jp.setSoBan);
    out.join.showWithGame = src(jp.showWithGame);
  }

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] create/join source probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunCreate2 = out;
  return out;
})();
