package com.example.loginapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.octopus.R

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout)

        val editTextRegUsername = findViewById<EditText>(R.id.editTextRegUsername)
        val editTextRegPassword = findViewById<EditText>(R.id.editTextRegPassword)
        val buttonRegister = findViewById<Button>(R.id.buttonRegister)

        buttonRegister.setOnClickListener {
            val username = editTextRegUsername.text.toString()
            val password = editTextRegPassword.text.toString()

            if (username.isNotEmpty() && password.isNotEmpty()) {
                // Здесь можно сохранить данные в базу данных
                Toast.makeText(this, "Регистрация успешна!", Toast.LENGTH_SHORT).show()
                finish() // Закрываем экран регистрации
            } else {
                Toast.makeText(this, "Заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }
    }
}