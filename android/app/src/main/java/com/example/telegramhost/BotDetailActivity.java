package com.example.telegramhost;

import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.*;

public class BotDetailActivity extends AppCompatActivity {
    private DatabaseHelper db;
    private String botId;
    private TextView tvLogs;
    private Handler handler = new Handler();
    private Runnable logRunnable;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_detail);
        db = new DatabaseHelper(this);
        botId = getIntent().getStringExtra("id");
        String name = getIntent().getStringExtra("name");

        TextView tvName = findViewById(R.id.tvName);
        tvName.setText("🤖 " + name);

        tvLogs = findViewById(R.id.tvLogs);
        Button btnStop = findViewById(R.id.btnStop);
        Button btnRestart = findViewById(R.id.btnRestart);
        Button btnLogs = findViewById(R.id.btnLogs);
        Button btnDelete = findViewById(R.id.btnDelete);
        Button btnSleep = findViewById(R.id.btnSleep);

        btnStop.setOnClickListener(v -> {
            MainActivity.api.stopBot(botId).enqueue(toast("⏹ Stopped"));
            db.updateBotStatus(botId, "stopped");
        });

        btnRestart.setOnClickListener(v -> {
            MainActivity.api.restartBot(botId).enqueue(toast("🔄 Restarted"));
            db.updateBotStatus(botId, "running");
        });

        btnLogs.setOnClickListener(v -> fetchLogs());

        btnSleep.setOnClickListener(v -> {
            db.toggleSleepMode(botId, true);
            Toast.makeText(this, "💤 Sleep mode ON", Toast.LENGTH_SHORT).show();
        });

        btnDelete.setOnClickListener(v -> {
            MainActivity.api.deleteBot(botId).enqueue(toast("🗑 Deleted"));
            db.deleteBot(botId);
            finish();
        });

        // Auto refresh logs every 4 sec (real-time)
        logRunnable = () -> { fetchLogs(); handler.postDelayed(logRunnable, 4000); };
        handler.post(logRunnable);
    }

    void fetchLogs() {
        MainActivity.api.getLogs(botId).enqueue(new Callback<LogsResponse>() {
            public void onResponse(Call<LogsResponse> c, Response<LogsResponse> r) {
                if (r.isSuccessful() && r.body() != null) {
                    tvLogs.setText(r.body().logs);
                }
            }
            public void onFailure(Call<LogsResponse> c, Throwable t) {
                tvLogs.setText("📡 HTTP request failed: " + t.getMessage() + "\n(Backend offline)");
            }
        });
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(logRunnable);
    }

    Callback<StatusResponse> toast(String msg) {
        return new Callback<StatusResponse>() {
            public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) {
                Toast.makeText(BotDetailActivity.this, msg, Toast.LENGTH_SHORT).show();
            }
            public void onFailure(Call<StatusResponse> c, Throwable t) {
                Toast.makeText(BotDetailActivity.this, "Offline", Toast.LENGTH_SHORT).show();
            }
        };
    }
}
