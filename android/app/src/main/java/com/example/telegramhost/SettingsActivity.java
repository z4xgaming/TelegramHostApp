package com.example.telegramhost;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;

public class SettingsActivity extends BaseActivity {
    private SharedPreferences prefs;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_settings);
        setupBottomNav(R.id.nav_settings);

        prefs = getSharedPreferences("env", MODE_PRIVATE);
        EditText etId = findViewById(R.id.etApiId);
        EditText etHash = findViewById(R.id.etApiHash);
        etId.setText(prefs.getString("API_ID", ""));
        etHash.setText(prefs.getString("API_HASH", ""));

        Button btnSave = findViewById(R.id.btnSaveEnv);
        btnSave.setOnClickListener(v -> {
            showProcessing(btnSave, "Saving");
            new Handler().postDelayed(() -> {
                prefs.edit()
                        .putString("API_ID", etId.getText().toString())
                        .putString("API_HASH", etHash.getText().toString())
                        .apply();
                hideProcessing(btnSave, R.color.success);
                Toast.makeText(this, "✅ Env saved", Toast.LENGTH_SHORT).show();
            }, 600);
        });

        Button btnShare = findViewById(R.id.btnShareApp);
        btnShare.setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_TEXT, "🚀 Try Telegram Host App - Host your bots!\nhttps://github.com/z4xgaming/TelegramHostApp");
            startActivity(Intent.createChooser(i, "Share via"));
        });

        Button btnProfile = findViewById(R.id.btnProfile);
        btnProfile.setOnClickListener(v -> startActivity(new Intent(this, ProfileActivity.class)));

        Button btnLogout = findViewById(R.id.btnLogout);
        btnLogout.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("🚪 Logout?")
                .setMessage("Kya tum logout karna chahte ho?")
                .setPositiveButton("Yes", (d, w) -> {
                    new DatabaseHelper(this).clearSession();
                    startActivity(new Intent(this, LoginActivity.class));
                    finishAffinity();
                })
                .setNegativeButton("Cancel", null).show());
    }
}
