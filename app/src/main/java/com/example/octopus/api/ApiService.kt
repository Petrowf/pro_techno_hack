package com.example.octopus.api

import Accident
import com.example.octopus.models.LoginRequest
import com.example.octopus.models.LoginResponse
import com.example.octopus.models.RegisterRequest
import com.example.octopus.models.UserProfileResponse
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.PUT

interface ApiService {
    @POST("api/v1/token") // Укажите путь к вашему API
    fun login(@Body request: LoginRequest): Call<LoginResponse>

    @POST("api/v1/register")
    fun register(@Body request: RegisterRequest): Call<LoginResponse>

    @GET("api/v1/me")
    fun getUserProfile(
        @Header("Authorization") token: String
    ): Call<UserProfileResponse>

    @POST("api/v1/me")
    fun updateUserProfile(
        @Header("Authorization") token: String
    ): Call<UserProfileResponse>

    @GET("api/v1/user-events")
    fun getAccidents(
        @Header("Authorization") token: String
    ): Call<List<Accident>>

    @PUT("api/v1/me/fcm_token")
    fun sendFcmToken(@Body request: FcmTokenRequest,
        @Header("Authorization") token: String): Call<ResponseBody>

    data class FcmTokenRequest(
        val fcmToken: String,
        val token : String
    )
}