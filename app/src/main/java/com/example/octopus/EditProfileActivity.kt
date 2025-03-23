package com.example.octopus

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.octopus.databinding.ActivityEditProfileBinding

class EditProfileActivity : AppCompatActivity() {

    private lateinit var binding: ActivityEditProfileBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityEditProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Получение данных из ProfileActivity
        val username = intent.getStringExtra("username")
        val login = intent.getStringExtra("login")
        val phone = intent.getStringExtra("phone")
        val address1 = intent.getStringExtra("address1")
        val address2 = intent.getStringExtra("address2")
        val address3 = intent.getStringExtra("address3")

        // Заполнение полей
        binding.editUsername.setText(username)
        binding.editLogin.setText(login)
        binding.editPhone.setText(phone)
        binding.editAddress1.setText(address1)
        binding.editAddress2.setText(address2)
        binding.editAddress3.setText(address3)

        // Обработка нажатия на кнопку "Сохранить"
        binding.saveButton.setOnClickListener {
            val resultIntent = Intent().apply {
                putExtra("username", binding.editUsername.text.toString())
                putExtra("login", binding.editLogin.text.toString())
                putExtra("phone", binding.editPhone.text.toString())
                putExtra("address1", binding.editAddress1.text.toString())
                putExtra("address2", binding.editAddress2.text.toString())
                putExtra("address3", binding.editAddress3.text.toString())
            }
            setResult(RESULT_OK, resultIntent)
            finish()
        }
    }
}