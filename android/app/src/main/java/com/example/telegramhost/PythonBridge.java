package com.example.telegramhost;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class PythonBridge {
    private static boolean initialized = false;

    public static void init(android.content.Context ctx) {
        if (!initialized) {
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(ctx));
            }
            initialized = true;
        }
    }

    public static String startBot(String code, String token) {
        try {
            PyObject main = Python.getInstance().getModule("main");
            return main.callAttr("start_bot", code, token).toString();
        } catch (Exception e) {
            return "error: " + e.getMessage();
        }
    }

    public static String stopBot() {
        try {
            PyObject main = Python.getInstance().getModule("main");
            return main.callAttr("stop_bot").toString();
        } catch (Exception e) {
            return "error: " + e.getMessage();
        }
    }

    public static boolean isRunning() {
        try {
            PyObject main = Python.getInstance().getModule("main");
            return main.callAttr("is_running").toJava(boolean.class);
        } catch (Exception e) {
            return false;
        }
    }

    public static String getLogs() {
        try {
            PyObject main = Python.getInstance().getModule("main");
            return main.callAttr("get_logs").toString();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    public static String testLibraries() {
        try {
            PyObject main = Python.getInstance().getModule("main");
            return main.callAttr("test_libraries").toString();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
}
