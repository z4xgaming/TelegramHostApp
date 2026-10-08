package com.example.telegramhost;

import org.json.JSONObject;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.util.concurrent.TimeUnit;

public class TelegramApi {
    private static final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build();

    public interface BotInfoCallback {
        void onResult(String name, String username, String id);
        void onError(String error);
    }

    // Token se bot ka naam, username, ID nikaalo (getMe API)
    public static void detectBot(String token, BotInfoCallback cb) {
        new Thread(() -> {
            try {
                Request req = new Request.Builder()
                        .url("https://api.telegram.org/bot" + token + "/getMe")
                        .build();
                Response resp = client.newCall(req).execute();
                String body = resp.body().string();
                JSONObject json = new JSONObject(body);
                if (json.getBoolean("ok")) {
                    JSONObject r = json.getJSONObject("result");
                    cb.onResult(
                            r.getString("first_name"),
                            r.optString("username", ""),
                            String.valueOf(r.getLong("id"))
                    );
                } else {
                    cb.onError("Invalid token");
                }
            } catch (Exception e) {
                cb.onError(e.getMessage());
            }
        }).start();
    }
}
