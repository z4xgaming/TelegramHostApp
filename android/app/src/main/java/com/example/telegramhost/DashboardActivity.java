package com.example.telegramhost;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.os.Handler;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;
import retrofit2.*;

public class DashboardActivity extends BaseActivity {
    private DatabaseHelper db;
    private LinearLayout container;
    private Handler refreshHandler = new Handler();
    private Runnable refreshRunnable;
    private static final int POLL = 5000; // 5s faster polling

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_dashboard);
        setupBottomNav(R.id.nav_bots);
        db = new DatabaseHelper(this);
        container = findViewById(R.id.container);
        findViewById(R.id.btnRefresh).setOnClickListener(v -> loadBots());
        refreshRunnable = () -> { loadBots(); refreshHandler.postDelayed(refreshRunnable, POLL); };
        refreshHandler.post(refreshRunnable);
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        refreshHandler.removeCallbacks(refreshRunnable);
    }

    void loadBots() {
        container.removeAllViews();
        Cursor c = db.getAllBots();
        if (c.getCount() == 0) {
            TextView tv = new TextView(this);
            tv.setText("🤖 Koi bot nahi\n🏠 Home se deploy karo");
            tv.setTextColor(getColor(R.color.text_secondary));
            tv.setTextSize(15f);
            tv.setPadding(40, 60, 40, 40);
            tv.setGravity(android.view.Gravity.CENTER);
            container.addView(tv); c.close(); return;
        }
        while (c.moveToNext()) {
            String id = c.getString(c.getColumnIndexOrThrow("id"));
            String name = c.getString(c.getColumnIndexOrThrow("name"));

            View card = LayoutInflater.from(this).inflate(R.layout.item_bot_card, container, false);
            TextView tvName = card.findViewById(R.id.tvBotName);
            TextView tvStatus = card.findViewById(R.id.tvBotStatus);
            Button btnStart = card.findViewById(R.id.btnStart);
            Button btnStop = card.findViewById(R.id.btnStop);
            Button btnRestart = card.findViewById(R.id.btnRestart);
            Button btnLogs = card.findViewById(R.id.btnLogs);
            Button btnDelete = card.findViewById(R.id.btnDelete);

            tvName.setText("🤖 " + name);
            tvStatus.setText("🟡 Checking...");
            tvStatus.setTextColor(getColor(R.color.warning));

            final String botId = id;
            final View cardRef = card;

            MainActivity.api.getBotStatus(botId).enqueue(new Callback<BotStatus>() {
                public void onResponse(Call<BotStatus> call, Response<BotStatus> r) {
                    if (r.isSuccessful() && r.body() != null) {
                        BotStatus s = r.body();
                        if (s.installing) {
                            tvStatus.setText("📦 Installing libraries...");
                            tvStatus.setTextColor(getColor(R.color.accent));
                        } else if (s.running) {
                            String txt = "🟢 Running";
                            if (s.auto_restart) txt += "  ♻️";
                            tvStatus.setText(txt);
                            tvStatus.setTextColor(getColor(R.color.success));
                        } else if (s.status.equals("waiting")) {
                            tvStatus.setText("🟡 Waiting...");
                            tvStatus.setTextColor(getColor(R.color.warning));
                        } else {
                            String txt = "🔴 Stopped";
                            if (s.exit_code != null && s.exit_code != 0) txt += " (code " + s.exit_code + ")";
                            tvStatus.setText(txt);
                            tvStatus.setTextColor(getColor(R.color.danger));
                        }
                        db.updateBotStatus(botId, s.running ? "running" : "stopped");
                    }
                }
                public void onFailure(Call<BotStatus> call, Throwable t) {
                    tvStatus.setText("⚫ Offline (backend)");
                    tvStatus.setTextColor(getColor(R.color.text_secondary));
                }
            });

            btnStart.setOnClickListener(v -> {
                showProcessing(btnStart, "Starting");
                MainActivity.api.restartBot(botId).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnStart, R.color.success);
                        Toast.makeText(DashboardActivity.this, "▶️ Start signal sent", Toast.LENGTH_SHORT).show();
                        new Handler().postDelayed(() -> loadBots(), 2000);
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnStart, R.color.success);
                        Toast.makeText(DashboardActivity.this, "❌ Backend offline!\nPehle backend chalao", Toast.LENGTH_LONG).show();
                    }
                });
            });

            btnStop.setOnClickListener(v -> {
                showProcessing(btnStop, "Stopping");
                MainActivity.api.stopBot(botId).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnStop, R.color.danger);
                        Toast.makeText(DashboardActivity.this, "⏹️ Stopped", Toast.LENGTH_SHORT).show();
                        new Handler().postDelayed(() -> loadBots(), 2000);
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnStop, R.color.danger);
                        Toast.makeText(DashboardActivity.this, "❌ Backend offline", Toast.LENGTH_SHORT).show();
                    }
                });
            });

            btnRestart.setOnClickListener(v -> {
                showProcessing(btnRestart, "Restart");
                MainActivity.api.restartBot(botId).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnRestart, R.color.warning);
                        Toast.makeText(DashboardActivity.this, "🔄 Restarting", Toast.LENGTH_SHORT).show();
                        new Handler().postDelayed(() -> loadBots(), 3000);
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnRestart, R.color.warning);
                        Toast.makeText(DashboardActivity.this, "❌ Backend offline", Toast.LENGTH_SHORT).show();
                    }
                });
            });

            btnLogs.setOnClickListener(v -> {
                Intent i = new Intent(this, BotDetailActivity.class);
                i.putExtra("id", botId); i.putExtra("name", name);
                startActivity(i);
            });

            btnDelete.setOnClickListener(v -> new AlertDialog.Builder(this)
                    .setTitle("🗑️ Delete Bot?")
                    .setMessage("\"" + name + "\" delete karein?")
                    .setPositiveButton("Delete", (d, w) -> {
                        MainActivity.api.deleteBot(botId).enqueue(new Callback<StatusResponse>() {
                            public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) {}
                            public void onFailure(Call<StatusResponse> c, Throwable t) {}
                        });
                        db.deleteBot(botId);
                        new Handler().postDelayed(() -> loadBots(), 500);
                    })
                    .setNegativeButton("Cancel", null).show());

            container.addView(card);
        }
        c.close();
    }
}
