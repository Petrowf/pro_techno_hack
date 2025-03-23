package com.example.octopus

import com.example.octopus.api.ApiService
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    private const val BASE_URL = "http://192.168.114.56:8000/" // Базовый URL вашего API

    val instance: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create()) // Для работы с JSON
            .build()
            .create(ApiService::class.java)
    }
}