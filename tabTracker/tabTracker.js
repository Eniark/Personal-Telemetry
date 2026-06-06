let currentTab = null;
let startTime = null;
let userTracked = true;
setInterval(checkBrowserFocus, 3000); // detects when browser gets unfocused

async function saveCurrentSession() {
    if (!currentTab || !startTime) return;
    if (!userTracked) return;

    const duration = Date.now() - startTime;
    if (duration <= 0) return;

    try {
        const res = await fetch("http://127.0.0.1:8000/event", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                website: currentTab,
                duration_ms: duration,
                started_at: startTime,
                ended_at: Date.now(),
            })
        });

        if (!res.ok) throw new Error("Save failed");

        console.log("Saved:", currentTab, Math.round(duration / 1000), "sec");

    } catch (err) {
        console.error("Save failed", err);
    }
}

async function switchToTab(tabId, save=true) {
    if (save) {
        await saveCurrentSession();
    }
    const tab = await chrome.tabs.get(tabId);

    if (!tab) {
        currentTab = null;
        startTime = null;
        userTracked = false;
    }
    else {
        currentTab = tab.url;
        startTime = Date.now();
        userTracked = true;
    }

    console.log("Tracking:", currentTab);

}

//
// TAB SWITCH
//
chrome.tabs.onActivated.addListener((activeInfo) => {
    console.log("onActivated")
    switchToTab(activeInfo.tabId);
});

//
// URL CHANGE IN SAME TAB
//
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {

    if (changeInfo.status !== "complete") return;

    chrome.tabs.query({
        active: true,
        currentWindow: true
    }, (tabs) => {

        if (tabs[0]?.id === tabId) {
            switchToTab(tabId);
        }
    });
});

//
// WINDOW FOCUS
//
chrome.windows.onFocusChanged.addListener(async (windowId) => {
    if (windowId === -1) {
        return
    }
    console.log(`onFocusChanged: Focus is back. ${windowId}`)
    
    userTracked = true

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    switchToTab(tabs[0].id, save=false);
});

async function checkBrowserFocus(){
    let browser = await chrome.windows.getCurrent()
    if (!browser.focused && userTracked) {
        console.log("Browser lost focus. Saved session")
        await saveCurrentSession();
        userTracked = false
    }
}

//
// IDLE DETECTION
//
chrome.idle.setDetectionInterval(15);

chrome.idle.onStateChanged.addListener(async (state) => {
    console.log("onStateChanged")
    const isActive = state === "active";
    if (!isActive) {
        await saveCurrentSession();
    }
    else {
            const tabs = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        if (tabs.length) {
            switchToTab(tabs[0].id);
        }
    }
    userTracked = isActive;
});

//
// INITIAL STARTUP
//
chrome.runtime.onStartup.addListener(async () => {
    console.log("onStartup")

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        switchToTab(tabs[0].id);
    }
});

chrome.runtime.onInstalled.addListener(async () => {
    console.log("onInstalled")

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        switchToTab(tabs[0].id);
    }
});



