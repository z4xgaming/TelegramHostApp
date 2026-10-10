package com.example.telegramhost;

import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.bottomnavigation.BottomNavigationView;

public class BaseActivity extends AppCompatActivity {
    protected void setupBottomNav(int selected) {
        BottomNavigationView nav = findViewById(R.id.bottomNav);
        if (nav == null) return;
        nav.setSelectedItemId(selected);
        nav.setOnItemSelectedListener(item -> {
            int id = item.getItemId();
            if (id == selected) return true;
            Class<?> target = null;
            if (id == R.id.nav_home) target = MainActivity.class;
            else if (id == R.id.nav_bots) target = DashboardActivity.class;
            else if (id == R.id.nav_logs) target = LogsActivity.class;
            else if (id == R.id.nav_settings) target = SettingsActivity.class;
            if (target != null) {
                startActivity(new Intent(this, target));
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
            }
            return true;
        });
    }

    protected void showProcessing(Button btn, String label) {
        btn.setTag(btn.getText().toString());
        btn.setEnabled(false);
        btn.setText("⬛ " + label + "...");
        btn.setBackgroundTintList(ColorStateList.valueOf(Color.BLACK));
    }

    protected void hideProcessing(Button btn, int colorRes) {
        btn.setEnabled(true);
        if (btn.getTag() != null) btn.setText(btn.getTag().toString());
        btn.setBackgroundTintList(ColorStateList.valueOf(getColor(colorRes)));
    }
}
