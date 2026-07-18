import { Tab } from "./Tab.js"

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.event_time = null;
        this.userTracked = true;
    }

    async saveCurrentSession() {
        if (!this.currentTab || !this.event_time) return;
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
                    started_at: this.event_time,
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
            this.event_time = null;
            this.userTracked = false;
        }
        else {
            this.previousTab = {...this.currentTab}
            this.currentTab = new Tab(tab.id, tab.url, tab.title)
            // console.log("Current Tab:", this.currentTab)
            // console.log("Previous Tab:",this.previousTab)
            this.event_time = Date.now();
            this.userTracked = true;
        }

        await this.saveCurrentSession();

        // console.log("Tracking:", this.currentTab.url);

    }
}
