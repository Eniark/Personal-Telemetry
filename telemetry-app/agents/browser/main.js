import { TabTracker } from "./TabTracker.js"

const tabTracker = new TabTracker()

setInterval(checkBrowserFocus, 4000); // detects when browser gets unfocused

chrome.runtime.onStartup.addListener(async () => {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    if (tabs.length) {
        tabTracker.registerTab(tabs[0].id);
    }
});

chrome.runtime.onInstalled.addListener(async () => {
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
    tabTracker.userTracked = true
});

async function checkBrowserFocus(){
    let browser = await chrome.windows.getCurrent()
    if (!browser.focused && tabTracker.userTracked) {
        console.log("Browser lost focus.")
        tabTracker.userTracked = false
        tabTracker.currentTab = null;
    }
}
