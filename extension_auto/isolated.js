(function () {
    'use strict';
    if (window !== window.top) return;
    if (!/sunwin/i.test(location.hostname || '')) return;

    let latestData = { ok: false, remain: 0, cards: [], player: null };
    let isConnected = false;
    let isConnecting = false;
    let wasHalt = false;

    function getControlId() {
        try {
            let id = sessionStorage.getItem('sw_ctrl_id');
            if (!id) {
                id = 'sw-' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
                sessionStorage.setItem('sw_ctrl_id', id);
            }
            return id;
        } catch (e) {
            return 'sw-' + Math.random().toString(36).slice(2, 12);
        }
    }

    function sendToInject(type, payload) {
        window.postMessage(Object.assign({ __cardHook: true, type: type }, payload || {}), '*');
    }

    function setArmed(armed) {
        isConnected = !!armed;
        sendToInject(isConnected ? 'ARM' : 'DISARM');
        updateButton();
    }

    function ensureStyle() {
        let style = document.getElementById('sw-connect-style');
        if (!style) {
            style = document.createElement('style');
            style.id = 'sw-connect-style';
            (document.head || document.documentElement).appendChild(style);
        }
        if (style.dataset.sw === 'v3') return;
        style.dataset.sw = 'v3';
        style.textContent = `
            #sw-connect-btn {
                position: fixed !important;
                left: 12px !important;
                bottom: 12px !important;
                z-index: 2147483647 !important;
                pointer-events: auto !important;
                cursor: pointer !important;
                box-sizing: border-box !important;
                padding: 6px 14px !important;
                border-radius: 6px !important;
                font: bold 12px / 1.2 "Segoe UI", Arial, sans-serif !important;
                border: 2px solid #f0c040 !important;
                background: #0b1220 !important;
                color: #f0c040 !important;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.7) !important;
                transition: all 0.2s ease !important;
            }
            #sw-connect-btn:hover {
                transform: scale(1.05) !important;
            }
            #sw-connect-btn.on {
                background: #14532d !important;
                color: #86efac !important;
                border-color: #4ade80 !important;
            }
            #sw-connect-btn.wait {
                opacity: 0.75 !important;
                border-color: #94a3b8 !important;
                color: #94a3b8 !important;
            }
        `;
    }

    function updateButton() {
        ensureStyle();
        let btn = document.getElementById('sw-connect-btn');
        if (!btn) {
            btn = document.createElement('button');
            btn.id = 'sw-connect-btn';
            btn.type = 'button';
            btn.addEventListener('click', toggleConnect);
            (document.documentElement || document.body).appendChild(btn);
        }
        btn.className = isConnected ? 'on' : isConnecting ? 'wait' : '';
        btn.textContent = isConnecting ? '⏳ Đang kết nối…' : isConnected ? '✅ TOOL ĐÃ KẾT NỐI (Bấm ngắt)' : '⚡ KẾT NỐI TOOL';
    }

    function requestControl(path, body) {
        return new Promise((resolve, reject) => {
            // Priority 1: Send via background script (Bypasses HTTPS Mixed Content & PNA)
            try {
                chrome.runtime.sendMessage({
                    type: 'HTTP_PROXY',
                    path: path,
                    method: body ? 'POST' : 'GET',
                    body: body
                }, (res) => {
                    if (chrome.runtime.lastError || !res) {
                        directFetch(path, body).then(resolve).catch(reject);
                    } else if (res.ok) {
                        resolve(res.data);
                    } else {
                        reject(new Error(res.error || ('HTTP ' + res.status)));
                    }
                });
            } catch (err) {
                directFetch(path, body).then(resolve).catch(reject);
            }
        });
    }

    function directFetch(path, body) {
        const opts = {
            method: body ? 'POST' : 'GET',
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) opts.body = JSON.stringify(body);
        return fetch('http://127.0.0.1:17831' + path, opts)
            .then(res => {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json().catch(() => ({ ok: true }));
            });
    }

    function toggleConnect() {
        if (isConnecting) return;
        isConnecting = true;
        updateButton();

        const path = isConnected ? '/disconnect' : '/connect';
        const payload = isConnected ? { id: getControlId() } : { id: getControlId(), host: location.host };

        requestControl(path, payload)
            .then(() => {
                setArmed(!isConnected);
            })
            .catch((err) => {
                console.warn('[SW Control] Connect error:', err);
                setArmed(false);
                sendToInject('DISARM');
            })
            .finally(() => {
                isConnecting = false;
                updateButton();
            });
    }

    // Polling /state every 800ms when connected
    setInterval(() => {
        if (!isConnected) return;
        sendToInject('ARM');

        const huntFound = !!latestData.huntFound;
        const foundRoom = latestData.foundRoom;

        const statePayload = {
            id: getControlId(),
            host: location.host,
            player: latestData.player,
            remain: latestData.remain,
            cards: latestData.cards,
            dbg: latestData.dbg || null,
            huntFound: huntFound,
            soBan: foundRoom && foundRoom.soBan,
            roomId: foundRoom && foundRoom.roomId,
            serverId: foundRoom && foundRoom.serverId,
            bet: foundRoom && foundRoom.bet,
            hostName: (foundRoom && foundRoom.hostName) || (latestData.player && latestData.player.name) || ''
        };

        requestControl('/state', statePayload)
            .then((res) => {
                if (huntFound && latestData.foundRoom === foundRoom) {
                    latestData.huntFound = false;
                    latestData.foundRoom = null;
                }

                if (res && Array.isArray(res.knownNames)) {
                    sendToInject('TEAM', { names: res.knownNames });
                }

                sendToInject('XA_CFG', {
                    delay: res && res.xaDelay != null ? res.xaDelay : 1000,
                    chongPha: !!(res && res.chongPha),
                    outGuest: !!(res && res.outGuest)
                });

                if (res && res.halt) {
                    if (!wasHalt) { sendToInject('LEAVE'); wasHalt = true; }
                    window.postMessage({ __cardHook: true, type: 'HALT' }, '*');
                } else {
                    wasHalt = false;
                    if (res && res.hunt) {
                        sendToInject('HUNT_START', {
                            mode: res.mode || 'create',
                            bet: res.bet || 100,
                            names: res.knownNames || [],
                            roomPass: (res && res.roomPass) || '',
                            sharedRoom: res.mode === 'join' ? (res.sharedRoom || null) : null
                        });
                    } else {
                        sendToInject('HUNT_STOP');
                    }
                }
            })
            .catch(() => {
                setArmed(false);
                sendToInject('DISARM');
            });
    }, 800);

    // Listen from inject.js
    window.addEventListener('message', (ev) => {
        const data = ev.data;
        if (!data || !data.__cardHook) return;

        if (data.type === 'STATE') {
            latestData = {
                ok: true,
                remain: data.remain || 0,
                cards: data.cards || [],
                player: data.player || null,
                dbg: data.dbg || null,
                huntFound: latestData.huntFound || false,
                foundRoom: latestData.foundRoom || null
            };
            try {
                chrome.runtime.sendMessage({
                    type: 'SNAPSHOT',
                    cards: latestData.cards,
                    remain: latestData.remain,
                    player: latestData.player
                }).catch(() => {});
            } catch (e) {}
        } else if (data.type === 'HUNT_FOUND') {
            latestData.huntFound = true;
            latestData.foundRoom = data.room || latestData.foundRoom;
        } else if (data.type === 'SNIFF') {
            requestControl('/sniff', { id: getControlId(), dir: data.dir, url: data.url, len: data.len, data: data.data, t: data.t }).catch(function () {});
        }
    });

    // Listen from popup.js
    chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
        if (req && req.type === 'GET_STATE') {
            sendResponse(latestData);
            return false;
        }
        return false;
    });

    // Init button & auto-connect
    function init() {
        updateButton();
        // Tự động kết nối sau 1.5s nếu App Control đang bật
        setTimeout(() => {
            if (!isConnected && !isConnecting) {
                toggleConnect();
            }
        }, 1500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    setInterval(updateButton, 2000);
})();