package com.example.telegramhost;
import java.util.List;
class BotRequest { public String name, token, code; public BotRequest(String n,String t,String c){name=n;token=t;code=c;} }
class BotResponse { public String status, bot_id, message; }
class StatusResponse { public String status, bot_id; }
class LogsResponse { public String logs; }
class BotsList { public List<BotInfo> bots; }
class BotInfo { public String id, name, status; }
