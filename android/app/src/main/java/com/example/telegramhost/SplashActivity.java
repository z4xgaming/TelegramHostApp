package com.example.telegramhost;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class SplashActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_splash);

        ImageView logo = findViewById(R.id.logo);
        TextView title = findViewById(R.id.title);

        Animation fadeIn = AnimationUtils.loadAnimation(this, android.R.anim.fade_in);
        fadeIn.setDuration(1200);
        logo.startAnimation(fadeIn);
        title.startAnimation(fadeIn);

        new Handler().postDelayed(() -> {
            DatabaseHelper db = new DatabaseHelper(this);
            String session = db.getSession();
            Intent i;
            if (session != null && !session.equals("__session__")) {
                i = new Intent(this, MainActivity.class);
            } else {
                i = new Intent(this, LoginActivity.class);
            }
            startActivity(i);
            finish();
        }, 2200);
    }
}
