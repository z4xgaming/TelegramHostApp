package com.example.telegramhost;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHelper extends SQLiteOpenHelper {
    private static final String DB_NAME = "telegram_host.db";
    private static final int DB_VERSION = 1;

    public DatabaseHelper(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override public void onCreate(SQLiteDatabase db) {
        // Users table - login/signup data store
        db.execSQL("CREATE TABLE users (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "email TEXT UNIQUE, " +
                "password TEXT, " +
                "first_name TEXT, " +
                "last_name TEXT, " +
                "profile_pic TEXT, " +
                "banner TEXT)");
        // Bots table - deployed bots
        db.execSQL("CREATE TABLE bots (" +
                "id TEXT PRIMARY KEY, " +
                "name TEXT, " +
                "token TEXT, " +
                "code TEXT, " +
                "status TEXT, " +
                "sleep_mode INTEGER DEFAULT 0, " +
                "created_at INTEGER)");
    }

    @Override public void onUpgrade(SQLiteDatabase db, int o, int n) {
        // Data loss nahi hoga - sirf naye columns add karo
    }

    // Signup
    public boolean signup(String email, String password, String fname, String lname) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("email", email); cv.put("password", password);
        cv.put("first_name", fname); cv.put("last_name", lname);
        long r = db.insert("users", null, cv);
        return r != -1;
    }

    // Login
    public boolean login(String email, String password) {
        SQLiteDatabase db = getReadableDatabase();
        Cursor c = db.rawQuery("SELECT id FROM users WHERE email=? AND password=?",
                new String[]{email, password});
        boolean ok = c.moveToFirst();
        c.close();
        return ok;
    }

    // Current user data
    public Cursor getUser(String email) {
        return getReadableDatabase().rawQuery("SELECT * FROM users WHERE email=?",
                new String[]{email});
    }

    // Update profile pic
    public void updateProfilePic(String email, String path) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("profile_pic", path);
        db.update("users", cv, "email=?", new String[]{email});
    }

    // Update banner
    public void updateBanner(String email, String path) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("banner", path);
        db.update("users", cv, "email=?", new String[]{email});
    }

    // Save bot
    public void saveBot(String id, String name, String token, String code, String status) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("id", id); cv.put("name", name); cv.put("token", token);
        cv.put("code", code); cv.put("status", status);
        cv.put("created_at", System.currentTimeMillis());
        db.insertWithOnConflict("bots", null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public Cursor getAllBots() {
        return getReadableDatabase().rawQuery("SELECT * FROM bots ORDER BY created_at DESC", null);
    }

    public void updateBotStatus(String id, String status) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("status", status);
        db.update("bots", cv, "id=?", new String[]{id});
    }

    public void toggleSleepMode(String id, boolean on) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("sleep_mode", on ? 1 : 0);
        db.update("bots", cv, "id=?", new String[]{id});
    }

    public void deleteBot(String id) {
        getWritableDatabase().delete("bots", "id=?", new String[]{id});
    }

    // Session - current logged in email save
    public void saveSession(String email) {
        SQLiteDatabase db = getWritableDatabase();
        ContentValues cv = new ContentValues();
        cv.put("email", "__session__");
        cv.put("password", email);
        db.insertWithOnConflict("users", null, cv, SQLiteDatabase.CONFLICT_REPLACE);
    }

    public String getSession() {
        Cursor c = getReadableDatabase().rawQuery(
                "SELECT password FROM users WHERE email='__session__'", null);
        String email = null;
        if (c.moveToFirst()) email = c.getString(0);
        c.close();
        return email;
    }

    public void clearSession() {
        getWritableDatabase().delete("users", "email=?", new String[]{"__session__"});
    }
}
