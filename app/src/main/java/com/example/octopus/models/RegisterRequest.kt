package com.example.octopus.models

data class RegisterRequest(
    val login: String,
    val password: String,
    val name: String
)