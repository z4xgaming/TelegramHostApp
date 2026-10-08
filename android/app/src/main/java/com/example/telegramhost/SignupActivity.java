package com.example.telegramhost;

import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;

public class SignupActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_signup);

        EditText etFname = findViewById(R.id.etFname);
        EditText etLname = findViewById(R.id.etLname);
        EditText etEmail = findViewById(R.id.etEmail);
        EditText etPass = findViewById(R.id.etPassword);
        Button btnSignup = findViewById(R.id.btnSignup);
        TextView tvLogin = findViewById(R.id.tvLogin);

        DatabaseHelper db = new DatabaseHelper(this);

        btnSignup.setOnClickListener(v -> {
            String f = etFname.getText().toString().trim();
            String l = etLname.getText().toString().trim();
            String e = etEmail.getText().toString().trim();
            String p = etPass.getText().toString();
            if (f.isEmpty() || e.isEmpty() || p.length() < 4) {
                Toast.makeText(this, "Sab fields bharo (password 4+ chars)", Toast.LENGTH_SHORT).show();
                return;
            }
            if (db.signup(e, p, f, l)) {
                db.saveSession(e);
                Toast.makeText(this, "Account ban gaya! ✅", Toast.LENGTH_SHORT).show();
                startActivity(new Intent(this, MainActivity.class));
                finishAffinity();
            } else {
                Toast.makeText(this, "❌ Email already registered", Toast.LENGTH_SHORT).show();
            }
        });

        tvLogin.setOnClickListener(v -> finish());
    }
}
