package com.example.telegramhost;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.os.Handler;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;

public class DashboardActivity extends AppCompatActivity {
    private DatabaseHelper db;
    private LinearLayout container;
    private Handler refreshHandler = new Handler();
    private Runnable refreshRunnable;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_dashboard);
        db = new DatabaseHelper(this);
        container = findViewById(R.id.container);
        Button btnRefresh = findViewById(R.id.btnRefresh);
        Button btnHome = findViewById(R.id.btnHome);

        btnRefresh.setOnClickListener(v -> loadBots());
        btnHome.setOnClickListener(v -> finish());

        // Auto-refresh every 5 seconds
        refreshRunnable = () -> { loadBots(); refreshHandler.postDelayed(refreshRunnable, 5000); };
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
            tv.setText("🤖 Koi bot nahi hai. Home se deploy karo.");
            tv.setTextColor(getColor(R.color.text_secondary));
            tv.setPadding(40, 40, 40, 40);
            container.addView(tv);
        }
        while (c.moveToNext()) {
            String id = c.getString(c.getColumnIndexOrThrow("id"));
            String name = c.getString(c.getColumnIndexOrThrow("name"));
            String status = c.getString(c.getColumnIndexOrThrow("status"));
            int sleep = c.getInt(c.getColumnIndexOrThrow("sleep_mode"));

            View card = LayoutInflater.from(this).inflate(R.layout.item_bot_card, container, false);
            TextView tvName = card.findViewById(R.id.tvBotName);
            TextView tvStatus = card.findViewById(R.id.tvBotStatus);
            TextView tvSleep = card.findViewById(R.id.tvSleep);

            tvName.setText("🤖 " + name);
            tvStatus.setText(status.equals("running") ? "● Online" : "● Offline");
            tvStatus.setTextColor(getColor(status.equals("running") ? R.color.success : R.color.danger));
            tvSleep.setVisibility(sleep == 1 ? View.VISIBLE : View.GONE);

            card.setOnClickListener(v -> {
                Intent i = new Intent(this, BotDetailActivity.class);
                i.putExtra("id", id); i.putExtra("name", name);
                startActivity(i);
            });
            container.addView(card);
        }
        c.close();
    }
}
