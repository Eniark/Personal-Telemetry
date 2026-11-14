import { Tab } from "./Tab.js"
import { DEBUG, API_ADDRESS } from "./configs.js";

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.userTracked = true;
    }

    async saveCurrentSession(tab) {
        if (!this.userTracked || !tab) return;
 
        try {
            const res = await fetch(`${API_ADDRESS}/browser_event`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: tab.url,
                    title: tab.title,
                    eventStartTime: tab.eventStartTime,
                    eventEndTime: Date.now()
                })
            });
            

            if (!res.ok) throw new Error("Save failed");

            if (DEBUG) console.log("Saved:", tab.url);
        
        } catch (err) {
            if (DEBUG) console.error("Save failed", err);
        }

        
    }

    async registerTab(tabId, save=true) {
        try {
            const tab = await chrome.tabs.get(tabId);
            this.previousTab = this.currentTab
            this.currentTab = new Tab(tab.id, tab.url, tab.title, Date.now())
            this.userTracked = true;
        }
        catch {
            this.currentTab = null;
            this.userTracked = false;
        }
        
        if (save) {
            await this.saveCurrentSession(this.previousTab);
        }

    }
}
