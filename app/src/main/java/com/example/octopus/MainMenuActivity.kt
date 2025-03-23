package com.example.octopus

import Accident
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import com.example.octopus.api.ApiService
import com.example.octopus.databinding.ActivityMainMenuBinding
import com.example.octopus.models.TokenManager
import com.google.firebase.messaging.FirebaseMessaging
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Response
import retrofit2.Callback
import java.text.SimpleDateFormat
import java.util.Locale

class MainMenuActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainMenuBinding
    private val apiService = RetrofitClient.instance

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Убрали первый setContentView
        binding = ActivityMainMenuBinding.inflate(layoutInflater)
        setContentView(binding.root)

        NotificationUtils(this).createNotificationChannel()
        supportActionBar?.hide()

        // Используем View Binding для кнопки
        binding.profileButton.setOnClickListener {
            val intent = Intent(this, ProfileActivity::class.java)
            startActivity(intent)
        }

        loadAccidentsData()
        checkAndSendFcmToken()
    }

    private fun loadAccidentsData() {
        val token = "${TokenManager.tokenType} ${TokenManager.accessToken}"

        apiService.getAccidents(token).enqueue(object : Callback<List<Accident>> {
            override fun onResponse(call: Call<List<Accident>>, response: Response<List<Accident>>) {
                if (response.isSuccessful) {
                    response.body()?.let { accidents ->
                        generateAccidentViews(accidents)
                    }
                } else {
                    showError("Ошибка загрузки: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<List<Accident>>, t: Throwable) {
                showError("Сетевая ошибка: ${t.message}")
            }
        })
    }

    private fun generateAccidentViews(accidents: List<Accident>) {
        binding.accidentsContainer.removeAllViews()

        accidents.forEach { accident ->
            val accidentCard = createAccidentCard(accident)
            binding.accidentsContainer.addView(accidentCard)
        }
    }

    private fun createAccidentCard(accident: Accident): LinearLayout {
        return LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(16.dpToPx(), 8.dpToPx(), 16.dpToPx(), 8.dpToPx())
            }

            orientation = LinearLayout.VERTICAL
            background = ContextCompat.getDrawable(context, R.drawable.rounded_card)
            elevation = 8f
            setPadding(24.dpToPx(), 24.dpToPx(), 24.dpToPx(), 24.dpToPx())

            // Заголовок аварии
            addView(createTextView(
                text = accident.type,
                textSizeSp = 18f,
                isBold = true,
                color = Color.RED
            ))

            // Время аварии
            addView(createTextView(
                text = "Время: ${formatDateTime(accident.startTime)} - ${formatDateTime(accident.endTime)}",
                textSizeSp = 14f,
                color = Color.DKGRAY
            ))

            // Причина
            addView(createTextView(
                text = "Причина: ${accident.reason}",
                textSizeSp = 14f
            ))

            // Комментарий
            addView(createTextView(
                text = accident.comment.replace("\n", " "),
                textSizeSp = 14f,
                maxLines = 3
            ))

            // Количество затронутых адресов
            addView(createTextView(
                text = "Затронуто адресов: ${accident.addressIds.size}",
                textSizeSp = 12f,
                color = Color.GRAY
            ))
        }
    }

    private fun createTextView(
        text: String,
        textSizeSp: Float,
        color: Int = Color.BLACK,
        isBold: Boolean = false,
        maxLines: Int = Int.MAX_VALUE
    ): TextView {
        return TextView(this).apply {
            this.text = text
            setTextColor(color)
            textSize = textSizeSp
            typeface = if (isBold) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
            setMaxLines(maxLines)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(0, 4.dpToPx(), 0, 4.dpToPx())
            }
        }
    }

    private fun formatDateTime(isoDateTime: String): String {
        return try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault())
            val date = inputFormat.parse(isoDateTime)
            outputFormat.format(date)
        } catch (e: Exception) {
            "Некорректное время"
        }
    }

    private fun Int.dpToPx(): Int = (this * resources.displayMetrics.density).toInt()

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
    /**
     * Метод для проверки и отправки FCM Token на сервер.
     */
    private fun checkAndSendFcmToken() {
        // Получаем текущий FCM Token из Firebase
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                val fcmToken = task.result
                println("Новый FCM Token: $fcmToken")
                val token = "${TokenManager.tokenType} ${TokenManager.accessToken}"
                // Отправляем FCM Token на сервер
                sendFcmTokenToServer(fcmToken, token)
            } else {
                println("Ошибка при получении FCM Token: ${task.exception}")
            }
        }
    }

    /**
     * Метод для отправки FCM Token на сервер через Retrofit.
     */
    private fun sendFcmTokenToServer(fcmToken: String, token : String) {
        val apiService = RetrofitClient.instance

        // Создаём объект запроса с FCM Token
        val request = ApiService.FcmTokenRequest(fcmToken, token)

        // Отправляем PUT-запрос на сервер
        apiService.sendFcmToken(request, token).enqueue(object : Callback<ResponseBody> {
            override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                if (response.isSuccessful) {
                    println("FCM Token успешно отправлен на сервер через PUT")
                } else {
                    println("Ошибка отправки FCM Token через PUT: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                println("Ошибка сети при отправке через PUT: ${t.message}")
            }
        })
    }
}