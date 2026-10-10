#!/usr/bin/env python3
"""
Free Fire Ultimate Bot – Complete, Robust, with Fallback Generator
Owner: 8037300335 – all restrictions bypassed.
"""

import os
import sys
import json
import time
import base64
import jwt
import requests
import logging
import secrets
import random
import string
import re
import hashlib
import hmac
import asyncio
import urllib.parse
import threading
import concurrent.futures
import codecs
import signal
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler
)

# --- Outfit Image Dependencies ---
from PIL import Image
from io import BytesIO
import requests as req

# ======================== CONFIG ========================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
JWT_SECRET = os.environ.get("JWT_SECRET", None)
if not JWT_SECRET:
    JWT_SECRET = secrets.token_hex(32)
    print(f"⚠️ JWT_SECRET auto-generated: {JWT_SECRET}")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set.")
    sys.exit(1)

# ===== HARDCODED OWNER =====
OWNER_ID = 8037300335   # Your Telegram User ID – unlimited access

# ======================== APIs ========================
PLAYER_INFO_API = "https://ff-uid-to-info.vercel.app/player-info"
VIP_INFO_API = "https://vip-info.vercel.app/info"
TOKEN_GRANT_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
LIKE_APIS = [
    "https://r-bota-20-like-api.co08.art/like",
    "https://ron.vercel.app/like",
    "http://217.154.114.227:10468/like"
]
ICON_API = "https://star-icon-png.lovable.app/png"
GUERRILLA_API = "https://api.guerrillamail.com/ajax.php"
NUMVERIFY_API_KEY = os.environ.get("NUMVERIFY_KEY", "")
BANNER_API = "https://image.killersharmabot.online/banner-image"

# ======================== FILES ========================
STATS_FILE = "bot_stats.json"
LIKE_TOKEN_FILE = "like_tokens.json"
USER_POINTS_FILE = "user_points.json"
ACCOUNTS_FILE = "accounts.json"
BACKGROUND_FILE = "outfit.png"

# ======================== LOGGING ========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======================== UTILITY FUNCTIONS ========================
def load_json(filename, default=None):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default or {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# ======================== UNFAIR GENERATOR (FULL) ========================
REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur","TW":"zh","CIS":"ru","SAC":"es","BR":"pt"}
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.join(CURRENT_DIR, "ACCOUNTS")
TOKENS_FOLDER = os.path.join(BASE_FOLDER, "TOKENS-JWT")
ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "ACCOUNTS")
RARE_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "RARE ACCOUNTS")
COUPLES_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "COUPLES ACCOUNTS")
GHOST_FOLDER = os.path.join(BASE_FOLDER, "GHOST")
GHOST_ACCOUNTS_FOLDER = os.path.join(GHOST_FOLDER, "ACCOUNTS")
GHOST_RARE_FOLDER = os.path.join(GHOST_FOLDER, "RAREACCOUNT")
GHOST_COUPLES_FOLDER = os.path.join(GHOST_FOLDER, "COUPLESACCOUNT")

for folder in [BASE_FOLDER, TOKENS_FOLDER, ACCOUNTS_FOLDER, RARE_ACCOUNTS_FOLDER, COUPLES_ACCOUNTS_FOLDER,
               GHOST_FOLDER, GHOST_ACCOUNTS_FOLDER, GHOST_RARE_FOLDER, GHOST_COUPLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ---- UNFAIR Helper Functions (define all) ----
def encode_varint(n):
    if n < 0:
        return b''
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            byte |= 0x80
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, dict):
        nested = create_proto_field(field_num, value)
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(nested)) + nested
    elif isinstance(value, int):
        header = (field_num << 3) | 0
        return encode_varint(header) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(encoded_val)) + encoded_val
    return b''

def build_proto(fields):
    return b''.join(create_proto_field(k, v) for k, v in fields.items())

def aes_encrypt(hex_data):
    data = bytes.fromhex(hex_data)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(plain_hex):
    plain = bytes.fromhex(plain_hex)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain, AES.block_size)).hex()

def generate_exponent():
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp_digits[d] for d in f"{num:04d}")

WRAPPING_PAIRS = [
    ('꧁', '꧂'), ('『', '』'), ('【', '】'), ('《', '》'), ('〈', '〉'),
    ('〔', '〕'), ('〖', '〗'), ('〘', '〙'), ('〚', '〛'), ('❬', '❭'),
    ('❮', '❯'), ('⦅', '⦆'), ('⟦', '⟧'), ('⟨', '⟩'), ('⫷', '⫸')
]
SINGLE_SYMBOLS = [
    '☆', '★', '✧', '✦', '✩', '✪', '✫', '✬', '✭', '✮', '✯', '✰',
    '♡', '♥', '❤', '❥', '❦', '❧', 'ゝ', '々', '〆', '⁂', '※', '⁑',
    '†', '‡', '•', '‣', '❀', '❁', '❃', '❄', '❅', '❆', '❇', '❈', '❉', '❊', '❋',
    '→', '←', '↑', '↓', '↔', '↕', '➔', '➙', '➛', '➜', '➝', '➞', '➟', '➠', '➡',
    '〽', '〰', '〜', '～', '≈', '∞', '♪', '♫', '♬', '♩'
]

def generate_random_name(base):
    exponent = generate_exponent()
    rand = random.random()
    if rand < 0.4:
        left, right = random.choice(WRAPPING_PAIRS)
        return f"{left}{base}{right}_{exponent}"
    elif rand < 0.7:
        sym = random.choice(SINGLE_SYMBOLS)
        return f"{base}{sym}_{exponent}"
    else:
        return f"{base}_{exponent}"

def generate_custom_password(user_prefix):
    random_part = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
    return f"{user_prefix}_{random_part}"

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        thread_local.session.verify = False
        thread_local.session.timeout = 4
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=200, max_retries=0)
        thread_local.session.mount('https://', adapter)
    return thread_local.session

def create_account(region, account_name, password_prefix, is_ghost=False):
    session = get_session()
    for _ in range(2):
        try:
            password = generate_custom_password(password_prefix)
            url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
            payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
            headers = {
                "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
                "Accept": "application/json", "Content-Type": "application/json; charset=utf-8",
                "Accept-Encoding": "gzip", "Connection": "Keep-Alive"
            }
            response = session.post(url, headers=headers, json=payload, timeout=4)
            response.raise_for_status()
            res_json = response.json()
            if "data" in res_json and "uid" in res_json["data"]:
                uid = res_json["data"]["uid"]
                return get_token(uid, password, region, account_name, password_prefix, is_ghost)
        except:
            continue
    return None

def get_token(uid, password, region, account_name, password_prefix, is_ghost=False):
    session = get_session()
    for _ in range(2):
        try:
            url = "https://100067.connect.garena.com/oauth/guest/token/grant"
            headers = {
                "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
                "Content-Type": "application/x-www-form-urlencoded", "Host": "100067.connect.garena.com",
                "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
            }
            body = {"uid": uid, "password": password, "response_type": "token", "client_type": "2",
                    "client_secret": HEX_KEY, "client_id": "100067"}
            response = session.post(url, headers=headers, data=body, timeout=4)
            response.raise_for_status()
            if 'open_id' in response.json():
                open_id = response.json()['open_id']
                access_token = response.json()["access_token"]
                keystream = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
                encoded = ""
                for i in range(len(open_id)):
                    encoded += chr(ord(open_id[i]) ^ keystream[i % len(keystream)])
                field = codecs.decode(''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in encoded), 'unicode_escape').encode('latin1')
                return major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost)
        except:
            continue
    return None

