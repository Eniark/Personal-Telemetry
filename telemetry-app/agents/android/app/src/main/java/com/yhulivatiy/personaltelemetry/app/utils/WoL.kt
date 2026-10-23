package com.yhulivatiy.personaltelemetry.app.utils

import android.util.Log
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

object WakeOnLan {

    suspend fun wake(
        macAddress: String,
        broadcastAddress: String = "255.255.255.255",
        port: Int = 9
    ) {
        val mac = macAddress
            .replace(":", "")
            .replace("-", "")

        require(mac.length == 12)

        val macBytes = ByteArray(6)

        for (i in 0 until 6) {
            macBytes[i] = mac
                .substring(i * 2, i * 2 + 2)
                .toInt(16)
                .toByte()
        }

        val packet = ByteArray(102)

        // 6 × FF
        for (i in 0 until 6) {
            packet[i] = 0xFF.toByte()
        }

        // MAC repeated 16 times
        for (i in 0 until 16) {
            System.arraycopy(
                macBytes,
                0,
                packet,
                6 + i * 6,
                6
            )
        }

        DatagramSocket().use { socket ->

            socket.broadcast = true

            val address = InetAddress.getByName(
                broadcastAddress
            )

            val datagram = DatagramPacket(
                packet,
                packet.size,
                address,
                port
            )

            Log.d(
                "WOL",
                "Sending WoL to $macAddress via $broadcastAddress:$port"
            )

            socket.send(datagram)

            Log.d(
                "WOL",
                "WoL packet sent successfully"
            )
        }
    }
}
