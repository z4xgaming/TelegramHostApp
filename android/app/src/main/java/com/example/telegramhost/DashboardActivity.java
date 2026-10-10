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
    private static final int POLL_INTERVAL = 10000; // 10 seconds

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_dashboard);
        setupBottomNav(R.id.nav_bots);

        db = new DatabaseHelper(this);
        container = findViewById(R.id.container);
        Button btnRefresh = findViewById(R.id.btnRefresh);
        btnRefresh.setOnClickListener(v -> loadBots());

        // 🎯 10 second polling - REAL status
        refreshRunnable = () -> { loadBots(); refreshHandler.postDelayed(refreshRunnable, POLL_INTERVAL); };
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
            tv.setText("🤖 Koi bot nahi hai.\n🏠 Home se deploy karo.");
            tv.setTextColor(getColor(R.color.text_secondary));
            tv.setTextSize(15f);
            tv.setPadding(40, 60, 40, 40);
            tv.setGravity(android.view.Gravity.CENTER);
            container.addView(tv);
            c.close();
            return;
        }
        while (c.moveToNext()) {
            String id = c.getString(c.getColumnIndexOrThrow("id"));
            String name = c.getString(c.getColumnIndexOrThrow("name"));
            String dbStatus = c.getString(c.getColumnIndexOrThrow("status"));
            int sleep = c.getInt(c.getColumnIndexOrThrow("sleep_mode"));

            View card = LayoutInflater.from(this).inflate(R.layout.item_bot_card, container, false);
            TextView tvName = card.findViewById(R.id.tvBotName);
            TextView tvStatus = card.findViewById(R.id.tvBotStatus);
            Button btnStart = card.findViewById(R.id.btnStart);
            Button btnStop = card.findViewById(R.id.btnStop);
            Button btnRestart = card.findViewById(R.id.btnRestart);
            Button btnLogs = card.findViewById(R.id.btnLogs);
            Button btnDelete = card.findViewById(R.id.btnDelete);

            tvName.setText("🤖 " + name);

            // Local status pehle dikhao
            updateStatusText(tvStatus, dbStatus, sleep, false);

            // 🎯 REAL status backend se fetch karo
            MainActivity.api.getBotStatus(id).enqueue(new Callback<BotStatus>() {
                public void onResponse(Call<BotStatus> call, Response<BotStatus> r) {
                    if (r.isSuccessful() && r.body() != null) {
                        boolean alive = r.body().running;
                        String newStatus = alive ? "running" : "stopped";
                        if (!newStatus.equals(dbStatus)) {
                            db.updateBotStatus(id, newStatus);
                        }
                        updateStatusText(tvStatus, newStatus, sleep, true);
                    }
                }
                public void onFailure(Call<BotStatus> call, Throwable t) {
                    // Backend offline - local status dikhao
                }
            });

            btnStart.setOnClickListener(v -> {
                showProcessing(btnStart, "Starting");
                MainActivity.api.restartBot(id).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnStart, R.color.success);
                        db.updateBotStatus(id, "running");
                        Toast.makeText(DashboardActivity.this, "▶️ Started (auto-restart ON)", Toast.LENGTH_SHORT).show();
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnStart, R.color.success);
                        db.updateBotStatus(id, "running");
                        Toast.makeText(DashboardActivity.this, "▶️ Marked running", Toast.LENGTH_SHORT).show();
                    }
                });
            });

            btnStop.setOnClickListener(v -> {
                showProcessing(btnStop, "Stopping");
                MainActivity.api.stopBot(id).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnStop, R.color.danger);
                        db.updateBotStatus(id, "stopped");
                        Toast.makeText(DashboardActivity.this, "⏹️ Stopped", Toast.LENGTH_SHORT).show();
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnStop, R.color.danger);
                        db.updateBotStatus(id, "stopped");
                        Toast.makeText(DashboardActivity.this, "⏹️ Stopped (offline)", Toast.LENGTH_SHORT).show();
                    }
                });
            });

            btnRestart.setOnClickListener(v -> {
                showProcessing(btnRestart, "Restart");
                MainActivity.api.restartBot(id).enqueue(new Callback<StatusResponse>() {
                    public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {
                        hideProcessing(btnRestart, R.color.warning);
                        db.updateBotStatus(id, "running");
                        Toast.makeText(DashboardActivity.this, "🔄 Restarted", Toast.LENGTH_SHORT).show();
                    }
                    public void onFailure(Call<StatusResponse> call, Throwable t) {
                        hideProcessing(btnRestart, R.color.warning);
                        Toast.makeText(DashboardActivity.this, "🔄 Restart failed", Toast.LENGTH_SHORT).show();
                    }
                });
            });

            btnLogs.setOnClickListener(v -> {
                Intent i = new Intent(this, BotDetailActivity.class);
                i.putExtra("id", id); i.putExtra("name", name);
                startActivity(i);
            });

            btnDelete.setOnClickListener(v -> new AlertDialog.Builder(this)
                    .setTitle("🗑️ Delete Bot?")
                    .setMessage("\"" + name + "\" ko permanently delete kar dein?")
                    .setPositiveButton("Delete", (d, w) -> {
                        showProcessing(btnDelete, "Deleting");
                        MainActivity.api.deleteBot(id).enqueue(new Callback<StatusResponse>() {
                            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> r) {}
                            public void onFailure(Call<StatusResponse> call, Throwable t) {}
                        });
                        db.deleteBot(id);
                        new Handler().postDelayed(() -> {
                            Toast.makeText(this, "🗑️ Deleted", Toast.LENGTH_SHORT).show();
                            loadBots();
                        }, 500);
                    })
                    .setNegativeButton("Cancel", null).show());
            container.addView(card);
        }
        c.close();
    }

    // 🎯 REAL status display - green dot only if actually running
    void updateStatusText(TextView tv, String status, int sleep, boolean verified) {
        String statText;
        int color;
        if (status.equals("running")) {
            statText = verified ? "🟢 Running" : "🟡 Checking...";
            color = verified ? R.color.success : R.color.warning;
        } else if (status.equals("draft")) {
            statText = "📝 Draft";
            color = R.color.text_secondary;
        } else if (status.equals("offline")) {
            statText = "⚫ Offline";
            color = R.color.text_secondary;
        } else {
            statText = "🔴 Stopped";
            color = R.color.danger;
        }
        if (sleep == 1) statText += "   💤 Sleep";
        tv.setText(statText);
        tv.setTextColor(getColor(color));
    }
}
