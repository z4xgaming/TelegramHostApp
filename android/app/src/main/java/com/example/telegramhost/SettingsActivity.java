package com.example.telegramhost;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;

public class SettingsActivity extends BaseActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_settings);
        setupBottomNav(R.id.nav_settings);

        TextView tvResult = findViewById(R.id.tvTestResult);
        Button btnTest = findViewById(R.id.btnTestLibs);
        btnTest.setOnClickListener(v -> {
            showProcessing(btnTest, "Testing");
            new Thread(() -> {
                String result = PythonBridge.testLibraries();
                runOnUiThread(() -> {
                    hideProcessing(btnTest, R.color.success);
                    tvResult.setText(result);
                });
            }).start();
        });

        Button btnShare = findViewById(R.id.btnShareApp);
        btnShare.setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_TEXT, "🚀 Telegram Host App\nhttps://github.com/z4xgaming/TelegramHostApp");
            startActivity(Intent.createChooser(i, "Share"));
        });

        Button btnProfile = findViewById(R.id.btnProfile);
        btnProfile.setOnClickListener(v -> startActivity(new Intent(this, ProfileActivity.class)));

        Button btnLogout = findViewById(R.id.btnLogout);
        btnLogout.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("🚪 Logout?")
                .setPositiveButton("Yes", (d, w) -> {
                    new DatabaseHelper(this).clearSession();
                    startActivity(new Intent(this, LoginActivity.class));
                    finishAffinity();
                })
                .setNegativeButton("Cancel", null).show());
    }
}
