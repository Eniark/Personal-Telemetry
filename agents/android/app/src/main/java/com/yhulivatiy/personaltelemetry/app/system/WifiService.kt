package com.yhulivatiy.personaltelemetry.app.system

import android.content.Context
import android.net.wifi.WifiManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

class WifiService(
    private val context: Context
) {
    fun isConnectedToWifi(): Boolean {
        val connectivityManager =
            context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }

    fun getCurrentSsid(): String? {
        val wifiManager =
            context.getSystemService(Context.WIFI_SERVICE) as WifiManager

        val ssid = wifiManager.connectionInfo.ssid

        return ssid.removeSurrounding("\"")
    }


}