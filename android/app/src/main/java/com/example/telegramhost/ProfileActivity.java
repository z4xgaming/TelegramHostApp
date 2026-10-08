package com.example.telegramhost;

import android.content.Intent;
import android.database.Cursor;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;

public class ProfileActivity extends AppCompatActivity {
    private DatabaseHelper db;
    private String email;
    private ImageView ivProfile;
    private ImageView btnCamera;
    private ActivityResultLauncher<Intent> picker;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_profile);

        db = new DatabaseHelper(this);
        email = db.getSession();

        ivProfile = findViewById(R.id.ivProfile);
        btnCamera = findViewById(R.id.btnCamera);
        TextView tvName = findViewById(R.id.tvName);
        TextView tvEmail = findViewById(R.id.tvEmail);
        Button btnLogout = findViewById(R.id.btnLogout);

        if (email != null) {
            Cursor c = db.getUser(email);
            if (c.moveToFirst()) {
                tvName.setText(c.getString(c.getColumnIndexOrThrow("first_name")) + " " +
                        c.getString(c.getColumnIndexOrThrow("last_name")));
                tvEmail.setText(email);
                String pic = c.getString(c.getColumnIndexOrThrow("profile_pic"));
                if (pic != null && !pic.isEmpty()) {
                    ivProfile.setImageBitmap(BitmapFactory.decodeFile(pic));
                    btnCamera.setVisibility(android.view.View.GONE); // 🎯 Camera gayab
                }
            }
            c.close();
        }

        // Photo picker
        picker = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                        Uri uri = result.getData().getData();
                        try {
                            InputStream is = getContentResolver().openInputStream(uri);
                            File f = new File(getFilesDir(), "profile_" + email + ".jpg");
                            FileOutputStream fos = new FileOutputStream(f);
                            byte[] buf = new byte[4096];
                            int len;
                            while ((len = is.read(buf)) > 0) fos.write(buf, 0, len);
                            fos.close(); is.close();
                            db.updateProfilePic(email, f.getAbsolutePath());
                            ivProfile.setImageBitmap(BitmapFactory.decodeFile(f.getAbsolutePath()));
                            btnCamera.setVisibility(android.view.View.GONE);
                            Toast.makeText(this, "Photo set ✅", Toast.LENGTH_SHORT).show();
                        } catch (Exception e) {
                            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                        }
                    }
                });

        btnCamera.setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            picker.launch(i);
        });

        btnLogout.setOnClickListener(v -> {
            db.clearSession();
            startActivity(new Intent(this, LoginActivity.class));
            finishAffinity();
        });
    }
}
