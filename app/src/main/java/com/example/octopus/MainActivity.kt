package com.example.octopus

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.octopus.models.LoginRequest
import com.example.octopus.models.LoginResponse
import com.example.octopus.models.TokenManager
import com.google.firebase.FirebaseApp
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        FirebaseApp.initializeApp(this)
        Log.d("FirebaseInit", "Firebase initialized successfully")
        setContentView(R.layout.activity_main)
        supportActionBar?.hide()
        // Привязываем элементы интерфейса
        val editTextUsername = findViewById<EditText>(R.id.editTextUsername)
        val editTextPassword = findViewById<EditText>(R.id.editTextPassword)
        val buttonLogin = findViewById<Button>(R.id.buttonLogin)
        val buttonRegisterLink = findViewById<Button>(R.id.buttonRegister)
        val buttonForgotPassword = findViewById<Button>(R.id.buttonForgotPassword)

        // Обработчик нажатия на кнопку "Войти"
        buttonLogin.setOnClickListener {
            val username = editTextUsername.text.toString()
            val password = editTextPassword.text.toString()

            if (username.isNotEmpty() && password.isNotEmpty()) {
                performLogin(username, password)
                println(username)
                println(password)
            } else {
                Toast.makeText(this, "Заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }

        // Обработчик нажатия на кнопку "Регистрация"
        buttonRegisterLink.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        // Обработчик нажатия на кнопку "Забыли пароль?"
        buttonForgotPassword.setOnClickListener {
            startActivity(Intent(this, ResetPasswordActivity::class.java))
        }
    }

    private fun performLogin(login: String, password: String) {
        val apiService = RetrofitClient.instance
        val loginRequest = LoginRequest(login, password)

        apiService.login(loginRequest).enqueue(object : Callback<LoginResponse> {
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                if (response.isSuccessful) {
                    val loginResponse = response.body()
                    loginResponse?.let {
                        TokenManager.accessToken = it.access_token
                        TokenManager.tokenType = it.token_type
                        println("Токен сохранен: ${TokenManager.accessToken}")
                        val intent = Intent(this@MainActivity, MainMenuActivity::class.java)
                        startActivity(intent)
                        finish()
                    }
                } else {
                    Toast.makeText(this@MainActivity, "Не верно введен логин или пароль", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Toast.makeText(this@MainActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                Log.e("NetworkError", "Ошибка сети: ${t.message}")
            }
        })
    }
}