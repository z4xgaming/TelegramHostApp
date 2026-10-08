package com.example.telegramhost;
import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.*;
public class DashboardActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_dashboard);
        LinearLayout container = findViewById(R.id.container);
        Button btnRefresh = findViewById(R.id.btnRefresh);
        btnRefresh.setOnClickListener(v -> loadBots(container));
        loadBots(container);
    }
    void loadBots(LinearLayout container) {
        container.removeAllViews();
        MainActivity.api.listBots().enqueue(new Callback<BotsList>() {
            public void onResponse(Call<BotsList> c, Response<BotsList> r) {
                if (r.isSuccessful() && r.body() != null && r.body().bots != null) {
                    for (BotInfo bot : r.body().bots) {
                        TextView tv = new TextView(DashboardActivity.this);
                        tv.setText("🤖 " + bot.name + " [" + bot.status + "]");
                        tv.setTextSize(18f); tv.setPadding(30,30,30,30);
                        tv.setOnClickListener(x -> {
                            Intent i = new Intent(DashboardActivity.this, BotDetailActivity.class);
                            i.putExtra("id", bot.id); i.putExtra("name", bot.name);
                            startActivity(i);
                        });
                        container.addView(tv);
                    }
                }
            }
            public void onFailure(Call<BotsList> c, Throwable t) {
                Toast.makeText(DashboardActivity.this,"Error: "+t.getMessage(),Toast.LENGTH_SHORT).show();
            }
        });
    }
}
