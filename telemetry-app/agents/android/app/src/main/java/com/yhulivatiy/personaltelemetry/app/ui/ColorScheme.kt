package com.yhulivatiy.personaltelemetry.app.ui

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

//val WarningColor = Color(0xFFFFC107)
val WarningColor = Color.Yellow
val LightColorScheme = lightColorScheme(
    primary = Color(0xFF8E94F2), // Purple
    onPrimary = Color.White,

    secondary = Color(0XFFFA824C), // Orange
    background = Color.Black,
    onError = Color.Red,
)

val ColorScheme.warning: Color
    get() = WarningColor

val ColorScheme.success: Color
    get() = Color.Green