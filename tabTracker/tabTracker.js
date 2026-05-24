let currentTab = null;
let startTime = null;
let browserFocused = true;
let userIdle = false;

async function saveCurrentSession() {

    if (!currentTab || !startTime) return;
    if (!browserFocused || userIdle) return;

    const duration = Date.now() - startTime;

    if (duration <= 0) return;

    const result = await chrome.storage.local.get("usage");
    const usage = result.usage || {};

    usage[currentTab] = (usage[currentTab] || 0) + duration;

    await chrome.storage.local.set({ usage });

    console.log(
        "Saved:",
        currentTab,
        Math.round(duration / 1000),
        "sec"
    );
}

async function switchToTab(tabId) {

    await saveCurrentSession();

    try {
        const tab = await chrome.tabs.get(tabId);

        currentTab = tab.url;
        startTime = Date.now();

        console.log("Tracking:", currentTab);

    } catch {
        currentTab = null;
    }
}

//
// TAB SWITCH
//
chrome.tabs.onActivated.addListener((activeInfo) => {
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

    await saveCurrentSession();

    browserFocused =
        windowId !== chrome.windows.WINDOW_ID_NONE;

    startTime = Date.now();
});

//
// IDLE DETECTION
//
chrome.idle.setDetectionInterval(60);

chrome.idle.onStateChanged.addListener(async (state) => {

    await saveCurrentSession();

    userIdle = state !== "active";

    startTime = Date.now();
});

//
// INITIAL STARTUP
//
chrome.runtime.onStartup.addListener(async () => {

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        switchToTab(tabs[0].id);
    }
});

chrome.runtime.onInstalled.addListener(async () => {

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        switchToTab(tabs[0].id);
    }
});