package com.example.personaltelemetry.app.ui

import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Typography
import androidx.compose.ui.graphics.Color

val AppTypography = Typography(
    headlineLarge = TextStyle(
        fontSize = 35.sp,
        fontWeight = FontWeight.Bold
    ),
    bodyLarge = TextStyle(
        fontSize = 32.sp,
        color = Color.White
    ),
    bodySmall = TextStyle(
        fontSize = 14.sp,
        color = Color.White
    )
)