import { TabTracker } from "./TabTracker.js"

const tabTracker = new TabTracker()

setInterval(checkBrowserFocus, 4000); // detects when browser gets unfocused


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
        tabTracker.registerTab(tabs[0].id);
    }
});

chrome.runtime.onInstalled.addListener(async () => {
    console.log("onInstalled")

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        tabTracker.registerTab(tabs[0].id);
    }
});

//
// TAB SWITCH
//
chrome.tabs.onActivated.addListener((activeInfo) => {
    console.log("onActivated")

    tabTracker.registerTab(activeInfo.tabId);
    
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
            tabTracker.registerTab(tabId);
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
    console.log(`onFocusChanged: Focus is back.`)
    
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });
    if (tabs[0].id === tabTracker.currentTab.id) {
        tabTracker.registerTab(tabs[0].id, false);
    }
});

async function checkBrowserFocus(){
    let browser = await chrome.windows.getCurrent()
    if (!browser.focused && tabTracker.userTracked) {
        console.log("Browser lost focus. Saved session")
        await tabTracker.saveCurrentSession();
        tabTracker.userTracked = false
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
        await tabTracker.saveCurrentSession();
    }
    else {
        tabTracker.registerTab(tabTracker.currentTab.id); // When user comes back from idle -> same tab will be on the screen
    }
    tabTracker.userTracked = isActive;
});