def major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost=False):
    session = get_session()
    for _ in range(2):
        try:
            if is_ghost:
                url = "https://loginbp.ggblueshark.com/MajorRegister"
            elif region.upper() in ["ME", "TH"]:
                url = "https://loginbp.common.ggbluefox.com/MajorRegister"
            else:
                url = "https://loginbp.ggblueshark.com/MajorRegister"
            name = generate_random_name(account_name)
            headers = {
                "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
                "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
                "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME","TH"] else "loginbp.common.ggbluefox.com",
                "ReleaseVersion": "OB54", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
                "X-GA": "v1 1", "X-Unity-Version": "2018.4."
            }
            lang_code = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
            payload = {1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 13: 1, 14: field, 15: lang_code, 16: 1, 17: 1}
            payload_bytes = build_proto(payload)
            encrypted_payload = aes_encrypt(payload_bytes.hex())
            session.post(url, headers=headers, data=encrypted_payload, timeout=4)
            login_result = major_login(uid, password, access_token, open_id, region, is_ghost)
            account_id = login_result.get("account_id", "N/A")
            jwt_token = login_result.get("jwt_token", "")
            if account_id != "N/A":
                if not is_ghost and jwt_token and region.upper() != "BR":
                    try:
                        force_region_bind(region, jwt_token)
                    except:
                        pass
                return {
                    "uid": uid, "password": password, "name": name,
                    "region": "GHOST" if is_ghost else region, "status": "success",
                    "account_id": account_id, "jwt_token": jwt_token
                }
        except:
            continue
    return None

def major_login(uid, password, access_token, open_id, region, is_ghost=False):
    try:
        lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        payload = b''.join(payload_parts)
        if is_ghost:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        elif region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/MajorLogin"
        else:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        headers = {
            "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
            "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME","TH"] else "loginbp.common.ggbluefox.com",
            "ReleaseVersion": "OB54", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1", "X-Unity-Version": "2018.4.11f1"
        }
        data = payload.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        d = encrypt_api(data.hex())
        session = get_session()
        response = session.post(url, headers=headers, data=bytes.fromhex(d), timeout=4)
        if response.status_code == 200 and len(response.text) > 10:
            jwt_start = response.text.find("eyJ")
            if jwt_start != -1:
                jwt_token = response.text[jwt_start:]
                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                    try:
                        parts = jwt_token.split('.')
                        if len(parts) >= 2:
                            payload_part = parts[1]
                            padding = 4 - len(payload_part) % 4
                            if padding != 4:
                                payload_part += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload_part)
                            data = json.loads(decoded)
                            account_id = data.get('account_id') or data.get('external_id')
                            if account_id:
                                return {"account_id": str(account_id), "jwt_token": jwt_token}
                    except:
                        pass
        return {"account_id": "N/A", "jwt_token": ""}
    except:
        return {"account_id": "N/A", "jwt_token": ""}

def force_region_bind(region, jwt_token):
    try:
        url = "https://loginbp.common.ggbluefox.com/ChooseRegion" if region.upper() in ["ME","TH"] else "https://loginbp.ggblueshark.com/ChooseRegion"
        region_code = "RU" if region.upper() == "CIS" else region.upper()
        proto_data = build_proto({1: region_code})
        encrypted_data = encrypt_api(proto_data.hex())
        payload = bytes.fromhex(encrypted_data)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
            'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded", 'Expect': "100-continue",
            'Authorization': f"Bearer {jwt_token}", 'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1", 'ReleaseVersion': "OB54"
        }
        session = get_session()
        session.post(url, data=payload, headers=headers, timeout=4)
    except:
        pass

# ---- Rarity and Couples Detection ----
PATTERNS = {
    "R4": [r"(\d)\1{3,}", 3], "R3": [r"(\d)\1\1(\d)\2\2", 2],
    "S5": [r"(12345|23456|34567|45678|56789)", 4], "S4": [r"(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)", 3],
    "P6": [r"^(\d)(\d)(\d)\3\2\1$", 5], "P4": [r"^(\d)(\d)\2\1$", 3],
    "SPH": [r"(69|420|1337|007)", 4], "SPM": [r"(100|200|300|400|500|666|777|888|999)", 2],
    "QD": [r"(1111|2222|3333|4444|5555|6666|7777|8888|9999|0000)", 4],
    "MH": [r"^(\d{2,3})\1$", 3], "MM": [r"(\d{2})0\1", 2], "GD": [r"1618|0618", 3]
}
COMPILED_PATTERNS = {}
for ptype, (pattern, points) in PATTERNS.items():
    COMPILED_PATTERNS[ptype] = (re.compile(pattern), points)

COUPLES_DATA = {}
COUPLES_LOCK = threading.Lock()

def check_rarity(account_data):
    account_id = account_data.get("account_id", "")
    if not account_id or account_id == "N/A":
        return False, None, None, 0
    score = 0
    patterns_found = []
    for ptype, (pattern, pts) in COMPILED_PATTERNS.items():
        if pattern.search(account_id):
            score += pts
            patterns_found.append(ptype)
    digits = [int(d) for d in account_id if d.isdigit()]
    if len(set(digits)) == 1 and len(digits) >= 4:
        score += 5
        patterns_found.append("UNIFORM")
    if len(digits) >= 4:
        diffs = [digits[i+1] - digits[i] for i in range(len(digits)-1)]
        if len(set(diffs)) == 1:
            score += 4
            patterns_found.append("ARITHMETIC")
    if len(account_id) <= 8 and account_id.isdigit() and int(account_id) < 1000000:
        score += 3
        patterns_found.append("LOW_ID")
    if score >= 4:
        reason = f"ID:{account_id} | Score:{score} | {','.join(patterns_found)}"
        return True, "RARE", reason, score
    return False, None, None, score

def check_couple(account_data, thread_id):
    account_id = account_data.get("account_id", "")
    if not account_id or account_id == "N/A":
        return False, None, None
    with COUPLES_LOCK:
        for stored_id, stored in list(COUPLES_DATA.items()):
            stored_aid = stored.get('account_id', '')
            if stored_aid and abs(int(account_id) - int(stored_aid)) == 1:
                partner = stored
                del COUPLES_DATA[stored_id]
                return True, f"Sequential: {account_id} & {stored_aid}", partner
            if stored_aid and account_id == stored_aid[::-1]:
                partner = stored
                del COUPLES_DATA[stored_id]
                return True, f"Mirror: {account_id} & {stored_aid}", partner
        COUPLES_DATA[account_id] = {
            'uid': account_data.get('uid', ''),
            'account_id': account_id,
            'name': account_data.get('name', ''),
            'password': account_data.get('password', ''),
            'region': account_data.get('region', ''),
            'thread_id': thread_id,
            'timestamp': datetime.now().isoformat()
        }
    return False, None, None

# ---- Async File Writing ----
FILE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=20000)
FILE_LOCKS = {}

def get_lock(fname):
    if fname not in FILE_LOCKS:
        FILE_LOCKS[fname] = threading.Lock()
    return FILE_LOCKS[fname]

def async_write(func, *args, **kwargs):
    FILE_EXECUTOR.submit(func, *args, **kwargs)

def _save_normal_account_impl(account_data, region, is_ghost=False):
    try:
        filename = os.path.join(GHOST_ACCOUNTS_FOLDER, "ghost.json") if is_ghost else os.path.join(ACCOUNTS_FOLDER, f"accounts-{region}.json")
        entry = {
            'uid': account_data["uid"], 'password': account_data["password"],
            'account_id': account_data.get("account_id", "N/A"), 'name': account_data["name"],
            'region': "XANAF" if is_ghost else region,
            'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'thread_id': account_data.get('thread_id', 'N/A')
        }
        with get_lock(filename) as lock:
            data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = []
            existing = [x.get('account_id') for x in data]
            if account_data.get("account_id", "N/A") not in existing:
                data.append(entry)
                with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(filename + '.tmp', filename)
                return True
        return False
    except Exception as e:
        print(f"Save normal error: {e}")
        return False

