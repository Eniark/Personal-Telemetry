import { TabTracker } from "./TabTracker.js"
import { BROWSER_FOCUS_POOLING_MS, DEBUG } from "./config.js";
const tabTracker = new TabTracker()

setInterval(checkBrowserFocus, BROWSER_FOCUS_POOLING_MS); // detects when browser gets unfocused

chrome.runtime.onStartup.addListener(async () => {
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
    if (DEBUG) console.log("onActivated");

    tabTracker.registerTab(activeInfo.tabId);
    
});

//
// URL CHANGE IN SAME TAB
//
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo) => {

    if (changeInfo.status !== "complete") return;

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });
    
    if (tabs[0]?.id === tabId) {
        tabTracker.registerTab(tabId);
    }
});

//
// WINDOW FOCUS
//
chrome.windows.onFocusChanged.addListener(async (windowId) => {
    if (windowId === -1) {
        return
    }
    if (DEBUG) console.log(`onFocusChanged: Focus is back.`);
    
    if (tabTracker.currentTab) 
        tabTracker.registerTab(tabTracker.currentTab.id, false);
    tabTracker.userTracked = true;
});

async function checkBrowserFocus(){
    let browser = await chrome.windows.getCurrent();
    if (!browser.focused && tabTracker.userTracked) {
        if (DEBUG) console.log("Browser lost focus.");
        tabTracker.saveCurrentSession(tabTracker.currentTab);
        tabTracker.userTracked = false;
      
    }
}