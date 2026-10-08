package com.example.telegramhost;

import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_login);

        EditText etEmail = findViewById(R.id.etEmail);
        EditText etPass = findViewById(R.id.etPassword);
        Button btnLogin = findViewById(R.id.btnLogin);
        TextView tvSignup = findViewById(R.id.tvSignup);

        DatabaseHelper db = new DatabaseHelper(this);

        btnLogin.setOnClickListener(v -> {
            String e = etEmail.getText().toString().trim();
            String p = etPass.getText().toString();
            if (e.isEmpty() || p.isEmpty()) {
                Toast.makeText(this, "Sab fields bharo", Toast.LENGTH_SHORT).show();
                return;
            }
            if (db.login(e, p)) {
                db.saveSession(e);
                Toast.makeText(this, "Welcome back! ✅", Toast.LENGTH_SHORT).show();
                startActivity(new Intent(this, MainActivity.class));
                finish();
            } else {
                Toast.makeText(this, "❌ Galat email ya password", Toast.LENGTH_SHORT).show();
            }
        });

        tvSignup.setOnClickListener(v -> startActivity(new Intent(this, SignupActivity.class)));
    }
}