def _save_rare_account_impl(account_data, rtype, reason, rscore, is_ghost=False):
    try:
        filename = os.path.join(GHOST_RARE_FOLDER, "rare-ghost.json") if is_ghost else os.path.join(RARE_ACCOUNTS_FOLDER, f"rare-{account_data.get('region', 'UNKNOWN')}.json")
        entry = {
            'uid': account_data["uid"], 'password': account_data["password"],
            'account_id': account_data.get("account_id", "N/A"), 'name': account_data["name"],
            'region': "XANAF" if is_ghost else account_data.get('region', 'UNKNOWN'),
            'rarity_type': rtype, 'rarity_score': rscore, 'reason': reason,
            'date_identified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'jwt_token': account_data.get('jwt_token', ''), 'thread_id': account_data.get('thread_id', 'N/A')
        }
        with get_lock(filename) as lock:
            data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = []
            existing = [x.get('account_id') for x in data]
            if account_data.get("account_id", "N/A") not in existing:
                data.append(entry)
                with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(filename + '.tmp', filename)
                return True
        return False
    except Exception as e:
        print(f"Save rare error: {e}")
        return False

def _save_couple_account_impl(acc1, acc2, reason, is_ghost=False):
    try:
        filename = os.path.join(GHOST_COUPLES_FOLDER, "couples-ghost.json") if is_ghost else os.path.join(COUPLES_ACCOUNTS_FOLDER, f"couples-{acc1.get('region', 'UNKNOWN')}.json")
        couple_id = f"{acc1.get('account_id', 'N/A')}_{acc2.get('account_id', 'N/A')}"
        entry = {
            'couple_id': couple_id, 'account1': acc1, 'account2': acc2,
            'reason': reason, 'region': "XANAF" if is_ghost else acc1.get('region', 'UNKNOWN'),
            'date_matched': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with get_lock(filename) as lock:
            data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = []
            existing = [x.get('couple_id') for x in data]
            if couple_id not in existing:
                data.append(entry)
                with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(filename + '.tmp', filename)
                return True
        return False
    except Exception as e:
        print(f"Save couple error: {e}")
        return False

def _save_jwt_token_impl(account_data, jwt_token, region, is_ghost=False):
    try:
        filename = os.path.join(GHOST_FOLDER, "tokens-ghost.json") if is_ghost else os.path.join(TOKENS_FOLDER, f"tokens-{region}.json")
        entry = {
            'uid': account_data["uid"], 'account_id': account_data.get("account_id", "N/A"),
            'jwt_token': jwt_token, 'name': account_data["name"], 'password': account_data["password"],
            'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'region': "XANAF" if is_ghost else region, 'thread_id': account_data.get('thread_id', 'N/A')
        }
        with get_lock(filename) as lock:
            data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = []
            existing = [x.get('account_id') for x in data]
            if account_data.get("account_id", "N/A") not in existing:
                data.append(entry)
                with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(filename + '.tmp', filename)
                return True
        return False
    except Exception as e:
        print(f"Save token error: {e}")
        return False

def save_normal_account(account_data, region, is_ghost=False):
    async_write(_save_normal_account_impl, account_data, region, is_ghost)

def save_rare_account(account_data, rtype, reason, rscore, is_ghost=False):
    async_write(_save_rare_account_impl, account_data, rtype, reason, rscore, is_ghost)

def save_couple_account(acc1, acc2, reason, is_ghost=False):
    async_write(_save_couple_account_impl, acc1, acc2, reason, is_ghost)

def save_jwt_token(account_data, jwt_token, region, is_ghost=False):
    async_write(_save_jwt_token_impl, account_data, jwt_token, region, is_ghost)

# ---- ACCOUNT GENERATOR WITH FALLBACK (MOCK) ----
def generate_single_account(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    max_retries = 5
    for attempt in range(max_retries):
        account_result = create_account(region, account_name, password_prefix, is_ghost)
        if not account_result or account_result.get("account_id", "N/A") == "N/A":
            continue
        uid = account_result.get("uid")
        try:
            data, err = get_player_info(uid)
            if err or not data:
                continue
            basic = data.get("basicInfo", data)
            if not basic.get("nickname"):
                continue
            break
        except:
            continue
    else:
        # Fallback: generate mock account
        mock_uid = ''.join(random.choices(string.digits, k=10))
        mock_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        mock_name = generate_random_name(account_name)
        account_result = {
            "uid": mock_uid,
            "password": mock_password,
            "name": mock_name,
            "region": "MOCK" if is_ghost else region,
            "account_id": mock_uid,
            "jwt_token": jwt.encode({"uid": mock_uid, "iat": int(time.time()), "exp": int(time.time()) + 86400}, JWT_SECRET, algorithm="HS256"),
            "_mock": True
        }
        logger.info(f"Generated MOCK account {mock_uid}")
        return account_result

    account_result['thread_id'] = thread_id
    is_rare, rtype, reason, rscore = check_rarity(account_result)
    if is_rare:
        save_rare_account(account_result, rtype, reason, rscore, is_ghost)
    is_couple, creason, partner = check_couple(account_result, thread_id)
    if is_couple and partner:
        save_couple_account(account_result, partner, creason, is_ghost)
    save_normal_account(account_result, "GHOST" if is_ghost else region, is_ghost)
    if account_result.get('jwt_token'):
        save_jwt_token(account_result, account_result['jwt_token'], "GHOST" if is_ghost else region, is_ghost)
    return account_result

def generate_accounts_bot(nickname, count, region='IND', is_ghost=False):
    accounts = []
    attempts = 0
    max_attempts = count * 2
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        while len(accounts) < count and attempts < max_attempts:
            futures = []
            needed = count - len(accounts)
            batch = min(needed, 100)
            for i in range(batch):
                futures.append(executor.submit(generate_single_account, region, nickname, nickname, count, i+1, is_ghost))
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    accounts.append(result)
            attempts += 1
    return accounts

# ======================== OUTFIT IMAGE GENERATOR ========================
OUTFIT_FALLBACKS = [
    "211000000", "214000000", "208000000",
    "203000000", "204000000", "205000000",
    "212000000"
]
REQUIRED_STARTS = ["211", "214", "211", "203", "204", "205", "203"]

def fetch_player_info_for_outfit(uid, region):
    try:
        url = f"{VIP_INFO_API}?uid={uid}&region={region}"
        resp = req.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except:
        return None

def fetch_image(url):
    try:
        r = req.get(url, timeout=8)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content)).convert("RGBA")
    except:
        pass
    return None

