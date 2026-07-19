import { Tab } from "./Tab.js"

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.eventTime = null;
        this.userTracked = true;
    }

    async saveCurrentSession() {
        if (!this.currentTab || !this.eventTime) return;
        if (!this.userTracked) return;

        try {
            const res = await fetch("http://127.0.0.1:8000/browser_event", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    website: this.currentTab.url,
                    title: this.currentTab.title,
                    eventTime: this.eventTime,
                    ended_at: Date.now(),
                })
            });

            if (!res.ok) throw new Error("Save failed");

            console.log("Saved:", this.currentTab.url);

        } catch (err) {
            console.error("Save failed", err);
        }
    }

    async registerTab(tabId) {
        
        const tab = await chrome.tabs.get(tabId);

        if (!tab) {
            this.currentTab = null;
            this.eventTime = null;
            this.userTracked = false;
        }
        else {
            this.previousTab = {...this.currentTab}
            this.currentTab = new Tab(tab.id, tab.url, tab.title)
            // console.log("Current Tab:", this.currentTab)
            // console.log("Previous Tab:",this.previousTab)
            this.eventTime = Date.now();
            this.userTracked = true;
        }

        await this.saveCurrentSession();

        // console.log("Tracking:", this.currentTab.url);

    }
}
