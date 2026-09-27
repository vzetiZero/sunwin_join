/* ============================================================================
 * Sunwin TLMN - Probe #3: id phong that + source ham join cua TableItemView
 * Chay o Console (top). O trong ban (acc1) -> doc field phong; o sanh (acc2)
 * -> liet ke cac ban trong list + source ham join. Ket qua copy clipboard.
 * ==========================================================================*/
(function () {
  'use strict';
  var cc = window.cc;
  function safe(f, d) { try { return f(); } catch (e) { return (d !== undefined ? d : ('<err:' + (e && e.message) + '>')); } }
  function cname(c) { try { if (cc && cc.js && cc.js.getClassName) { var n = cc.js.getClassName(c); if (n) return n; } } catch (e) {} try { return (c && c.constructor && c.constructor.name) || ''; } catch (e) { return ''; } }
  var scene = safe(function () { return cc.director.getScene(); }, null);
  var out = { scene: scene && scene.name, gameView: null, lobbyItems: [], fnSrc: {} };
  if (!scene) { console.log(out); return out; }
  var seen = new Set(), all = [];
  (function walk(n, d) { if (!n || d > 40 || seen.has(n)) return; seen.add(n); var cs = []; try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {} cs.forEach(function (c) { if (c) all.push({ c: c, n: n, cn: cname(c) }); }); (n.children || []).forEach(function (k) { walk(k, d + 1); }); })(scene, 0);

  for (var i = 0; i < all.length; i++) {
    var e = all[i];
    if (!out.gameView && (e.cn === 'TienLenFullScreenGameView' || (e.c.btn_danhbai && e.c.my_info))) {
      var g = e.c, o = { keys: safe(function () { return Object.keys(g); }, []) };
      ['roomID', 'roomId', 'serverID', 'serverId', 'gameID', 'gameId', 'soBan', 'roomNo', 'tableID', 'tableId', 'roomNumber', 'serverCode', 'roomPassword'].forEach(function (k) {
        if (k in g) o[k] = safe(function () { return g[k]; });
      });
      o.lbl_info = safe(function () { return g.lbl_info && g.lbl_info.string; });
      out.gameView = o;
    }
    if (e.cn === 'TableItemView') {
      out.lobbyItems.push({
        node: e.n.name, active: safe(function () { return e.n.active; }),
        roomID: safe(function () { return e.c.roomID; }), serverID: safe(function () { return e.c.serverID; }),
        bet: safe(function () { return e.c.bet; }), maxUser: safe(function () { return e.c.maxUser; }),
        hasPass: safe(function () { return e.c.hasPass; }), gameID: safe(function () { return e.c.gameID; })
      });
      if (!out.fnSrc.onJoinRoom) {
        out.fnSrc.onJoinRoom = safe(function () { return String(e.c.onJoinRoom); });
        out.fnSrc.onBookRoom = safe(function () { return String(e.c.onBookRoom); });
      }
    }
  }
  out.lobbyItems = out.lobbyItems.slice(0, 40);
  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] room id / join source probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunRoom3 = out;
  return out;
})();
