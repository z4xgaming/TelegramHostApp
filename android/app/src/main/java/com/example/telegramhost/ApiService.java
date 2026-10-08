package com.example.telegramhost;
import retrofit2.Call;
import retrofit2.http.*;
import java.util.List;
public interface ApiService {
    @POST("bot/create") Call<BotResponse> createBot(@Body BotRequest bot);
    @POST("bot/{id}/stop") Call<StatusResponse> stopBot(@Path("id") String id);
    @POST("bot/{id}/restart") Call<StatusResponse> restartBot(@Path("id") String id);
    @GET("bot/{id}/logs") Call<LogsResponse> getLogs(@Path("id") String id);
    @GET("bots") Call<BotsList> listBots();
    @DELETE("bot/{id}") Call<StatusResponse> deleteBot(@Path("id") String id);
}