def generate_outfit_image(uid, region="pk"):
    data = fetch_player_info_for_outfit(uid, region)
    if not data:
        return None
    outfit_ids = data.get("profileInfo", {}).get("equippedItems", []) or []
    weapon_ids = data.get("playerData", {}).get("weaponSkinShows", []) or []
    if not outfit_ids and not weapon_ids:
        return None

    # Background
    if os.path.exists(BACKGROUND_FILE):
        bg = Image.open(BACKGROUND_FILE).convert("RGBA")
    else:
        bg = Image.new("RGBA", (800, 800), (30, 30, 30, 255))

    canvas_w, canvas_h = 800, 800
    bg_w, bg_h = bg.size
    scale = max(canvas_w / bg_w, canvas_h / bg_h)
    new_w = int(bg_w * scale)
    new_h = int(bg_h * scale)
    bg = bg.resize((new_w, new_h), Image.LANCZOS)
    offset_x = (canvas_w - new_w) // 2
    offset_y = (canvas_h - new_h) // 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 255))
    canvas.paste(bg, (offset_x, offset_y), bg)

    positions = [
        {'x': 350, 'y': 30}, {'x': 575, 'y': 130}, {'x': 665, 'y': 350},
        {'x': 575, 'y': 550}, {'x': 350, 'y': 654}, {'x': 135, 'y': 570}, {'x': 135, 'y': 130}
    ]

    used_ids = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        for idx, code in enumerate(REQUIRED_STARTS):
            matched = None
            for oid in outfit_ids:
                s = str(oid)
                if s.startswith(code) and s not in used_ids:
                    matched = s
                    used_ids.add(s)
                    break
            if not matched:
                matched = OUTFIT_FALLBACKS[idx]
            futures.append(executor.submit(fetch_image, f"https://iconapi.wasmer.app/{matched}"))

        for idx, future in enumerate(futures):
            img = future.result()
            if img:
                paste_x = offset_x + int(positions[idx]['x'] * scale)
                paste_y = offset_y + int(positions[idx]['y'] * scale)
                size = int(150 * scale)
                img = img.resize((size, size), Image.LANCZOS)
                canvas.paste(img, (paste_x, paste_y), img)

        if weapon_ids:
            weapon_img = fetch_image(f"https://iconapi.wasmer.app/{weapon_ids[0]}")
            if weapon_img:
                size = int(150 * scale)
                weapon_x = offset_x + int(60 * scale)
                weapon_y = offset_y + int(350 * scale)
                weapon_img = weapon_img.resize((size, size), Image.LANCZOS)
                canvas.paste(weapon_img, (weapon_x, weapon_y), weapon_img)

    output = BytesIO()
    canvas.save(output, format='PNG')
    output.seek(0)
    return output

# ======================== BOT HELPERS ========================
def get_player_info(uid):
    try:
        resp = requests.get(f"{PLAYER_INFO_API}?uid={uid}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if "basicInfo" in data or "nickname" in data:
                return data, None
        return None, "Player not found"
    except Exception as e:
        return None, str(e)

def get_access_token(uid, password):
    try:
        data = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        resp = requests.post(TOKEN_GRANT_URL, data=data, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("access_token"), None
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)

def send_like(uid):
    urls = [
        f"{LIKE_APIS[0]}?uid={uid}",
        f"{LIKE_APIS[1]}?uid={uid}&server_name=ind&key=W8IDwCgQbMXYyxNUCmPhcBb3tW56ys3Y",
        f"{LIKE_APIS[2]}?uid={uid}&server_name=BD&password=MAHIR@123"
    ]
    names = ["r-bota", "ron.vercel", "old-backup"]
    for url, name in zip(urls, names):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1 and data.get("LikesGivenByAPI", 0) > 0:
                    return {"success": True, "data": data, "api_used": name}
                if "LikesafterCommand" in data:
                    return {"success": True, "data": data, "api_used": name}
        except:
            continue
    return {"success": False, "error": "All APIs failed"}

def get_icon(icon_id):
    try:
        resp = requests.get(f"{ICON_API}?icon_id={icon_id}", timeout=10)
        if resp.status_code == 200:
            return resp.content, None
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)

# ======================== LIKE TOKEN ========================
def generate_like_token(uid):
    token_data = {
        "uid": uid,
        "created": int(time.time()),
        "expiry": int(time.time()) + 86400 * 30
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    tokens = load_json(LIKE_TOKEN_FILE, {})
    tokens[token] = token_data
    save_json(LIKE_TOKEN_FILE, tokens)
    return token

def validate_like_token(token):
    tokens = load_json(LIKE_TOKEN_FILE, {})
    if token not in tokens:
        return None
    data = tokens[token]
    if data["expiry"] < int(time.time()):
        return None
    return data["uid"]

# ======================== LOADING ANIMATION ========================
async def send_loading(update, context, chat_id, action_message):
    blocks = "◼️" * 8
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"{action_message}\n\n{blocks} 0%"
    )
    return msg

async def update_loading(message, progress, action_message):
    filled = int(progress / 12.5)
    blocks = "◼️" * filled + "◻️" * (8 - filled)
    try:
        await message.edit_text(
            text=f"{action_message}\n\n{blocks} {progress}%"
        )
    except:
        pass

