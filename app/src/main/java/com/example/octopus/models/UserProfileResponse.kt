package com.example.octopus.models

data class UserProfileResponse(
    val name: String,
    val phone: String,
    val user_addresses: List<UserAddress> // Теперь это список адресов
)

data class UserAddress(
    val id: Int,
    val name: String,
    val address: AddressDetails
)

data class AddressDetails(
    val id: Int,
    val district: String,
    val street: String,
    val house: String
)

data class Address(
    val name: String,
    val district: String,
    val street: String,
    val house: String
)
