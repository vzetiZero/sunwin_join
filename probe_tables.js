/* ============================================================================
 * Sunwin TLMN - Lobby/Table probe (chẩn đoán)
 * Chạy trong DevTools Console (context top / main world) khi ĐANG Ở SẢNH BÀN TLMN.
 * Mục đích: tìm cách (a) tạo bàn TRỐNG, (b) nhận biết TableItemView đang trống.
 * Kết quả in ra console + copy vào clipboard. Dán lại cho tôi.
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
  var out = { scene: scene && scene.name, components: {}, tableItems: [], roomish: [], labels: [] };
  if (!scene) { out.err = 'khong co scene'; console.log(JSON.stringify(out)); return out; }

  var seen = new Set();
  function walk(node, depth) {
    if (!node || depth > 40 || seen.has(node)) return;
    seen.add(node);
    var comps = [];
    try { comps = node.getComponents ? (node.getComponents(cc.Component) || []) : (node.components || []); } catch (e) {}
    for (var i = 0; i < comps.length; i++) {
      var c = comps[i]; if (!c) continue;
      var cn = cname(c);
      out.components[cn] = (out.components[cn] || 0) + 1;

      if (/room|table|creat|join|tao|ban|quickplay/i.test(cn)) {
        out.roomish.push({
          cls: cn,
          node: node.name,
          methods: safe(function () {
            var p = Object.getOwnPropertyNames(Object.getPrototypeOf(c));
            return p.filter(function (k) { return typeof c[k] === 'function'; }).slice(0, 60);
          }, []),
          props: safe(function () {
            var r = {}; Object.keys(c).slice(0, 40).forEach(function (k) { var v = c[k]; if (typeof v !== 'object' && typeof v !== 'function') r[k] = v; });
            return r;
          }, {})
        });
      }

      if (cn === 'TableItemView') {
        out.tableItems.push({
          node: node.name,
          keys: safe(function () { return Object.keys(c); }, []),
          props: safe(function () {
            var r = {};
            Object.keys(c).forEach(function (k) {
              var v = c[k];
              if (v === null || typeof v === 'boolean' || typeof v === 'number' || typeof v === 'string') r[k] = v;
            });
            return r;
          }, {}),
          methods: safe(function () {
            var p = Object.getOwnPropertyNames(Object.getPrototypeOf(c));
            return p.filter(function (k) { return typeof c[k] === 'function'; });
          }, []),
          nodeChildren: safe(function () { return (node.children || []).map(function (k) { return k.name; }); }, []),
          bet: safe(function () { return c.bet; }),
          maxUser: safe(function () { return c.maxUser; }),
          numPlayer: safe(function () { return (typeof c.getNumPlayer === 'function') ? c.getNumPlayer() : c.numPlayer; }),
          active: safe(function () { return node.active; })
        });
      }

      // thu thập text của các Label để xem hiển thị số người / tên chủ bàn
      if (typeof c.string === 'string' && c.string) {
        out.labels.push(node.name + ' = ' + c.string);
      }
    }
    var kids = node.children || [];
    for (var k = 0; k < kids.length; k++) walk(kids[k], depth + 1);
  }
  walk(scene, 0);

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] Lobby/Table probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunLobbyProbe = out;
  return out;
})();
