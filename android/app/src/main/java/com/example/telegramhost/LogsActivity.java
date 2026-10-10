package com.example.telegramhost;

import android.database.Cursor;
import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import retrofit2.*;

public class LogsActivity extends BaseActivity {
    private DatabaseHelper db;
    private TextView tvLogs;
    private Handler handler = new Handler();
    private Runnable refresh;
    private StringBuilder allLogs;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_logs);
        setupBottomNav(R.id.nav_logs);

        db = new DatabaseHelper(this);
        tvLogs = findViewById(R.id.tvAllLogs);
        Button btnRefresh = findViewById(R.id.btnRefreshLogs);
        btnRefresh.setOnClickListener(v -> loadAllLogs());

        refresh = () -> { loadAllLogs(); handler.postDelayed(refresh, 6000); };
        handler.post(refresh);
    }

    void loadAllLogs() {
        allLogs = new StringBuilder("> All bots logs\n> " + new java.util.Date() + "\n> ------------\n");
        Cursor c = db.getAllBots();
        int count = 0;
        while (c.moveToNext()) {
            count++;
            String id = c.getString(c.getColumnIndexOrThrow("id"));
            String name = c.getString(c.getColumnIndexOrThrow("name"));
            allLogs.append("> 🤖 ").append(name).append("\n");
            MainActivity.api.getLogs(id).enqueue(new Callback<LogsResponse>() {
                public void onResponse(Call<LogsResponse> call, Response<LogsResponse> r) {
                    if (r.isSuccessful() && r.body() != null) {
                        allLogs.append(r.body().logs).append("\n\n");
                    } else {
                        allLogs.append("  [no logs]\n\n");
                    }
                    tvLogs.setText(allLogs.toString());
                }
                public void onFailure(Call<LogsResponse> call, Throwable t) {
                    allLogs.append("  [backend offline]\n\n");
                    tvLogs.setText(allLogs.toString());
                }
            });
        }
        c.close();
        if (count == 0) {
            tvLogs.setText("> Koi bot nahi hai\n> Pehle Home se bot deploy karo");
        } else {
            tvLogs.setText(allLogs.toString());
        }
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacks(refresh);
    }
}
