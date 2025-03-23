package com.example.octopus

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.octopus.models.TokenManager
import com.example.octopus.models.UserProfileResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.graphics.Color
import android.util.Log
import com.example.octopus.databinding.ActivityProfileBinding
import com.example.octopus.models.UserAddress
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import androidx.core.view.children
import androidx.core.view.get
import com.example.octopus.models.AddressDetails


class ProfileActivity : AppCompatActivity() {

    private lateinit var usernameTextView: TextView
    private lateinit var phoneTextView: TextView
    private lateinit var binding: ActivityProfileBinding
    private var counter_ : Int = 0;
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Инициализируем binding перед установкой контента
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root) // Используем root view из binding

        supportActionBar?.hide()

        // Все элементы теперь получаем через binding
        val backButton = binding.backProfileButton
        backButton.setOnClickListener {
            finish()
        }

        // Инициализация TextView через binding
        usernameTextView = binding.usernameTextView
        phoneTextView = binding.phoneTextView

        // Запрос данных
        val token = "${TokenManager.tokenType} ${TokenManager.accessToken}"
        fetchUserProfile(token)


    }   companion object {
        private const val EDIT_PROFILE_REQUEST = 1
    }

    private fun addAddressCard(address: UserAddress) {
        val cardView = layoutInflater.inflate(
            R.layout.item_address_card,
            binding.addressesContainer,
            false
        )

        with(cardView) {
            findViewById<TextView>(R.id.titleTextView).text = address.name
            findViewById<TextView>(R.id.detailsDistrict).text = "Район: ${address.address.district}"
            findViewById<TextView>(R.id.detailsStreet).text = "Улица: ${address.address.street}"
            findViewById<TextView>(R.id.detailsHouse).text = "Дом: ${address.address.house}"
            //counter_++
            setOnClickListener { showEditAddressDialog(address) }
        }

        binding.addressesContainer.addView(cardView)
    }

    private fun fetchUserProfile(token: String) {
        val apiService = RetrofitClient.instance

        apiService.getUserProfile(token).enqueue(object : Callback<UserProfileResponse> {
            override fun onResponse(
                call: Call<UserProfileResponse>,
                response: Response<UserProfileResponse>
            ) {
                if (response.isSuccessful) {

                    response.body()?.let { profile ->
                        // Очищаем предыдущие карточки
                        binding.addressesContainer.removeAllViews()
                        usernameTextView.setText(profile.name)
                        phoneTextView.setText(profile.phone)
                        //userProfile_ = profile;
                        // Добавляем новые карточки
                        profile.user_addresses.forEach { address ->
                            addAddressCard(address)
                            Log.d("ADDRESS_DEBUG", "Added address: ${address.name}")
                        }
                    }
                }
            }

            override fun onFailure(call: Call<UserProfileResponse>, t: Throwable) {
                Toast.makeText(this@ProfileActivity, "Ошибка сети", Toast.LENGTH_SHORT).show()
            }
        })
    }



    private fun showEditAddressDialog(address: UserAddress) {
        val dialogView = layoutInflater.inflate(R.layout.dialog_edit_address, null)

        with(dialogView) {
            //findViewById<TextView>(R.id.idCard).setText(address.id)
            findViewById<EditText>(R.id.etName).setText(address.name)
            findViewById<EditText>(R.id.etDistrict).setText(address.address.district)
            findViewById<EditText>(R.id.etStreet).setText(address.address.street)
            findViewById<EditText>(R.id.etHouse).setText(address.address.house)
        }

        AlertDialog.Builder(this)
            .setTitle("Редактирование адреса")
            .setView(dialogView)
            .setPositiveButton("Сохранить") { _, _ ->
                // Обновление данных
                val updatedAddress = UserAddress(

                    id = address.id,
                    name = dialogView.findViewById<EditText>(R.id.etName).text.toString(),
                    address = AddressDetails(
                        id = address.address.id,
                        district = dialogView.findViewById<EditText>(R.id.etDistrict).text.toString(),
                        street = dialogView.findViewById<EditText>(R.id.etStreet).text.toString(),
                        house = dialogView.findViewById<EditText>(R.id.etHouse).text.toString()
                    )
                )
                //updateAddress(updatedAddress, dialogView.findViewById<TextView>(R.id.idCard).text.toString().toInt())
            }
            .setNegativeButton("Отмена", null)
            .show()
    }

    public fun updateAddress(updatedAddress: UserAddress, id_Card : Int) {
        // Реализуйте обновление адреса через API
        // и обновите соответствующую карточкуащк


/*
        binding.addressesContainer.children.forEach { view ->
            val address = view.findViewById<TextView>(R.id.idCard).text
            if(id_Card.toString() == address) {
                view.findViewById<EditText>(R.id.etName).setText(updatedAddress<)
                view.findViewById<EditText>(R.id.etDistrict).setText(updatedAddress.district)
                view.findViewById<EditText>(R.id.etStreet).setText(updatedAddress.street)
                view.findViewById<EditText>(R.id.etHouse).setText(updatedAddress.house)

            }
    }*/
        }


    private fun setDefaultTextIfEmpty(textView: TextView) {
        if (textView.text == getString(R.string.default_username) ||
            textView.text == getString(R.string.default_phone) ||
            textView.text.startsWith(getString(R.string.default_address_prefix))
        ) {
            textView.setTextColor(Color.GRAY) // Устанавливаем белый цвет текста
        } else {
            textView.setTextColor(Color.BLACK) // Возвращаем черный цвет для реальных данных
        }
    }

    /*
    private fun fetchUserUpdateProfile(token: String, ) {
        val apiService = RetrofitClient.instance
        val token = "${TokenManager.tokenType} ${TokenManager.accessToken}"
        val userProfile
        apiService.updateUserProfile(,token).enqueue(object : Callback<UserProfileResponse> {
            override fun onResponse(
                call: Call<UserProfileResponse>,
                response: Response<UserProfileResponse>
            ) {
                Log.d("API_RESPONSE", "Response Body: $response")
                if (response.isSuccessful) {

                    val userProfile = response.body()
                    userProfile?.let {
                        // Заполняем данные профиля с проверкой на null
                        usernameTextView.text = userProfile.username?.ifEmpty { "Имя пользователя" } ?: "Имя пользователя"
                        loginTextView.text = userProfile.login?.ifEmpty { "Логин" } ?: "Логин"
                        phoneTextView.text = userProfile.phone?.ifEmpty { "Номер телефона" } ?: "Номер телефона"

                        // Проверяем, что addresses не null
                        val addresses = userProfile.addresses?.toList() ?: emptyList()

                        // Заполняем адреса
                        address1TextView.text = addresses.getOrNull(0)?.second ?: "Адрес 1"
                        address2TextView.text = addresses.getOrNull(1)?.second ?: "Адрес 2"
                        address3TextView.text = addresses.getOrNull(2)?.second ?: "Адрес 3"

                        // Устанавливаем белый цвет текста для запасных значений
                        setDefaultTextIfEmpty(usernameTextView)
                        setDefaultTextIfEmpty(loginTextView)
                        setDefaultTextIfEmpty(phoneTextView)
                        setDefaultTextIfEmpty(address1TextView)
                        setDefaultTextIfEmpty(address2TextView)
                        setDefaultTextIfEmpty(address3TextView)
                    }
                } else {
                    // Обработка ошибки
                    println("Ошибка получения данных профиля: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<UserProfileResponse>, t: Throwable) {
                // Обработка ошибки сети
                println("Ошибка сети: ${t.message}")
            }
        })
    }*/
}