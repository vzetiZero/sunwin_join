const tabState = {};

chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) {
    if (msg && msg.type === 'HTTP_PROXY') {
        const url = 'http://127.0.0.1:17831' + msg.path;
        fetch(url, {
            method: msg.method || 'GET',
            headers: { 'Content-Type': 'application/json' },
            body: msg.body ? JSON.stringify(msg.body) : undefined
        })
        .then(async (res) => {
            const data = await res.json().catch(() => ({ ok: res.ok }));
            sendResponse({ ok: res.ok, status: res.status, data: data });
        })
        .catch((err) => {
            sendResponse({ ok: false, error: err.message });
        });
        return true; // asynchronous response
    }

    const tabId = sender && sender.tab ? sender.tab.id : null;
    if (!tabId || !msg) return false;
    if (msg.type === 'SNAPSHOT') {
        tabState[tabId] = {
            cards: msg.cards || [],
            remain: msg.remain,
            player: msg.player || null
        };
        sendResponse({ ok: true });
        return true;
    }
    return false;
});

chrome.tabs.onRemoved.addListener(function(tabId) {
    delete tabState[tabId];
});