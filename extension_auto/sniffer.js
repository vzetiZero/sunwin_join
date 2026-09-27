/* ============================================================================
 * Sunwin - WebSocket sniffer (thu protocol thuc te)
 * Chay o MAIN world, document_start, TRUOC inject.js.
 * Hook WebSocket.send / message -> postMessage 'SNIFF' sang isolated.js
 * ==========================================================================*/
(function () {
    'use strict';
    try {
        var Native = window.WebSocket;
        if (!Native || Native.__swSniff) return;
        window.__swSniffReady = true;

        var MAX_FRAMES = 1500;
        var sent = 0;
        function report(rec) {
            if (sent >= MAX_FRAMES) return;
            sent++;
            try { window.postMessage(Object.assign({ __cardHook: true, type: 'SNIFF' }, rec), '*'); } catch (e) {}
        }
        function b64(u8, n) {
            var s = '';
            for (var i = 0; i < n; i++) s += String.fromCharCode(u8[i]);
            try { return btoa(s); } catch (e) { return ''; }
        }
        function enc(d) {
            try {
                if (typeof d === 'string') return (d.length > 1200 ? d.slice(0, 1200) + '…' : d);
                if (d instanceof ArrayBuffer) { var u = new Uint8Array(d); return 'BIN len=' + u.length + ' b64=' + b64(u, Math.min(u.length, 400)); }
                if (window.ArrayBuffer && ArrayBuffer.isView && ArrayBuffer.isView(d)) { var v = new Uint8Array(d.buffer); return 'VIEW len=' + v.length + ' b64=' + b64(v, Math.min(v.length, 400)); }
                if (d && d.byteLength != null) { var u2 = new Uint8Array(d); return 'BIN len=' + u2.length + ' b64=' + b64(u2, Math.min(u2.length, 400)); }
                if (typeof Blob !== 'undefined' && d instanceof Blob) return 'BLOB size=' + d.size + ' type=' + d.type;
                return String(d).slice(0, 1200);
            } catch (e) { return '<enc-err ' + e.message + '>'; }
        }
        function tidy(text) {
            if (typeof text !== 'string') return true;
            if (text === '2' || text === '3') return false; // engine.io ping/pong
            return true;
        }

        function Wrap(url, protocols) {
            var ws = protocols !== undefined ? new Native(url, protocols) : new Native(url);
            try {
                var origSend = ws.send;
                ws.send = function (data) {
                    try { var t = enc(data); if (tidy(t)) report({ dir: 'out', url: String(url), len: (data && data.byteLength) || (data && data.length) || 0, data: t, t: Date.now() }); } catch (e) {}
                    return origSend.apply(ws, arguments);
                };
                ws.addEventListener('message', function (ev) {
                    try { var t = enc(ev.data); if (tidy(t)) report({ dir: 'in', url: String(url), len: (ev.data && ev.data.byteLength) || (ev.data && ev.data.length) || 0, data: t, t: Date.now() }); } catch (e) {}
                });
                ws.addEventListener('open', function () { report({ dir: 'open', url: String(url), data: 'OPEN', t: Date.now() }); });
                ws.addEventListener('close', function () { report({ dir: 'close', url: String(url), data: 'CLOSE', t: Date.now() }); });
            } catch (e) {}
            return ws;
        }
        Wrap.prototype = Native.prototype;
        Wrap.CONNECTING = 0; Wrap.OPEN = 1; Wrap.CLOSING = 2; Wrap.CLOSED = 3;
        Wrap.__swSniff = true;
        window.WebSocket = Wrap;
    } catch (e) {}
})();
