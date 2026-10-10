package com.example.telegramhost;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.os.Handler;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;

public class DashboardActivity extends BaseActivity {
    private DatabaseHelper db;
    private LinearLayout container;
    private Handler refreshHandler = new Handler();
    private Runnable refreshRunnable;
    private static final int POLL = 3000;

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
            tv.setTextSize(15f); tv.setPadding(40, 60, 40, 40);
            tv.setGravity(android.view.Gravity.CENTER);
            container.addView(tv); c.close(); return;
        }
        while (c.moveToNext()) {
            final String id = c.getString(c.getColumnIndexOrThrow("id"));
            final String name = c.getString(c.getColumnIndexOrThrow("name"));

            View card = LayoutInflater.from(this).inflate(R.layout.item_bot_card, container, false);
            TextView tvName = card.findViewById(R.id.tvBotName);
            TextView tvStatus = card.findViewById(R.id.tvBotStatus);
            Button btnStart = card.findViewById(R.id.btnStart);
            Button btnStop = card.findViewById(R.id.btnStop);
            Button btnRestart = card.findViewById(R.id.btnRestart);
            Button btnLogs = card.findViewById(R.id.btnLogs);
            Button btnDelete = card.findViewById(R.id.btnDelete);

            tvName.setText("🤖 " + name);

            // 🐍 In-app Python bot status check
            boolean running = PythonBridge.isRunning();
            if (running) {
                tvStatus.setText("🟢 Running (in-app)");
                tvStatus.setTextColor(getColor(R.color.success));
            } else {
                tvStatus.setText("🔴 Stopped");
                tvStatus.setTextColor(getColor(R.color.danger));
            }

            btnStart.setOnClickListener(v -> {
                Toast.makeText(this, "Bot Home se deploy karo", Toast.LENGTH_SHORT).show();
            });

            btnStop.setOnClickListener(v -> {
                showProcessing(btnStop, "Stopping");
                String r = PythonBridge.stopBot();
                new Handler().postDelayed(() -> {
                    hideProcessing(btnStop, R.color.danger);
                    Toast.makeText(DashboardActivity.this, "⏹️ " + r, Toast.LENGTH_SHORT).show();
                    loadBots();
                }, 500);
            });

            btnRestart.setOnClickListener(v -> {
                Toast.makeText(this, "Deploy again from Home", Toast.LENGTH_SHORT).show();
            });

            btnLogs.setOnClickListener(v -> {
                Intent i = new Intent(this, BotDetailActivity.class);
                i.putExtra("id", id); i.putExtra("name", name);
                startActivity(i);
            });

            btnDelete.setOnClickListener(v -> new AlertDialog.Builder(this)
                    .setTitle("🗑️ Delete Bot?")
                    .setMessage("\"" + name + "\" delete karein?")
                    .setPositiveButton("Delete", (d, w) -> {
                        PythonBridge.stopBot();
                        db.deleteBot(id);
                        new Handler().postDelayed(() -> loadBots(), 500);
                    })
                    .setNegativeButton("Cancel", null).show());

            container.addView(card);
        }
        c.close();
    }
}
