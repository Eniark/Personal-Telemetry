import { Tab } from "./Tab.js"

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.startTime = null;
        this.userTracked = true;
    }

    async saveCurrentSession() {
        if (!this.currentTab || !this.startTime) return;
        if (!this.userTracked) return;

        const duration = Date.now() - this.startTime;
        if (duration <= 0) return;

        try {
            const res = await fetch("http://127.0.0.1:8000/event", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    website: this.currentTab.url,
                    duration_ms: duration,
                    started_at: this.startTime,
                    ended_at: Date.now(),
                })
            });

            if (!res.ok) throw new Error("Save failed");

            // console.log("Saved:", this.currentTab.url, Math.round(duration / 1000), "sec");

        } catch (err) {
            console.error("Save failed", err);
        }
    }

    async registerTab(tabId, save=true) {
        if (save) {
            await this.saveCurrentSession();
        }
        const tab = await chrome.tabs.get(tabId);

        if (!tab) {
            this.currentTab = null;
            this.startTime = null;
            this.userTracked = false;
        }
        else {
            this.previousTab = {...this.currentTab}
            this.currentTab = new Tab(tab.id, tab.url, tab.title)
            console.log("Current Tab:", this.currentTab)
            console.log("Previos Tab:",this.previousTab)
            this.startTime = Date.now();
            this.userTracked = true;
        }

        // console.log("Tracking:", this.currentTab.url);

    }
}