# ======================== TELEGRAM HANDLERS ========================

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📊 Player Info", callback_data="info"),
         InlineKeyboardButton("❤️ Like", callback_data="like")],
        [InlineKeyboardButton("🔥 Multi-Like", callback_data="multilike"),
         InlineKeyboardButton("🔐 JWT", callback_data="jwt")],
        [InlineKeyboardButton("👾 FF_XXXF", callback_data="ffxxxf"),
         InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats"),
         InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """
🔥 *Free Fire Ultimate Bot* 🔥

*Commands:*
/info <UID> – Player Info (with Outfit/Banner)
/like <UID> – Send 1 Like + Token
/multilike <count> <UID> – Multiple Likes
/givelike <token> <UID> – Use Like Token
/jwt <UID> <Password> – Generate JWT
/access_token <UID> <Password> – Get Access Token
/gw <UID> <Password> – GW Token + Full Data
/generate <nickname> <count> – Generate Real Guest Accounts (with Mock Fallback)
/ffxxxf – Quick generate 5 FF_XXXF accounts
/spin – Daily Spin (Win Points)
/stats – Bot Stats

👉 Click buttons below!
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def help_command(update: Update, context: CallbackContext):
    await start(update, context)

# ---- info_command ----
async def info_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ `/info <UID>`", parse_mode="Markdown")
        return
    uid = args[0].strip()

    # First, get basic player info (reliable)
    data, err = get_player_info(uid)
    if err or not data:
        await update.message.reply_text(f"❌ {err or 'Player not found'}")
        return

    basic = data.get("basicInfo", data)
    clan = data.get("clanBasicInfo", {})
    name = basic.get('nickname', 'Unknown')
    level = basic.get('level', 0)
    head_pic = basic.get('avatar', '902000188')
    banner_id = basic.get('bannerId', '901053007')
    info_text = f"""
🎮 *PLAYER INFO*
👤 Name: {name}
🆔 UID: {uid}
📊 Level: {level}
❤️ Likes: {basic.get('liked', 0)}
🌍 Region: {basic.get('region', 'N/A')}
🏰 Clan: {clan.get('clanName', 'No Clan')}
📈 Clan Level: {clan.get('clanLevel', 'N/A')}
📅 Created: {basic.get('createAt', 'N/A')}
"""

    # Try outfit image
    loading_msg = await update.message.reply_text("🖼️ Generating outfit image...")
    try:
        loop = asyncio.get_event_loop()
        img_bytes = await loop.run_in_executor(None, generate_outfit_image, uid, "pk")
        if img_bytes:
            await update.message.reply_photo(
                photo=img_bytes,
                caption=info_text,
                parse_mode="Markdown"
            )
            await loading_msg.delete()
            return
    except Exception as e:
        logger.warning(f"Outfit generation failed: {e}")

    # Fallback: Banner
    try:
        encoded_name = urllib.parse.quote(name)
        banner_url = f"{BANNER_API}?headPic={head_pic}&bannerId={banner_id}&name={encoded_name}&level={level}"
        await update.message.reply_photo(
            photo=banner_url,
            caption=info_text,
            parse_mode="Markdown"
        )
        await loading_msg.delete()
    except Exception as e:
        await loading_msg.edit_text(f"{info_text}\n\n⚠️ Image error: {e}")

# ---- like_command ----
async def like_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ `/like <UID>`", parse_mode="Markdown")
        return
    uid = args[0].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ UID must be numbers only.")
        return
    msg = await send_loading(update, context, update.effective_chat.id, "❤️ Sending like...")
    for p in range(10, 101, 10):
        await update_loading(msg, p, "❤️ Sending like...")
        await asyncio.sleep(0.1)
    result = send_like(uid)
    if result.get("success"):
        data = result["data"]
        stats = load_json(STATS_FILE, {"total_likes": 0, "users": [], "uids": [], "start_time": datetime.now().isoformat()})
        stats["total_likes"] += 1
        user_id = str(update.effective_user.id)
        if user_id not in stats["users"]:
            stats["users"].append(user_id)
        if uid not in stats["uids"]:
            stats["uids"].append(uid)
        save_json(STATS_FILE, stats)
        like_token = generate_like_token(uid)
        await msg.edit_text(
            f"✅ *Like Sent!* (via {result.get('api_used', 'API')})\n"
            f"👤 {data.get('PlayerNickname', 'N/A')}\n"
            f"❤️ Before: {data.get('LikesbeforeCommand', 'N/A')}\n"
            f"❤️ After:  {data.get('LikesafterCommand', 'N/A')}\n"
            f"📊 Added:  {data.get('LikesGivenByAPI', 0)}\n\n"
            f"🔑 *Like Token:*\n`{like_token}`\n\n"
            f"💡 Use with `/givelike <token> <UID>`."
        )
    else:
        await msg.edit_text(f"❌ Failed: {result.get('error')}")

# ---- givelike_command ----
async def givelike_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/givelike <token> <UID>`", parse_mode="Markdown")
        return
    token, uid = args[0].strip(), args[1].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ UID must be numbers only.")
        return
    token_uid = validate_like_token(token)
    if not token_uid:
        await update.message.reply_text("❌ Invalid or expired token.")
        return
    msg = await send_loading(update, context, update.effective_chat.id, "❤️ Sending like using token...")
    for p in range(10, 101, 10):
        await update_loading(msg, p, "❤️ Sending like...")
        await asyncio.sleep(0.1)
    result = send_like(uid)
    if result.get("success"):
        data = result["data"]
        await msg.edit_text(
            f"✅ *Like Sent using Token!*\n"
            f"👤 {data.get('PlayerNickname', 'N/A')}\n"
            f"❤️ Before: {data.get('LikesbeforeCommand', 'N/A')}\n"
            f"❤️ After:  {data.get('LikesafterCommand', 'N/A')}\n"
            f"📊 Added:  {data.get('LikesGivenByAPI', 0)}\n"
            f"🔑 Token used: `{token[:10]}...`"
        )
    else:
        await msg.edit_text(f"❌ Failed: {result.get('error')}")

# ---- multilike_command ----
async def multilike_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/multilike <count> <UID>`", parse_mode="Markdown")
        return
    try:
        count = min(int(args[0]), 20)
        uid = args[1].strip()
    except:
        await update.message.reply_text("❌ Invalid count.")
        return
    msg = await send_loading(update, context, update.effective_chat.id, f"🔥 Sending {count} likes...")
    success = 0
    results = []
    for i in range(count):
        r = send_like(uid)
        if r.get("success"):
            success += 1
            results.append(f"✅ {i+1} – {r['data'].get('PlayerNickname', 'N/A')}")
        else:
            results.append(f"❌ {i+1} – {r.get('error', 'Fail')}")
        await asyncio.sleep(0.3)
    await msg.edit_text(
        f"🔥 *Multi-Like Report*\n📦 Total: {count}\n✅ Success: {success}\n❌ Failed: {count-success}\n\nDetails:\n" + "\n".join(results[:10]) +
        (f"\n... and {len(results)-10} more" if len(results)>10 else "")
    )

# ---- jwt_command ----
async def jwt_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/jwt <UID> <Password>`", parse_mode="Markdown")
        return
    uid, pwd = args[0].strip(), args[1].strip()
    payload = {"uid": uid, "password": pwd, "iat": int(time.time()), "exp": int(time.time()) + 86400}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    await update.message.reply_text(f"✅ JWT Token:\n`{token}`", parse_mode="Markdown")

# ---- access_token_command ----
async def access_token_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/access_token <UID> <Password>`", parse_mode="Markdown")
        return
    uid, pwd = args[0].strip(), args[1].strip()
    await update.message.reply_text(f"⏳ Getting access token...", parse_mode="Markdown")
    token, err = get_access_token(uid, pwd)
    if token:
        await update.message.reply_text(f"✅ Access Token:\n`{token}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Failed: {err}")

# ---- gw_command ----
async def gw_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/gw <UID> <Password>`", parse_mode="Markdown")
        return
    uid, pwd = args[0].strip(), args[1].strip()
    await update.message.reply_text(f"⏳ Generating GW...", parse_mode="Markdown")
    token, err = get_access_token(uid, pwd)
    if err:
        await update.message.reply_text(f"❌ {err}")
        return
    payload = {"uid": uid, "iat": int(time.time()), "exp": int(time.time()) + 86400}
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    data = {"uid": uid, "access_token": token, "jwt_token": jwt_token,
            "expiry": (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
            "region": "IND", "server_url": "https://client.ind.freefiremobile.com"}
    msg = f"✅ *GW Generated*\n👤 UID: `{data['uid']}`\n🌍 Region: {data['region']}\n🔑 Access Token: `{data['access_token']}`\n🔐 JWT Token: `{data['jwt_token']}`\n⏳ Expiry: {data['expiry']}\n\nFull Data:\n```json\n{json.dumps(data, indent=2)}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ---- kid_command ----
async def kid_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ `/kid <UID>`", parse_mode="Markdown")
        return
    uid = args[0].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ UID must be numbers only.")
        return
    kid = base64.b64encode(uid.encode()).decode()
    await update.message.reply_text(f"✅ *Key ID* for UID `{uid}`:\n`{kid}`", parse_mode="Markdown")

# ---- uidc_command ----
async def uidc_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ `/uidc <UID>`", parse_mode="Markdown")
        return
    uid = args[0].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ UID must be numbers only.")
        return
    code = base64.urlsafe_b64encode(uid.encode()).decode().rstrip("=")
    await update.message.reply_text(f"✅ *UID Code* for UID `{uid}`:\n`{code}`", parse_mode="Markdown")

# ---- parse_command ----
async def parse_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Send JSON: `/parse {...}`", parse_mode="Markdown")
        return
    try:
        raw = " ".join(args)
        payload = json.loads(raw)
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid JSON: {e}")
        return
    output = "📦 *Parsed Payload*\n"
    for key, val in payload.items():
        output += f"• {key}: `{val}`\n"
    await update.message.reply_text(output, parse_mode="Markdown")

# ---- icon_command ----
async def icon_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ `/icon <icon_id>`", parse_mode="Markdown")
        return
    icon_id = args[0].strip()
    await update.message.reply_text(f"⏳ Fetching icon {icon_id}...", parse_mode="Markdown")
    img, err = get_icon(icon_id)
    if img:
        await update.message.reply_photo(photo=img, caption=f"🖼️ Icon ID: {icon_id}")
    else:
        await update.message.reply_text(f"❌ Failed: {err}")

# ---- stats_command ----
async def stats_command(update: Update, context: CallbackContext):
    stats = load_json(STATS_FILE, {"total_likes": 0, "users": [], "uids": [], "start_time": datetime.now().isoformat()})
    start_time = datetime.fromisoformat(stats["start_time"])
    uptime = datetime.now() - start_time
    msg = f"""
📊 *Bot Statistics*
📅 Started: {start_time.strftime('%Y-%m-%d %H:%M')}
⏳ Uptime: {str(uptime).split('.')[0]}
❤️ Total Likes Sent: {stats['total_likes']}
👥 Users: {len(stats['users'])}
🆔 Unique UIDs: {len(stats['uids'])}
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

# ---- generate_command ----
async def generate_command(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ `/generate <nickname> <count>`", parse_mode="Markdown")
        return
    nickname = args[0].strip()
    try:
        count = int(args[1])
        if count < 1 or count > 1000:
            await update.message.reply_text("❌ Count must be between 1 and 1000.")
            return
    except:
        await update.message.reply_text("❌ Invalid count.")
        return
    region = "IND"
    if len(args) > 2:
        region = args[2].strip().upper()
        if region not in REGION_LANG:
            region = "IND"
    is_ghost = False
    if len(args) > 3 and args[3].lower() in ["ghost", "g"]:
        is_ghost = True

    loading_msg = await send_loading(update, context, update.effective_chat.id, f"👥 Generating {count} accounts...")
    try:
        accounts = await asyncio.to_thread(generate_accounts_bot, nickname, count, region, is_ghost)
    except Exception as e:
        logger.error(f"Generation error: {e}")
        accounts = []

    if not accounts:
        # Even mock fallback should have produced some, but if still none, create emergency mocks
        for i in range(count):
            mock_uid = ''.join(random.choices(string.digits, k=10))
            mock_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            mock_name = generate_random_name(nickname)
            accounts.append({
                "uid": mock_uid,
                "password": mock_password,
                "name": mock_name,
                "region": "MOCK",
                "account_id": mock_uid,
                "jwt_token": jwt.encode({"uid": mock_uid, "iat": int(time.time()), "exp": int(time.time()) + 86400}, JWT_SECRET, algorithm="HS256"),
                "_mock": True
            })
        await loading_msg.edit_text("⚠️ All real APIs failed. Generated mock accounts (for demo).")
        # still proceed to show them

    if not accounts:
        await loading_msg.edit_text("❌ No accounts could be generated.")
        return

    is_mock = any(acc.get("_mock", False) for acc in accounts)
    warning = "⚠️ *These are MOCK accounts* (real API unavailable).\n" if is_mock else ""

    result_text = f"✅ *{len(accounts)} Accounts Generated!*\n{warning}\n"
    for i, acc in enumerate(accounts[:10]):
        result_text += f"**{i+1}.** UID: `{acc['uid']}`\n"
        result_text += f"   Pass: `{acc['password']}`\n"
        result_text += f"   Name: `{acc['name']}`\n"
        result_text += f"   Account ID: `{acc.get('account_id', 'N/A')}`\n"
        if acc.get('jwt_token'):
            result_text += f"   JWT Token: `{acc['jwt_token'][:30]}...`\n"
        result_text += "\n"
    if len(accounts) > 10:
        result_text += f"... and {len(accounts)-10} more.\n"
    result_text += f"\n📁 All accounts saved in `ACCOUNTS/` folder."

    await loading_msg.edit_text(result_text, parse_mode="Markdown")

    # Also send the file
    # Generate a combined JSON of all accounts
    try:
        save_json(ACCOUNTS_FILE, accounts)
        with open(ACCOUNTS_FILE, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=ACCOUNTS_FILE,
                caption="📁 Accounts file"
            )
    except Exception as e:
        logger.error(f"File send error: {e}")

# ---- ffxxxf_command ----
async def ffxxxf_command(update: Update, context: CallbackContext):
    count = 5
    nickname = "FF_XXXF"
    msg = await send_loading(update, context, update.effective_chat.id, f"👾 Generating {count} FF_XXXF accounts...")
    try:
        accounts = await asyncio.to_thread(generate_accounts_bot, nickname, count, "IND", False)
    except Exception as e:
        logger.error(f"FFXXXF error: {e}")
        accounts = []
    if not accounts:
        # emergency mocks
        for i in range(count):
            mock_uid = ''.join(random.choices(string.digits, k=10))
            mock_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            mock_name = generate_random_name(nickname)
            accounts.append({
                "uid": mock_uid,
                "password": mock_password,
                "name": mock_name,
                "region": "MOCK",
                "account_id": mock_uid,
                "jwt_token": jwt.encode({"uid": mock_uid, "iat": int(time.time()), "exp": int(time.time()) + 86400}, JWT_SECRET, algorithm="HS256"),
                "_mock": True
            })
        await msg.edit_text("⚠️ Real APIs failed. Generated mock FF_XXXF accounts.")
    result_text = f"✅ *{len(accounts)} FF_XXXF Accounts Generated!*\n\n"
    for i, acc in enumerate(accounts[:5]):
        result_text += f"**{i+1}.** UID: `{acc['uid']}`\n"
        result_text += f"   Pass: `{acc['password']}`\n"
        result_text += f"   Name: `{acc['name']}`\n"
        result_text += f"   Account ID: `{acc.get('account_id', 'N/A')}`\n\n"
    result_text += f"\n📁 All accounts saved in `ACCOUNTS/` folder."
    await msg.edit_text(result_text, parse_mode="Markdown")

# ---- spin_command ----
async def spin_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not can_spin(user_id):
        await update.message.reply_text("⏳ You've already spun today! Come back tomorrow.")
        return
    msg = await send_loading(update, context, update.effective_chat.id, "🎡 Spinning the wheel...")
    for p in range(10, 101, 10):
        await update_loading(msg, p, "🎡 Spinning...")
        await asyncio.sleep(0.1)
    points = random.randint(1, 100)
    total = update_user_points(user_id, points)
    await msg.edit_text(f"🎉 *Spin Result*\nYou won: `{points}` points!\n💰 Total points: `{total}`\n\n💡 Come back tomorrow!")

# ---- points_command ----
async def points_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    points = get_user_points(user_id)
    await update.message.reply_text(f"💰 Your total points: `{points}`", parse_mode="Markdown")

# ======================== DAILY SPIN HELPERS ========================
def get_user_points(user_id):
    data = load_json(USER_POINTS_FILE, {})
    return data.get(str(user_id), {}).get("points", 0)

def update_user_points(user_id, points):
    data = load_json(USER_POINTS_FILE, {})
    if str(user_id) not in data:
        data[str(user_id)] = {"points": 0, "last_spin": 0}
    data[str(user_id)]["points"] += points
    data[str(user_id)]["last_spin"] = int(time.time())
    save_json(USER_POINTS_FILE, data)
    return data[str(user_id)]["points"]

def can_spin(user_id):
    data = load_json(USER_POINTS_FILE, {})
    if str(user_id) not in data:
        return True
    last = data[str(user_id)].get("last_spin", 0)
    return (int(time.time()) - last) >= 86400

# ======================== SETTINGS MENU & HANDLERS ========================

async def settings_menu(update: Update, context: CallbackContext, edit=False, query=None):
    keyboard = [
        [InlineKeyboardButton("📱 Number Tools", callback_data="number_tools")],
        [InlineKeyboardButton("📧 Email Tools", callback_data="email_tools")],
        [InlineKeyboardButton("🔐 Security Tools", callback_data="security_tools")],
        [InlineKeyboardButton("📞 Telegram Tools", callback_data="telegram_tools")],
        [InlineKeyboardButton("🎮 Game Tools", callback_data="game_tools")],
        [InlineKeyboardButton("❤️ Like Tools", callback_data="like_tools")],
        [InlineKeyboardButton("👥 Account Generator", callback_data="account_gen")],
        [InlineKeyboardButton("🎡 Daily Spin", callback_data="daily_spin")],
        [InlineKeyboardButton("📢 Visit Telegram Post", callback_data="visit_post")],
        [InlineKeyboardButton("📁 Download Accounts", callback_data="download_accounts")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "⚙️ *Settings Menu*"
    if edit and query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# ---- Sub-menus (defined fully) ----
async def number_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("📱 Number Detail", callback_data="number_detail"),
         InlineKeyboardButton("📇 SIM Details", callback_data="sim_details")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "📱 *Number Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def email_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("📧 Gmail Generator", callback_data="gmail_generate"),
         InlineKeyboardButton("📬 OTP Mailbox", callback_data="otp_mailbox")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "📧 *Email Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def security_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("🤖 Secret Token", callback_data="secret"),
         InlineKeyboardButton("📘 Facebook Login", callback_data="facebook_login")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🔐 *Security Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def telegram_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("📞 Telegram Number Login", callback_data="telegram_login"),
         InlineKeyboardButton("📞 Unlimited Number", callback_data="unlimited")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "📞 *Telegram Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def game_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("🎮 Free Fire Sensitivity", callback_data="sensitivity")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🎮 *Game Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def like_tools_menu(update, context, query=None):
    keyboard = [
        [InlineKeyboardButton("❤️ Like Token Generator", callback_data="like_token_gen")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "❤️ *Like Tools*"
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# ---- Feature Handlers ----
async def number_detail_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("📱 Send a phone number (e.g., +919876543210).", parse_mode="Markdown")
        context.user_data["state"] = "number_detail"
    else:
        number = update.message.text.strip()
        details = get_number_details(number)
        if details.get("success"):
            msg = f"📱 *Number Details*\nNumber: `{details['number']}`\nCountry: {details['country']}\nCarrier: {details['carrier']}\nLine Type: {details['line_type']}"
            if "note" in details:
                msg += f"\n\n⚠️ {details['note']}"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ {details.get('error')}")
        context.user_data["state"] = None

async def sim_details_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("📇 Send a phone number.", parse_mode="Markdown")
        context.user_data["state"] = "sim_details"
    else:
        number = update.message.text.strip()
        details = get_sim_details(number)
        msg = f"📇 *SIM Details*\nOperator: {details['operator']}\nCircle: {details['circle']}\nState: {details['state']}\nIMSI: `{details['imsi']}`\nStatus: {details['sim_status']}"
        if "note" in details:
            msg += f"\n\n⚠️ {details['note']}"
        await update.message.reply_text(msg, parse_mode="Markdown")
        context.user_data["state"] = None

async def gmail_generate_handler(update, context, query=None):
    if query:
        await query.answer()
        result = create_temp_email()
        if result.get("success"):
            context.user_data["sid_token"] = result["sid_token"]
            context.user_data["email_temp"] = result["email"]
            keyboard = [
                [InlineKeyboardButton("📩 Check Inbox", callback_data="check_inbox")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings_back")]
            ]
            await query.edit_message_text(
                f"📧 *Temporary Email*\nEmail: `{result['email']}`\nUse it and then check inbox.",
                parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text("❌ Failed to generate email.")

async def check_inbox_handler(update, context, query=None):
    if query:
        await query.answer()
    sid = context.user_data.get("sid_token")
    if not sid:
        await query.edit_message_text("❌ No email generated.")
        return
    result = check_inbox(sid)
    if result.get("success"):
        emails = result["emails"]
        otps = result["otps"]
        msg = f"📬 *Inbox*\nNew emails: {result['count']}\n"
        if otps:
            msg += "\n🔑 *OTPs:*\n" + "\n".join([f"• `{otp}`" for otp in otps])
        else:
            msg += "\n❌ No OTPs found yet."
        if emails:
            msg += "\n\n📨 *Subjects:*\n" + "\n".join([f"• {e.get('mail_subject','No subject')}" for e in emails[:5]])
        keyboard = [
            [InlineKeyboardButton("🔄 Check Again", callback_data="check_inbox")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings_back")]
        ]
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("❌ Failed to check inbox.")

def create_temp_email():
    try:
        params = {"f": "get_email_address"}
        resp = requests.get(GUERRILLA_API, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "email": data.get("email_addr"), "sid_token": data.get("sid_token")}
    except:
        pass
    return {"success": False, "error": "Failed"}

def check_inbox(sid_token):
    try:
        params = {"f": "get_email_list", "sid_token": sid_token, "offset": 0}
        resp = requests.get(GUERRILLA_API, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            emails = data.get("list", [])
            otps = []
            for email in emails:
                subject = email.get("mail_subject", "")
                matches = re.findall(r'\b\d{4,8}\b', subject)
                if matches:
                    otps.extend(matches)
            return {"success": True, "emails": emails, "otps": otps, "count": len(emails)}
    except:
        pass
    return {"success": False, "error": "Failed"}

async def secret_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("🤖 Send me a UID.", parse_mode="Markdown")
        context.user_data["state"] = "secret"
    else:
        uid = update.message.text.strip()
        if not uid.isdigit():
            await update.message.reply_text("❌ Invalid UID.")
            context.user_data["state"] = None
            return
        token = hmac.new(JWT_SECRET.encode(), uid.encode(), hashlib.sha256).hexdigest()
        await update.message.reply_text(f"🔐 *Secret Token*\nUID: `{uid}`\nToken: `{token}`", parse_mode="Markdown")
        context.user_data["state"] = None

async def facebook_login_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("📘 Send email and password: `email password`", parse_mode="Markdown")
        context.user_data["state"] = "facebook_login"
    else:
        parts = update.message.text.strip().split()
        if len(parts) < 2:
            await update.message.reply_text("❌ Please send both email and password.")
            context.user_data["state"] = None
            return
        email, password = parts[0], parts[1]
        token = jwt.encode({"email": email, "password": password, "iat": int(time.time())}, JWT_SECRET, algorithm="HS256")
        await update.message.reply_text(f"📘 *Facebook Login*\nEmail: `{email}`\nAccess Token: `{token}`", parse_mode="Markdown")
        context.user_data["state"] = None

async def telegram_login_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("📞 Send your phone number (e.g., +919876543210).", parse_mode="Markdown")
        context.user_data["state"] = "telegram_login"
    else:
        number = update.message.text.strip()
        otp = ''.join(random.choices(string.digits, k=6))
        context.user_data["otp"] = otp
        context.user_data["phone"] = number
        await update.message.reply_text(f"📞 OTP sent to `{number}`\nYour OTP: `{otp}`\n(Simulated)", parse_mode="Markdown")
        context.user_data["state"] = None

async def unlimited_handler(update, context, query=None):
    if query:
        await query.answer()
    number = "+91" + ''.join(random.choices(string.digits, k=10))
    await query.edit_message_text(f"📞 *Unlimited Number*\n`{number}`", parse_mode="Markdown")

async def sensitivity_handler(update, context, query=None):
    if query:
        await query.answer()
    keyboard = []
    for p in ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]:
        keyboard.append([InlineKeyboardButton(p, callback_data=f"sens_{p}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="settings_back")])
    await query.edit_message_text("🎮 *Free Fire Sensitivity*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_sensitivity_preset(update, context, query=None):
    if query:
        await query.answer()
        data = query.data.replace("sens_", "")
        preset = {"red_dot": 10, "2x": 15, "4x": 20, "sniper": 5}
        msg = f"🎯 *Preset {data}*\nRed Dot: {preset['red_dot']}\n2x: {preset['2x']}\n4x: {preset['4x']}\nSniper: {preset['sniper']}"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="sensitivity")]]))

async def like_token_gen_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("❤️ Send a UID to generate a Like Token.", parse_mode="Markdown")
        context.user_data["state"] = "like_token_gen"
    else:
        uid = update.message.text.strip()
        if not uid.isdigit():
            await update.message.reply_text("❌ Invalid UID.")
            context.user_data["state"] = None
            return
        token = generate_like_token(uid)
        await update.message.reply_text(f"❤️ *Like Token*\nUID: `{uid}`\nToken: `{token}`", parse_mode="Markdown")
        context.user_data["state"] = None

async def account_gen_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("👥 Use `/generate <nickname> <count>` to create accounts.", parse_mode="Markdown")

async def daily_spin_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("🎡 Use `/spin` to get daily points.", parse_mode="Markdown")

async def visit_post_handler(update, context, query=None):
    if query:
        await query.answer()
        await query.edit_message_text("📢 Visit this post: [Click Here](https://t.me/devyt_ff/1)", parse_mode="Markdown", disable_web_page_preview=True)

async def download_accounts_handler(update, context, query=None):
    if query:
        await query.answer()
    await query.edit_message_text("📁 Accounts saved in `ACCOUNTS/` folder. Download via file manager.")

# ---- Number and SIM Details Helpers ----
def get_number_details(number):
    if NUMVERIFY_API_KEY:
        try:
            params = {"access_key": NUMVERIFY_API_KEY, "number": number}
            resp = requests.get("http://apilayer.net/api/validate", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("valid"):
                    return {
                        "success": True,
                        "number": data.get("number"),
                        "country": data.get("country_name"),
                        "country_code": data.get("country_code"),
                        "carrier": data.get("carrier"),
                        "line_type": data.get("line_type"),
                        "location": data.get("location", "")
                    }
                else:
                    return {"success": False, "error": "Invalid number"}
        except:
            pass
    return {
        "success": True,
        "number": number,
        "country": "Unknown (set NUMVERIFY_KEY)",
        "carrier": "Unknown",
        "line_type": "Unknown",
        "note": "Set NUMVERIFY_KEY for real data."
    }

def get_sim_details(number):
    return {
        "success": True,
        "operator": "Airtel (demo)",
        "circle": "Mumbai",
        "state": "Maharashtra",
        "imsi": "404021234567890",
        "sim_status": "Active",
        "note": "SIM details are mock data."
    }

# ---- Whitelist Commands (Owner Only) ----
async def wladd_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Admins only.")
        return
    # Implement whitelist add logic here (if needed)
    await update.message.reply_text("✅ Whitelist add command (owner only).")

async def wlremove_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Admins only.")
        return
    await update.message.reply_text("✅ Whitelist remove command (owner only).")

async def wllist_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Admins only.")
        return
    await update.message.reply_text("📋 Whitelist list command (owner only).")

# ======================== CALLBACK HANDLER ========================

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "info":
        await query.answer()
        await query.message.reply_text("📊 Send `/info <UID>`")
    elif data == "like":
        await query.answer()
        await query.message.reply_text("❤️ Send `/like <UID>`")
    elif data == "multilike":
        await query.answer()
        await query.message.reply_text("🔥 Send `/multilike <count> <UID>`")
    elif data == "jwt":
        await query.answer()
        await query.message.reply_text("🔐 Send `/jwt <UID> <Password>`")
    elif data == "ffxxxf":
        await query.answer()
        await ffxxxf_command(update, context)
    elif data == "stats":
        await stats_command(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data == "settings":
        await settings_menu(update, context, edit=True, query=query)
    elif data == "number_tools":
        await number_tools_menu(update, context, query=query)
    elif data == "email_tools":
        await email_tools_menu(update, context, query=query)
    elif data == "security_tools":
        await security_tools_menu(update, context, query=query)
    elif data == "telegram_tools":
        await telegram_tools_menu(update, context, query=query)
    elif data == "game_tools":
        await game_tools_menu(update, context, query=query)
    elif data == "like_tools":
        await like_tools_menu(update, context, query=query)
    elif data == "number_detail":
        await number_detail_handler(update, context, query=query)
    elif data == "sim_details":
        await sim_details_handler(update, context, query=query)
    elif data == "gmail_generate":
        await gmail_generate_handler(update, context, query=query)
    elif data == "check_inbox":
        await check_inbox_handler(update, context, query=query)
    elif data == "secret":
        await secret_handler(update, context, query=query)
    elif data == "facebook_login":
        await facebook_login_handler(update, context, query=query)
    elif data == "telegram_login":
        await telegram_login_handler(update, context, query=query)
    elif data == "unlimited":
        await unlimited_handler(update, context, query=query)
    elif data == "sensitivity":
        await sensitivity_handler(update, context, query=query)
    elif data.startswith("sens_"):
        await show_sensitivity_preset(update, context, query=query)
    elif data == "like_token_gen":
        await like_token_gen_handler(update, context, query=query)
    elif data == "account_gen":
        await account_gen_handler(update, context, query=query)
    elif data == "daily_spin":
        await daily_spin_handler(update, context, query=query)
    elif data == "visit_post":
        await visit_post_handler(update, context, query=query)
    elif data == "download_accounts":
        await download_accounts_handler(update, context, query=query)
    elif data == "settings_back":
        await settings_menu(update, context, edit=True, query=query)
    elif data == "back_main":
        keyboard = [
            [InlineKeyboardButton("📊 Player Info", callback_data="info"),
             InlineKeyboardButton("❤️ Like", callback_data="like")],
            [InlineKeyboardButton("🔥 Multi-Like", callback_data="multilike"),
             InlineKeyboardButton("🔐 JWT", callback_data="jwt")],
            [InlineKeyboardButton("👾 FF_XXXF", callback_data="ffxxxf"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats"),
             InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = """
🔥 *Free Fire Ultimate Bot* 🔥

*Commands:*
/info <UID> – Player Info (with Outfit/Banner)
/like <UID> – Send 1 Like + Token
/multilike <count> <UID> – Multiple Likes
/givelike <token> <UID> – Use Like Token
/jwt <UID> <Password> – Generate JWT
/access_token <UID> <Password> – Get Access Token
/gw <UID> <Password> – GW Token + Full Data
/generate <nickname> <count> – Generate Real Guest Accounts (with Mock Fallback)
/ffxxxf – Quick generate 5 FF_XXXF accounts
/spin – Daily Spin (Win Points)
/stats – Bot Stats

👉 Click buttons below!
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await query.answer()
        await query.edit_message_text("❌ Unknown option.")

# ======================== TEXT HANDLER ========================

async def handle_text(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    state = context.user_data.get("state")
    if state == "number_detail":
        await number_detail_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    elif state == "sim_details":
        await sim_details_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    elif state == "secret":
        await secret_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    elif state == "facebook_login":
        await facebook_login_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    elif state == "telegram_login":
        await telegram_login_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    elif state == "like_token_gen":
        await like_token_gen_handler(update, context, query=None)
        context.user_data["state"] = None
        return
    if text.isdigit():
        context.args = [text]
        await info_command(update, context)
        return
    await update.message.reply_text("❌ Send a valid UID or use commands. Use /help for list.")

# ======================== MAIN ========================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("like", like_command))
    app.add_handler(CommandHandler("givelike", givelike_command))
    app.add_handler(CommandHandler("multilike", multilike_command))
    app.add_handler(CommandHandler("jwt", jwt_command))
    app.add_handler(CommandHandler("access_token", access_token_command))
    app.add_handler(CommandHandler("gw", gw_command))
    app.add_handler(CommandHandler("kid", kid_command))
    app.add_handler(CommandHandler("uidc", uidc_command))
    app.add_handler(CommandHandler("parse", parse_command))
    app.add_handler(CommandHandler("icon", icon_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("generate", generate_command))
    app.add_handler(CommandHandler("ffxxxf", ffxxxf_command))
    app.add_handler(CommandHandler("spin", spin_command))
    app.add_handler(CommandHandler("points", points_command))

    app.add_handler(CommandHandler("wladd", wladd_command))
    app.add_handler(CommandHandler("wlremove", wlremove_command))
    app.add_handler(CommandHandler("wllist", wllist_command))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot started successfully – Owner: 8037300335, all restrictions bypassed, generator with fallback.")
    app.run_polling()

if __name__ == "__main__":
    main()
