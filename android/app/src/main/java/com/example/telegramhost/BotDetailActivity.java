package com.example.telegramhost;

import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;

public class BotDetailActivity extends BaseActivity {
    private DatabaseHelper db;
    private String botId, botName;
    private TextView tvLogs, tvStatusBadge;
    private Handler handler = new Handler();
    private Runnable logRunnable;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_detail);
        setupBottomNav(R.id.nav_bots);

        db = new DatabaseHelper(this);
        botId = getIntent().getStringExtra("id");
        botName = getIntent().getStringExtra("name");
        if (botName == null) botName = "Bot";

        ((TextView) findViewById(R.id.tvName)).setText("🤖 " + botName);
        tvLogs = findViewById(R.id.tvLogs);
        tvStatusBadge = findViewById(R.id.tvStatusBadge);

        Button btnStop = findViewById(R.id.btnStop);
        Button btnRestart = findViewById(R.id.btnRestart);
        Button btnSleep = findViewById(R.id.btnSleep);
        Button btnDelete = findViewById(R.id.btnDelete);
        Button btnLogs = findViewById(R.id.btnLogs);

        btnStop.setOnClickListener(v -> {
            showProcessing(btnStop, "Stopping");
            String r = PythonBridge.stopBot();
            new Handler().postDelayed(() -> {
                hideProcessing(btnStop, R.color.danger);
                Toast.makeText(this, "⏹️ " + r, Toast.LENGTH_SHORT).show();
            }, 500);
        });

        btnRestart.setOnClickListener(v -> {
            Toast.makeText(this, "Deploy again from Home", Toast.LENGTH_SHORT).show();
        });

        btnSleep.setOnClickListener(v -> {
            Toast.makeText(this, "💤 Sleep mode", Toast.LENGTH_SHORT).show();
        });

        btnDelete.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("🗑️ Delete?")
                .setMessage("Delete \"" + botName + "\"?")
                .setPositiveButton("Delete", (d, w) -> {
                    PythonBridge.stopBot();
                    db.deleteBot(botId);
                    finish();
                })
                .setNegativeButton("Cancel", null).show());

        btnLogs.setOnClickListener(v -> fetchLogs());

        logRunnable = () -> { fetchLogs(); fetchStatus(); handler.postDelayed(logRunnable, 2000); };
        handler.post(logRunnable);
    }

    void fetchLogs() {
        String logs = PythonBridge.getLogs();
        tvLogs.setText(logs.isEmpty() ? "> Waiting for logs...\n>" : "> " + logs.replace("\n", "\n> "));
    }

    void fetchStatus() {
        boolean running = PythonBridge.isRunning();
        String text = running ? "🟢 Running (in-app)" : "🔴 Stopped";
        tvStatusBadge.setText(text);
        tvStatusBadge.setTextColor(getColor(running ? R.color.success : R.color.danger));
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(logRunnable);
    }
}
