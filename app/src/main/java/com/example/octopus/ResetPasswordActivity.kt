package com.example.octopus

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.octopus.R

class ResetPasswordActivity : AppCompatActivity() {

    private var verificationCode = "123456" // Пример кода подтверждения

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_reset_password)
        supportActionBar?.hide()
        val editTextPhone = findViewById<EditText>(R.id.editTextPhone)
        val editTextCode = findViewById<EditText>(R.id.editTextCode)
        val buttonSendCode = findViewById<Button>(R.id.buttonSendCode)
        val buttonConfirmCode = findViewById<Button>(R.id.buttonConfirmCode)

        buttonSendCode.setOnClickListener {
            val phone = editTextPhone.text.toString()
            if (phone.isNotEmpty()) {
                // Здесь можно отправить код на телефон через API
                Toast.makeText(this, "Код отправлен на $phone", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Введите номер телефона", Toast.LENGTH_SHORT).show()
            }
        }

        buttonConfirmCode.setOnClickListener {
            val code = editTextCode.text.toString()
            if (code == verificationCode) {
                Toast.makeText(this, "Код подтвержден!", Toast.LENGTH_SHORT).show()
                // Здесь можно сбросить пароль
            } else {
                Toast.makeText(this, "Неверный код", Toast.LENGTH_SHORT).show()
            }
        }
    }
}