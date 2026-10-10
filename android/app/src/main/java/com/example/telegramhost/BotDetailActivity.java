package com.example.telegramhost;

import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;
import retrofit2.*;

public class BotDetailActivity extends BaseActivity {
    private DatabaseHelper db;
    private String botId;
    private String botName;
    private TextView tvLogs;
    private TextView tvStatusBadge;
    private Handler handler = new Handler();
    private Runnable logRunnable;
    private static final int POLL_INTERVAL = 10000; // 10 seconds

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_detail);
        setupBottomNav(R.id.nav_bots);

        db = new DatabaseHelper(this);
        botId = getIntent().getStringExtra("id");
        botName = getIntent().getStringExtra("name");
        if (botName == null) botName = "Bot";

        TextView tvName = findViewById(R.id.tvName);
        tvName.setText("🤖 " + botName);

        tvLogs = findViewById(R.id.tvLogs);
        tvStatusBadge = findViewById(R.id.tvStatusBadge);
        Button btnStop = findViewById(R.id.btnStop);
        Button btnRestart = findViewById(R.id.btnRestart);
        Button btnSleep = findViewById(R.id.btnSleep);
        Button btnDelete = findViewById(R.id.btnDelete);
        Button btnLogs = findViewById(R.id.btnLogs);

        btnStop.setOnClickListener(v -> {
            showProcessing(btnStop, "Stopping");
            MainActivity.api.stopBot(botId).enqueue(new Callback<StatusResponse>() {
                public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) {
                    hideProcessing(btnStop, R.color.danger);
                    db.updateBotStatus(botId, "stopped");
                    Toast.makeText(BotDetailActivity.this, "⏹️ Stopped", Toast.LENGTH_SHORT).show();
                }
                public void onFailure(Call<StatusResponse> c, Throwable t) {
                    hideProcessing(btnStop, R.color.danger);
                    db.updateBotStatus(botId, "stopped");
                    Toast.makeText(BotDetailActivity.this, "⏹️ Stopped (offline)", Toast.LENGTH_SHORT).show();
                }
            });
        });

        btnRestart.setOnClickListener(v -> {
            showProcessing(btnRestart, "Restart");
            MainActivity.api.restartBot(botId).enqueue(new Callback<StatusResponse>() {
                public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) {
                    hideProcessing(btnRestart, R.color.warning);
                    db.updateBotStatus(botId, "running");
                    Toast.makeText(BotDetailActivity.this, "🔄 Restarted (auto-restart ON)", Toast.LENGTH_SHORT).show();
                }
                public void onFailure(Call<StatusResponse> c, Throwable t) {
                    hideProcessing(btnRestart, R.color.warning);
                    Toast.makeText(BotDetailActivity.this, "🔄 Restart failed", Toast.LENGTH_SHORT).show();
                }
            });
        });

        btnSleep.setOnClickListener(v -> {
            showProcessing(btnSleep, "Sleep");
            new Handler().postDelayed(() -> {
                db.toggleSleepMode(botId, true);
                hideProcessing(btnSleep, R.color.accent);
                Toast.makeText(this, "💤 Sleep mode ON", Toast.LENGTH_SHORT).show();
            }, 500);
        });

        btnDelete.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("🗑️ Delete Bot?")
                .setMessage("\"" + botName + "\" ko delete kar dein?")
                .setPositiveButton("Delete", (d, w) -> {
                    showProcessing(btnDelete, "Deleting");
                    MainActivity.api.deleteBot(botId).enqueue(new Callback<StatusResponse>() {
                        public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) {}
                        public void onFailure(Call<StatusResponse> c, Throwable t) {}
                    });
                    db.deleteBot(botId);
                    Toast.makeText(this, "🗑️ Deleted", Toast.LENGTH_SHORT).show();
                    finish();
                })
                .setNegativeButton("Cancel", null).show());

        btnLogs.setOnClickListener(v -> fetchLogs());

        // 🎯 10 second polling - real-time logs + status
        logRunnable = () -> { fetchLogs(); fetchStatus(); handler.postDelayed(logRunnable, POLL_INTERVAL); };
        handler.post(logRunnable);
    }

    void fetchLogs() {
        MainActivity.api.getLogs(botId).enqueue(new Callback<LogsResponse>() {
            public void onResponse(Call<LogsResponse> c, Response<LogsResponse> r) {
                if (r.isSuccessful() && r.body() != null) {
                    tvLogs.setText("> " + r.body().logs + "\n>");
                } else {
                    tvLogs.setText("> [no logs yet]\n>");
                }
            }
            public void onFailure(Call<LogsResponse> c, Throwable t) {
                tvLogs.setText("> 📡 backend offline\n> " + t.getMessage() + "\n>");
            }
        });
    }

    // 🎯 REAL status check
    void fetchStatus() {
        MainActivity.api.getBotStatus(botId).enqueue(new Callback<BotStatus>() {
            public void onResponse(Call<BotStatus> c, Response<BotStatus> r) {
                if (r.isSuccessful() && r.body() != null && tvStatusBadge != null) {
                    boolean alive = r.body().running;
                    boolean ar = r.body().auto_restart;
                    String text = alive ? "🟢 Running" : "🔴 Stopped";
                    if (ar) text += "  ♻️ Auto-Restart";
                    tvStatusBadge.setText(text);
                    tvStatusBadge.setTextColor(getColor(alive ? R.color.success : R.color.danger));
                    db.updateBotStatus(botId, alive ? "running" : "stopped");
                }
            }
            public void onFailure(Call<BotStatus> c, Throwable t) {}
        });
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(logRunnable);
    }
}
