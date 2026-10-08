package com.example.telegramhost;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.*;
public class BotDetailActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_detail);
        String id = getIntent().getStringExtra("id");
        String name = getIntent().getStringExtra("name");
        ((TextView)findViewById(R.id.tvName)).setText("🤖 " + name);
        Button btnStop = findViewById(R.id.btnStop), btnRestart = findViewById(R.id.btnRestart),
               btnLogs = findViewById(R.id.btnLogs), btnDelete = findViewById(R.id.btnDelete);
        TextView tvLogs = findViewById(R.id.tvLogs);
        btnStop.setOnClickListener(v -> MainActivity.api.stopBot(id).enqueue(toast("Stopped")));
        btnRestart.setOnClickListener(v -> MainActivity.api.restartBot(id).enqueue(toast("Restarted")));
        btnLogs.setOnClickListener(v -> MainActivity.api.getLogs(id).enqueue(new Callback<LogsResponse>() {
            public void onResponse(Call<LogsResponse> c, Response<LogsResponse> r) { tvLogs.setText(r.body()!=null?r.body().logs:"No logs"); }
            public void onFailure(Call<LogsResponse> c, Throwable t) { tvLogs.setText("Error: "+t.getMessage()); }
        }));
        btnDelete.setOnClickListener(v -> { MainActivity.api.deleteBot(id).enqueue(toast("Deleted")); finish(); });
    }
    Callback<StatusResponse> toast(String msg) {
        return new Callback<StatusResponse>() {
            public void onResponse(Call<StatusResponse> c, Response<StatusResponse> r) { Toast.makeText(BotDetailActivity.this,msg,Toast.LENGTH_SHORT).show(); }
            public void onFailure(Call<StatusResponse> c, Throwable t) { Toast.makeText(BotDetailActivity.this,"Error",Toast.LENGTH_SHORT).show(); }
        };
    }
}
