/* ============================================================================
 * Sunwin TLMN - Probe tao/vao ban (CreateTablePopup / JoinTablePopup)
 * Chay trong DevTools Console (context top) khi DANG O SANH BAN TLMN.
 * Ket qua copy vao clipboard -> dan lai cho toi.
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
  var out = { scene: scene && scene.name, found: {} };
  if (!scene) { out.err = 'no scene'; console.log(out); return out; }

  var seen = new Set(), all = [];
  function walk(node, depth) {
    if (!node || depth > 40 || seen.has(node)) return;
    seen.add(node);
    var comps = [];
    try { comps = node.getComponents ? (node.getComponents(cc.Component) || []) : (node.components || []); } catch (e) {}
    for (var i = 0; i < comps.length; i++) { if (comps[i]) all.push({ node: node, c: comps[i], cn: cname(comps[i]) }); }
    var kids = node.children || [];
    for (var k = 0; k < kids.length; k++) walk(kids[k], depth + 1);
  }
  walk(scene, 0);

  function describe(entry) {
    var c = entry.c, node = entry.node;
    var o = { node: node.name, cls: entry.cn, active: safe(function () { return node.active; }), keys: safe(function () { return Object.keys(c); }, []) };
    o.methods = safe(function () { return Object.getOwnPropertyNames(Object.getPrototypeOf(c)).filter(function (k) { return typeof c[k] === 'function'; }); }, []);
    o.props = {};

    // thu thap cac field co the quan trong
    ['bet', 'betList', 'betIndex', 'bets', 'curBet', 'selectBetIndex', 'gameId', 'gameID', 'soNguoi', 'numPlayer', 'maxUser', 'moneyBuyIn', 'buyIn', 'soBan', 'password', 'pass', 'soBanInput', 'editBoxBet', 'editBoxPass', 'toggle'].forEach(function (k) {
      if (k in c) o.props[k] = safe(function () { var v = c[k]; return (v && typeof v === 'object') ? ('<' + (v.node ? v.node.name : (v.constructor && v.constructor.name)) + '>') : v; });
    });

    // node con: label / editbox / toggle / button
    o.subtree = [];
    (function rec(n, d) {
      if (!n || d > 12) return;
      var cs = [];
      try { cs = n.getComponents ? (n.getComponents(cc.Component) || []) : (n.components || []); } catch (e) {}
      for (var j = 0; j < cs.length; j++) {
        var x = cs[j], xn = cname(x);
        if (xn === 'cc.Label') o.subtree.push({ node: n.name, t: 'Label', s: safe(function () { return x.string; }) });
        else if (xn === 'cc.EditBox') o.subtree.push({ node: n.name, t: 'EditBox', s: safe(function () { return x.string; }), ph: safe(function () { return x.placeholder; }) });
        else if (xn === 'cc.Toggle') o.subtree.push({ node: n.name, t: 'Toggle', isOn: safe(function () { return x.isChecked; }) });
        else if (xn === 'cc.Button') o.subtree.push({ node: n.name, t: 'Button' });
      }
      (n.children || []).forEach(function (k) { rec(k, d + 1); });
    })(node, 0);
    o.subtree = o.subtree.slice(0, 60);
    return o;
  }

  ['CreateTablePopup', 'JoinTablePopup', 'TableListView', 'TableViewController', 'AloneBookRoomView'].forEach(function (name) {
    var e = null;
    for (var i = 0; i < all.length; i++) { if (all[i].cn === name) { e = all[i]; break; } }
    out.found[name] = e ? describe(e) : null;
  });

  var txt = JSON.stringify(out, null, 2);
  console.group('%c[SUN] create/join popup probe', 'color:#f0c040;font-weight:bold');
  console.log(out);
  console.groupEnd();
  try { copy(txt); } catch (e) {}
  window.__sunCreateProbe = out;
  return out;
})();
