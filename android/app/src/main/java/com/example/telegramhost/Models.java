package com.example.telegramhost;
import java.util.List;

class BotRequest {
    public String name, token, code, requirements;
    public BotRequest(String n, String t, String c) { name=n; token=t; code=c; requirements=""; }
    public BotRequest(String n, String t, String c, String r) { name=n; token=t; code=c; requirements=r; }
}
class BotResponse { public String status, bot_id, message; }
class StatusResponse { public String status, bot_id; }
class LogsResponse { public String logs; }
class BotStatus {
    public String status;
    public boolean running;
    public String pid;
    public boolean auto_restart;
}
class BotsList { public List<BotInfo> bots; }
class BotInfo {
    public String id, name, status;
    public boolean auto_restart;
}
