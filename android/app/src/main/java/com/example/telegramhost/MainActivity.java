package com.example.telegramhost;
import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.*;
import retrofit2.converter.gson.GsonConverterFactory;
public class MainActivity extends AppCompatActivity {
    public static final String BASE_URL = "http://10.0.2.2:8000/";
    public static ApiService api;
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        api = new Retrofit.Builder().baseUrl(BASE_URL).addConverterFactory(GsonConverterFactory.create()).build().create(ApiService.class);
        EditText etName = findViewById(R.id.etName);
        EditText etToken = findViewById(R.id.etToken);
        EditText etCode = findViewById(R.id.etCode);
        Button btnDeploy = findViewById(R.id.btnDeploy);
        Button btnDash = findViewById(R.id.btnDashboard);
        btnDeploy.setOnClickListener(v -> {
            String n = etName.getText().toString(), t = etToken.getText().toString(), c = etCode.getText().toString();
            if (n.isEmpty() || t.isEmpty() || c.isEmpty()) { Toast.makeText(this,"Sab fields bharo",Toast.LENGTH_SHORT).show(); return; }
            api.createBot(new BotRequest(n,t,c)).enqueue(new Callback<BotResponse>() {
                public void onResponse(Call<BotResponse> call, Response<BotResponse> r) {
                    Toast.makeText(MainActivity.this, r.isSuccessful()?"Bot Deployed ✅":"Error: "+r.code(), Toast.LENGTH_SHORT).show();
                }
                public void onFailure(Call<BotResponse> call, Throwable t) {
                    Toast.makeText(MainActivity.this, "Network: "+t.getMessage(), Toast.LENGTH_LONG).show();
                }
            });
        });
        btnDash.setOnClickListener(v -> startActivity(new Intent(this, DashboardActivity.class)));
    }
}
