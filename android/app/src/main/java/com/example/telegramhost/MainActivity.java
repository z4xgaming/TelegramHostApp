package com.example.telegramhost;

import android.Manifest;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.widget.*;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.content.ContextCompat;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class MainActivity extends BaseActivity {
    // Ab backend ki zaroorat nahi, lekin ApiService reference rakhna hai
    public static ApiService api = null;
    public static final String BASE_URL = "in-app";  // Python in-app
    private String uploadedCode = null;
    private ActivityResultLauncher<String> filePicker;
    private ActivityResultLauncher<String[]> permLauncher;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        setupBottomNav(R.id.nav_home);

        // 🐍 Python initialize karo
        PythonBridge.init(this);

        requestAllPermissions();

        EditText etToken = findViewById(R.id.etToken);
        EditText etName = findViewById(R.id.etName);
        EditText etCode = findViewById(R.id.etCode);
        TextView tvDetect = findViewById(R.id.tvDetect);
        TextView tvUploaded = findViewById(R.id.tvUploadedFile);
        Button btnDetect = findViewById(R.id.btnDetect);
        Button btnUpload = findViewById(R.id.btnUpload);
        Button btnDeploy = findViewById(R.id.btnDeploy);
        Button btnDraft = findViewById(R.id.btnSaveDraft);

        DatabaseHelper db = new DatabaseHelper(this);

        filePicker = registerForActivityResult(
                new ActivityResultContracts.GetContent(),
                uri -> {
                    if (uri != null) {
                        try {
                            uploadedCode = readFile(uri);
                            tvUploaded.setText("✅ File loaded: " + uploadedCode.length() + " chars");
                            tvUploaded.setTextColor(getColor(R.color.success));
                        } catch (Exception e) {
                            tvUploaded.setText("❌ " + e.getMessage());
                            tvUploaded.setTextColor(getColor(R.color.danger));
                        }
                    }
                });

        btnUpload.setOnClickListener(v -> filePicker.launch("*/*"));

        btnDetect.setOnClickListener(v -> {
            String token = etToken.getText().toString().trim();
            if (token.isEmpty()) { Toast.makeText(this, "Token daalo", Toast.LENGTH_SHORT).show(); return; }
            showProcessing(btnDetect, "Detecting");
            tvDetect.setText("🔍 Detecting...");
            TelegramApi.detectBot(token, new TelegramApi.BotInfoCallback() {
                @Override public void onResult(String name, String username, String id) {
                    runOnUiThread(() -> {
                        hideProcessing(btnDetect, R.color.accent);
                        etName.setText(name);
                        tvDetect.setText("✅ @" + username + " (ID: " + id + ")");
                        tvDetect.setTextColor(getColor(R.color.success));
                    });
                }
                @Override public void onError(String error) {
                    runOnUiThread(() -> {
                        hideProcessing(btnDetect, R.color.accent);
                        tvDetect.setText("❌ " + error);
                        tvDetect.setTextColor(getColor(R.color.danger));
                    });
                }
            });
        });

        btnDeploy.setOnClickListener(v -> {
            String n = etName.getText().toString();
            String t = etToken.getText().toString();
            String c = uploadedCode != null ? uploadedCode : etCode.getText().toString();
            if (n.isEmpty() || t.isEmpty() || c.isEmpty()) {
                Toast.makeText(this, "Sab fields bharo ya file upload karo", Toast.LENGTH_SHORT).show();
                return;
            }
            showProcessing(btnDeploy, "Deploying");

            final String code = c;
            // 🐍 Python bot start karo (in-app)
            new Thread(() -> {
                String result = PythonBridge.startBot(code, t);
                runOnUiThread(() -> {
                    hideProcessing(btnDeploy, R.color.primary);
                    if (result.equals("started")) {
                        db.saveBot("app_" + System.currentTimeMillis(), n, t, code, "running");
                        Toast.makeText(MainActivity.this, "🚀 Bot started in-app!", Toast.LENGTH_LONG).show();
                    } else if (result.equals("already_running")) {
                        Toast.makeText(MainActivity.this, "⚠️ Bot already running", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this, "❌ " + result, Toast.LENGTH_LONG).show();
                    }
                });
            }).start();
        });

        btnDraft.setOnClickListener(v -> {
            String n = etName.getText().toString();
            String t = etToken.getText().toString();
            String c = uploadedCode != null ? uploadedCode : etCode.getText().toString();
            if (n.isEmpty() && c.isEmpty()) { Toast.makeText(this, "Kuch to likho", Toast.LENGTH_SHORT).show(); return; }
            showProcessing(btnDraft, "Saving");
            new Handler().postDelayed(() -> {
                db.saveBot("draft_" + System.currentTimeMillis(), n.isEmpty() ? "Draft Bot" : n, t, c, "draft");
                hideProcessing(btnDraft, R.color.text_secondary);
                Toast.makeText(this, "💾 Draft saved", Toast.LENGTH_SHORT).show();
            }, 700);
        });
    }

    private String readFile(Uri uri) throws IOException {
        InputStream is = getContentResolver().openInputStream(uri);
        String path = uri.getPath() != null ? uri.getPath().toLowerCase() : "";
        StringBuilder sb = new StringBuilder();
        if (path.endsWith(".zip")) {
            ZipInputStream zis = new ZipInputStream(is);
            ZipEntry e;
            while ((e = zis.getNextEntry()) != null) {
                if (e.getName().endsWith(".py")) {
                    BufferedReader br = new BufferedReader(new InputStreamReader(zis));
                    String l;
                    while ((l = br.readLine()) != null) sb.append(l).append("\n");
                }
            }
            zis.close();
        } else {
            BufferedReader br = new BufferedReader(new InputStreamReader(is));
            String l;
            while ((l = br.readLine()) != null) sb.append(l).append("\n");
            br.close();
        }
        return sb.toString();
    }

    private void requestAllPermissions() {
        List<String> perms = new ArrayList<>();
        perms.add(Manifest.permission.INTERNET);
        perms.add(Manifest.permission.ACCESS_NETWORK_STATE);
        perms.add(Manifest.permission.CAMERA);
        if (Build.VERSION.SDK_INT >= 33) {
            perms.add(Manifest.permission.READ_MEDIA_IMAGES);
            perms.add("android.permission.POST_NOTIFICATIONS");
        } else {
            perms.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            perms.add(Manifest.permission.WRITE_EXTERNAL_STORAGE);
        }
        List<String> need = new ArrayList<>();
        for (String p : perms) {
            if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED)
                need.add(p);
        }
        if (!need.isEmpty()) {
            permLauncher = registerForActivityResult(
                    new ActivityResultContracts.RequestMultiplePermissions(), result -> {});
            permLauncher.launch(need.toArray(new String[0]));
        }
    }
}
