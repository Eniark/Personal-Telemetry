import { Tab } from "./Tab.js"

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.userTracked = true;
    }

    async saveCurrentSession(tab) {
        if (!this.userTracked || Object.keys(tab).length === 0) return;
 
        try {
            const res = await fetch("http://127.0.0.1:8080/browser_event", {
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

            console.log("Saved:", tab.url);
        
        } catch (err) {
            console.error("Save failed", err);
        }

        
    }

    async registerTab(tabId) {
        
        const tab = await chrome.tabs.get(tabId);

        
        if (tab) {
            this.previousTab = {...this.currentTab}
            this.currentTab = new Tab(tab.id, tab.url, tab.title, Date.now())
            this.userTracked = true;
        }
        else {
            this.currentTab = null;
            this.userTracked = false;
        }
        await this.saveCurrentSession(this.previousTab);

    }
}
