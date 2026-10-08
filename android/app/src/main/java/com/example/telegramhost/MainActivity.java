package com.example.telegramhost;

import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.*;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {
    public static final String BASE_URL = "http://10.0.2.2:8000/";
    public static ApiService api;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);

        api = new Retrofit.Builder().baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build().create(ApiService.class);

        EditText etToken = findViewById(R.id.etToken);
        EditText etName = findViewById(R.id.etName);
        EditText etCode = findViewById(R.id.etCode);
        TextView tvDetect = findViewById(R.id.tvDetect);
        Button btnDeploy = findViewById(R.id.btnDeploy);
        Button btnDash = findViewById(R.id.btnDashboard);
        Button btnProfile = findViewById(R.id.btnProfile);
        Button btnDetect = findViewById(R.id.btnDetect);

        DatabaseHelper db = new DatabaseHelper(this);

        // Auto detect bot name from token
        btnDetect.setOnClickListener(v -> {
            String token = etToken.getText().toString().trim();
            if (token.isEmpty()) {
                Toast.makeText(this, "Pehle token daalo", Toast.LENGTH_SHORT).show();
                return;
            }
            tvDetect.setText("🔍 Detecting bot...");
            TelegramApi.detectBot(token, new TelegramApi.BotInfoCallback() {
                @Override public void onResult(String name, String username, String id) {
                    runOnUiThread(() -> {
                        etName.setText(name);
                        tvDetect.setText("✅ @" + username + " (ID: " + id + ")");
                        tvDetect.setTextColor(getColor(R.color.success));
                    });
                }
                @Override public void onError(String error) {
                    runOnUiThread(() -> {
                        tvDetect.setText("❌ " + error);
                        tvDetect.setTextColor(getColor(R.color.danger));
                    });
                }
            });
        });

        btnDeploy.setOnClickListener(v -> {
            String n = etName.getText().toString();
            String t = etToken.getText().toString();
            String c = etCode.getText().toString();
            if (n.isEmpty() || t.isEmpty() || c.isEmpty()) {
                Toast.makeText(this, "Sab fields bharo", Toast.LENGTH_SHORT).show();
                return;
            }
            api.createBot(new BotRequest(n, t, c)).enqueue(new Callback<BotResponse>() {
                public void onResponse(Call<BotResponse> call, Response<BotResponse> r) {
                    if (r.isSuccessful() && r.body() != null) {
                        db.saveBot(r.body().bot_id, n, t, c, "running");
                        Toast.makeText(MainActivity.this, "🚀 Bot deployed!", Toast.LENGTH_SHORT).show();
                    } else {
                        // Offline save
                        db.saveBot("local_" + System.currentTimeMillis(), n, t, c, "offline");
                        Toast.makeText(MainActivity.this, "💾 Saved locally (backend offline)", Toast.LENGTH_SHORT).show();
                    }
                }
                public void onFailure(Call<BotResponse> call, Throwable t) {
                    db.saveBot("local_" + System.currentTimeMillis(), n, t.toString(), c, "offline");
                    Toast.makeText(MainActivity.this, "💾 Saved locally", Toast.LENGTH_SHORT).show();
                }
            });
        });

        btnDash.setOnClickListener(v -> startActivity(new Intent(this, DashboardActivity.class)));
        btnProfile.setOnClickListener(v -> startActivity(new Intent(this, ProfileActivity.class)));
    }
}
