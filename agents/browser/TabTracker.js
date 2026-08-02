import { Tab } from "./Tab.js"

export class TabTracker {
    constructor() {
        this.currentTab = this.previousTab = null;
        this.userTracked = true;
    }

    async saveCurrentSession() {
        if (!this.userTracked) return;
        console.log({
            url: this.previousTab.url,
            title: this.previousTab.title,
            eventStartTime: this.previousTab.eventStartTime,
            eventEndTime: Date.now()
        })
        try {
            const res = await fetch("http://127.0.0.1:8000/browser_event", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: this.previousTab.url,
                    title: this.previousTab.title,
                    eventStartTime: this.previousTab.eventStartTime,
                    eventEndTime: Date.now()
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

        
        if (tab) {
            this.previousTab = {...this.currentTab}
            this.currentTab = new Tab(tab.id, tab.url, tab.title, Date.now())
            this.userTracked = true;
        }
        else {
            console.log("EWXEC")
            this.currentTab = null;
            this.userTracked = false;
        }
        await this.saveCurrentSession();


        // console.log("Tracking:", this.currentTab.url);

    }
}
