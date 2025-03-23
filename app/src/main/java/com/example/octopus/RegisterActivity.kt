package com.example.octopus
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import com.example.octopus.models.LoginResponse
import com.example.octopus.models.RegisterRequest
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.register_activity)
        supportActionBar?.hide()
        val editTextEmail = findViewById<EditText>(R.id.editTextEmail)
        val editTextPassword = findViewById<EditText>(R.id.editTextPassword)
        val buttonRegister = findViewById<Button>(R.id.buttonRegister)

        buttonRegister.setOnClickListener {
            val email = editTextEmail.text.toString()
            val password = editTextPassword.text.toString()

            if (email.isNotEmpty() && password.isNotEmpty()) {
                // Извлекаем username из email
                val username = extractUsernameFromEmail(email)

                // Создаем объект RegisterRequest
                val registerRequest = RegisterRequest(email, password, username)
                val apiService = RetrofitClient.instance
                // Отправляем запрос на сервер
                apiService.register(registerRequest).enqueue(object : Callback<LoginResponse> {
                    override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                        if (response.isSuccessful) {
                            val loginResponse = response.body()
                            loginResponse?.let {
                                Toast.makeText(this@RegisterActivity, "Регистрация успешна!", Toast.LENGTH_SHORT).show()
                                // Перенаправление на экран входа
                                startActivity(Intent(this@RegisterActivity, MainActivity::class.java))
                                finish()
                            }
                        } else {
                            Toast.makeText(this@RegisterActivity, "Ошибка регистрации", Toast.LENGTH_SHORT).show()
                        }
                    }

                    override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                        Toast.makeText(this@RegisterActivity, "Ошибка сети: ${t.message}", Toast.LENGTH_SHORT).show()
                    }
                })
            } else {
                Toast.makeText(this, "Заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun extractUsernameFromEmail(email: String): String {
        return email.substringBefore("@")
    }
}