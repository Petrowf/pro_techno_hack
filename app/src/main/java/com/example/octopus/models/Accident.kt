import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class Accident(
    @SerializedName("id") val id: Int,
    @SerializedName("type") val type: String,
    @SerializedName("reason") val reason: String,
    @SerializedName("comment") val comment: String,
    @SerializedName("start_time") val startTime: String,
    @SerializedName("end_time") val endTime: String,
    @SerializedName("address_ids") val addressIds: List<Int>
) : Serializable