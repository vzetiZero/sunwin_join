/* ============================================================================
 * Sunwin TLMN - Probe so ban (chay tren ACC1 dang ngoi trong ban)
 * DevTools Console (context top) -> dan -> Enter. Ket qua copy clipboard.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) { try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {} try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; } }
  var out = { scene: null, gameView: null, lbl_info: null, tableNumbers: [], labels: [] };
  var scene = safe(function () { return cc.director.getScene(); }, null);
  out.scene = scene && scene.name;
  if (!scene) { console.log(out); return out; }

  var seen = new Set(), all = [];
  (function walk(n, d) { if (!n || d > 40 || seen.has(n)) return; seen.add(n); var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {} cs.forEach(function (c) { if (c) all.push({ c: c, n: n, cn: cname(c) }); }); (n.children || []).forEach(function (k) { walk(k, d + 1); }); })(scene, 0);

  for (var i = 0; i < all.length; i++) {
    var e = all[i];
    if (e.cn === 'TienLenFullScreenGameView' || (e.c.btn_danhbai && e.c.my_info)) {
      out.gameView = { cls: e.cn, keys: safe(function () { return Object.keys(e.c); }, []) };
      out.lbl_info = safe(function () { return e.c.lbl_info && e.c.lbl_info.string; }, null);
    }
    if (e.cn === 'cc.Label' && typeof e.c.string === 'string') {
      var s = e.c.string;
      if (/B\u00e0n/i.test(s)) out.labels.push(e.n.name + ' = ' + s);
      if (/^[0-9A-Za-z]{2,7}$/.test(s.trim())) out.tableNumbers.push(e.n.name + ' = ' + s);
    }
  }
  out.labels = out.labels.slice(0, 40);
  out.tableNumbers = out.tableNumbers.slice(0, 40);

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] room number probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunRoomProbe = out;
  return out;
})();
