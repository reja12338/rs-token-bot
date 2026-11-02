"""
File: server.py
Lightweight High-Performance Server for RS TOKEN Platform
"""
import os
import json
import time
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = {
    "notice": "🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!",
    "miningSpeed": 60,
    "tokenPriceUSD": 0.054,
    "tokenPriceTON": 0.0098,
    "baseJoined": 0,
    "baseOnline": 1,
    "require1DollarHold": True,
    "minWithdrawRS": 100,
    "masterHotWallet": "EQD_RS_AutoPayout_MasterPool_TON99",
    "contractAddress": "EQBv_RSTOKEN_Official_Jetton_MasterPool_99",
    "dexSwapUrl": "https://ston.fi/swap?chartVisible=true",
    "refReward": 25,
    "refCommission": 10,
    "users": {},
    "leaderboard": [],
    "ads": [
        {"id": 1, "name": "Monetag SmartLink", "duration": 15, "reward": 15, "url": "https://example.com/monetag"},
        {"id": 2, "name": "Adsterra High CPM Ad #2", "duration": 20, "reward": 20, "url": "https://example.com/adsterra"},
        {"id": 3, "name": "PropellerAds Popunder #3", "duration": 15, "reward": 10, "url": "https://example.com/propeller"}
    ],
    "tasks": [
        {"id": 1, "title": "Join Official RS TOKEN Channel", "members": "Official", "reward": 50, "url": "https://t.me/RSTokenOfficial"},
        {"id": 2, "title": "Join RS TOKEN Community Chat", "members": "Community", "reward": 40, "url": "https://t.me/RSTokenChat"},
        {"id": 3, "title": "Join RS VIP Signals & News", "members": "VIP", "reward": 30, "url": "https://t.me/RSTokenSignals"}
    ]
}

def load_file_content(filename, fallback_title):
    paths = [filename, os.path.join(os.path.dirname(__file__), filename), os.path.join(os.getcwd(), filename)]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return f"<html><body><h1>{fallback_title}</h1><p>File {filename} not found.</p></body></html>"

class WebServiceHandler(BaseHTTPRequestHandler):
    def _send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/health', '/healthz', '/ping'):
            self.send_response(200)
            self._send_cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode('utf-8'))
            return

        if path == '/api/settings':
            real_count = len(DB["users"])
            resp_data = dict(DB)
            resp_data["realUsersCount"] = real_count
            resp_data["joinedCount"] = DB["baseJoined"] + real_count
            resp_data["onlineCount"] = max(1, DB["baseOnline"] if DB["baseOnline"] > 0 else real_count)
            self.send_response(200)
            self._send_cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp_data).encode('utf-8'))
            return

        if path == '/admin' or path.startswith('/admin/'):
            content = load_file_content("admin.html", "RS TOKEN Admin Panel")
            self.send_response(200)
            self._send_cors()
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            return

        content = load_file_content("dashboard.html", "RS TOKEN Mining Dashboard")
        self.send_response(200)
        self._send_cors()
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        if path == '/api/user/sync':
            try:
                data = json.loads(body.decode('utf-8'))
                uid = str(data.get("uid", "miner_1"))
                DB["users"][uid] = {
                    "name": data.get("name", "Miner"),
                    "coins": float(data.get("coins", 0)),
                    "wallet": data.get("wallet", None),
                    "lastSeen": time.time()
                }
                real_count = len(DB["users"])
                resp = {
                    "success": True,
                    "joinedCount": DB["baseJoined"] + real_count,
                    "onlineCount": max(1, DB["baseOnline"] if DB["baseOnline"] > 0 else real_count),
                    "notice": DB["notice"],
                    "miningSpeed": DB["miningSpeed"],
                    "tokenPriceUSD": DB["tokenPriceUSD"],
                    "contractAddress": DB["contractAddress"],
                    "ads": DB["ads"],
                    "tasks": DB["tasks"]
                }
                self.send_response(200)
                self._send_cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
                return
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

        if path == '/api/settings':
            try:
                data = json.loads(body.decode('utf-8'))
                for k, v in data.items():
                    if k in DB: DB[k] = v
                self.send_response(200)
                self._send_cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                return
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()

def run():
    if os.path.exists("bot.py"):
        try:
            import subprocess
            subprocess.Popen(["python3", "bot.py"])
        except Exception:
            try: subprocess.Popen(["python", "bot.py"])
            except Exception: pass

    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), WebServiceHandler)
    server.serve_forever()

if __name__ == '__main__':
    run()
