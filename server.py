import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_CONTENT = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>RS TOKEN — TON Cloud Mining</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #07090e; color: #f1f5f9; touch-action: manipulation; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glass { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(56, 189, 248, 0.15); }
    .glow-cyan { box-shadow: 0 0 25px rgba(6, 182, 212, 0.35); }
    .pulse-ring { animation: pulse 2s infinite cubic-bezier(0.66, 0, 0, 1); }
    @keyframes pulse { to { box-shadow: 0 0 0 16px rgba(34, 197, 94, 0); } }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between pb-24 select-none">
  <!-- Top Header -->
  <header class="p-4 border-b border-slate-800 glass sticky top-0 z-40">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white text-lg shadow-lg">
          RS
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="font-bold text-sm text-white">RS TOKEN</h1>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">TON</span>
          </div>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
            <span class="text-[11px] text-slate-400 font-mono">1,248 Online</span>
          </div>
        </div>
      </div>
      <button onclick="toggleWalletModal()" id="wallet-btn" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
        <i class="fa-solid fa-wallet"></i>
        <span id="wallet-btn-text">Connect Wallet</span>
      </button>
    </div>
    <div id="notice-banner" class="mt-3 px-3 py-2 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center gap-2 text-xs text-cyan-200">
      <i class="fa-solid fa-bullhorn text-cyan-400"></i>
      <span class="truncate" id="notice-text">📢 RS TOKEN মাইনিং লাইভ! প্রতি ঘণ্টায় ৬০ RS টোকেন ফ্রিতে মাইনিং করুন।</span>
    </div>
  </header>

  <!-- Main Tabs -->
  <main class="flex-1 p-4 max-w-md mx-auto w-full">
    <!-- 1. MINING TAB -->
    <section id="tab-mining" class="space-y-4">
      <div class="p-5 rounded-2xl glass glow-cyan text-center relative overflow-hidden">
        <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">মোট ব্যালেন্স</p>
        <div class="flex items-baseline justify-center gap-2">
          <span class="text-4xl font-extrabold text-white font-mono" id="balance-display">250.00</span>
          <span class="text-lg font-bold text-cyan-400">RS</span>
        </div>
        <p class="text-xs text-slate-400 mt-1 font-mono">≈ $<span id="usd-value">13.50</span> USD (TON Network)</p>
        <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
          <span class="text-slate-400"><i class="fa-solid fa-chart-line text-cyan-400 mr-1"></i> RS রেট: <b class="text-white font-mono">$0.054</b></span>
          <span class="text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded-full">+14.2% ↗</span>
        </div>
      </div>

      <div class="p-5 rounded-2xl glass text-center">
        <div class="relative w-32 h-32 mx-auto mb-3 flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border-4 border-slate-800"></div>
          <div class="absolute inset-0 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" style="animation-duration: 4s;"></div>
          <div class="w-24 h-24 rounded-full bg-slate-900 flex flex-col items-center justify-center">
            <i class="fa-solid fa-cube text-cyan-400 text-xl mb-1"></i>
            <span class="text-[10px] font-bold text-slate-400 uppercase">Mining</span>
            <span class="text-[11px] font-mono font-bold text-emerald-400">+60 RS/hr</span>
          </div>
        </div>
        <p class="text-xs font-semibold text-emerald-400 mb-3"><span class="w-2 h-2 rounded-full bg-emerald-400 inline-block mr-1"></span> অটো ক্লাউড মাইনিং সক্রিয়</p>
        <button onclick="claimMiningReward()" class="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25 active:scale-95 transition-all">
          ⚡ ক্লেম করুন (+24.00 RS)
        </button>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <button onclick="openTab('wallet')" class="p-3.5 rounded-xl glass text-left hover:bg-slate-800/60">
          <i class="fa-solid fa-paper-plane text-emerald-400 text-base mb-1"></i>
          <p class="text-xs text-slate-400">২৪ ঘণ্টা অটো পেমেন্ট</p>
          <p class="text-sm font-bold text-white">উইথড্র করুন</p>
        </button>
        <button onclick="openTab('tasks')" class="p-3.5 rounded-xl glass text-left hover:bg-slate-800/60">
          <i class="fa-solid fa-gift text-amber-400 text-base mb-1"></i>
          <p class="text-xs text-slate-400">বোনাস টোকেন</p>
          <p class="text-sm font-bold text-white">টাস্ক ও অ্যাড</p>
        </button>
      </div>
    </section>

    <!-- 2. WALLET & WITHDRAW TAB -->
    <section id="tab-wallet" class="space-y-4 hidden">
      <div class="p-4 rounded-2xl glass">
        <h2 class="text-sm font-bold text-white mb-1">RS / USDT লাইভ মার্কেট</h2>
        <div class="h-36 w-full bg-slate-950 rounded-xl p-2 flex items-end">
          <canvas id="priceChart" class="w-full h-full"></canvas>
        </div>
        <div class="grid grid-cols-3 gap-2 mt-3">
          <button onclick="alert('🛒 Tonkeeper ওপেন হচ্ছে... $0.054 রেটে RS টোকেন কিনুন।')" class="py-2 rounded-xl bg-emerald-500 text-white font-bold text-xs">বাই (Buy)</button>
          <button onclick="alert('🔒 RS টোকেন হোল্ড লক সক্রিয়! বোনাস +18.5% APY')" class="py-2 rounded-xl bg-blue-600 text-white font-bold text-xs">হোল্ড (Hold)</button>
          <button onclick="alert('💸 সেল অর্ডার প্রস্তুত! মিনিমাম সেল ৫০০ RS।')" class="py-2 rounded-xl bg-rose-600 text-white font-bold text-xs">সেল (Sell)</button>
        </div>
      </div>

      <div class="p-5 rounded-2xl glass border-cyan-500/30">
        <h3 class="text-sm font-bold text-white mb-2">⚡ ২৪ ঘণ্টা অটো পেমেন্ট উইথড্র</h3>
        <p class="text-xs text-slate-400 mb-3">Tonkeeper ওয়ালেট অ্যাড্রেস দিন। ২৪ ঘণ্টা পর উইথড্র বাটনে ক্লিক করলে স্বয়ংক্রিয়ভাবে ব্যালেন্স ট্রান্সফার হবে।</p>
        <div class="space-y-3">
          <input type="text" id="withdraw-address" placeholder="EQBv... বা UQBv... (Tonkeeper)" class="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono">
          <input type="number" id="withdraw-amount" value="500" min="500" placeholder="টোকেন পরিমাণ (মিনিমাম ৫০০ RS)" class="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono">
          <button onclick="processWithdrawal()" class="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold text-xs shadow-lg active:scale-95">
            উইথড্র রিকোয়েস্ট পাঠান
          </button>
        </div>
      </div>
    </section>

    <!-- 3. TASKS & ADS TAB -->
    <section id="tab-tasks" class="space-y-3 hidden">
      <div class="p-3.5 rounded-xl glass flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-white">ভিডিও অ্যাড দেখুন</p>
          <p class="text-[11px] text-emerald-400 font-mono font-bold">+25 RS</p>
        </div>
        <button onclick="watchVideoAd()" id="ad-btn" class="px-3.5 py-1.5 rounded-lg bg-cyan-500 text-white text-xs font-bold">দেখুন</button>
      </div>
      <div class="p-3.5 rounded-xl glass flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-white">অফিসিয়াল টেলিগ্রাম চ্যানেল</p>
          <p class="text-[11px] text-emerald-400 font-mono font-bold">+50 RS</p>
        </div>
        <button onclick="window.open('https://t.me/RSTokenOfficial','_blank'); balance+=50; updateBalanceDisplay(); alert('+50 RS যুক্ত হয়েছে!');" class="px-3.5 py-1.5 rounded-lg bg-slate-800 text-white text-xs font-bold">ক্লেম</button>
      </div>
    </section>

    <!-- 4. LEADERBOARD TAB -->
    <section id="tab-leaderboard" class="space-y-3 hidden">
      <div class="p-4 rounded-2xl glass">
        <h3 class="text-xs font-bold text-slate-300 uppercase mb-3">শীর্ষ মাইনার্স লিডারবোর্ড 🏆</h3>
        <div class="space-y-2 text-xs font-mono">
          <div class="flex justify-between p-2 rounded bg-amber-500/10 text-amber-400 font-bold"><span>🥇 1. @ton_whale99</span><span>48,750 RS</span></div>
          <div class="flex justify-between p-2 rounded bg-slate-800 text-white font-bold"><span>🥈 2. @crypto_reja</span><span>39,400 RS</span></div>
          <div class="flex justify-between p-2 rounded bg-amber-700/10 text-amber-600 font-bold"><span>🥉 3. @shakib_ton</span><span>32,150 RS</span></div>
        </div>
      </div>
    </section>

    <!-- 5. ADMIN PANEL TAB -->
    <section id="tab-admin" class="space-y-3 hidden">
      <div class="p-4 rounded-2xl glass border-purple-500/30">
        <h2 class="text-sm font-bold text-white mb-2">অ্যাডমিন কন্ট্রোল প্যানেল</h2>
        <textarea id="admin-notice-input" rows="2" class="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white" placeholder="বটের সকল ইউজারের জন্য নোটিশ লিখুন..."></textarea>
        <button onclick="const t=document.getElementById('admin-notice-input').value; if(t){document.getElementById('notice-text').innerText='📢 '+t; alert('নোটিশ ব্রডকাস্ট সফল!');}" class="mt-2 w-full py-2 rounded-xl bg-purple-600 text-white font-bold text-xs">নোটিশ পাঠান</button>
      </div>
    </section>
  </main>

  <!-- Bottom Navigation -->
  <nav class="fixed bottom-0 inset-x-0 glass border-t border-slate-800 px-4 py-2 flex items-center justify-around z-40 max-w-md mx-auto">
    <button onclick="openTab('mining')" id="nav-mining" class="flex flex-col items-center gap-1 text-cyan-400"><i class="fa-solid fa-cube text-base"></i><span class="text-[10px] font-bold">মাইনিং</span></button>
    <button onclick="openTab('wallet')" id="nav-wallet" class="flex flex-col items-center gap-1 text-slate-400"><i class="fa-solid fa-wallet text-base"></i><span class="text-[10px] font-bold">ওয়ালেট</span></button>
    <button onclick="openTab('tasks')" id="nav-tasks" class="flex flex-col items-center gap-1 text-slate-400"><i class="fa-solid fa-list-check text-base"></i><span class="text-[10px] font-bold">টাস্ক</span></button>
    <button onclick="openTab('leaderboard')" id="nav-leaderboard" class="flex flex-col items-center gap-1 text-slate-400"><i class="fa-solid fa-ranking-star text-base"></i><span class="text-[10px] font-bold">লিডারবোর্ড</span></button>
    <button onclick="openTab('admin')" id="nav-admin" class="flex flex-col items-center gap-1 text-slate-400"><i class="fa-solid fa-gear text-base"></i><span class="text-[10px] font-bold">অ্যাডমিন</span></button>
  </nav>

  <script>
    if (window.Telegram && window.Telegram.WebApp) { window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand(); }
    let balance = parseFloat(localStorage.getItem('rs_balance') || '250.00');
    function updateBalanceDisplay() {
      document.getElementById('balance-display').innerText = balance.toFixed(2);
      document.getElementById('usd-value').innerText = (balance * 0.054).toFixed(2);
      localStorage.setItem('rs_balance', balance.toString());
    }
    updateBalanceDisplay();

    function openTab(id) {
      ['mining','wallet','tasks','leaderboard','admin'].forEach(t => {
        document.getElementById('tab-'+t).classList.add('hidden');
        document.getElementById('nav-'+t).className = 'flex flex-col items-center gap-1 text-slate-400';
      });
      document.getElementById('tab-'+id).classList.remove('hidden');
      document.getElementById('nav-'+id).className = 'flex flex-col items-center gap-1 text-cyan-400';
      if(id === 'wallet') drawChart();
    }

    setInterval(() => { balance += 0.0166; updateBalanceDisplay(); }, 1000);
    function claimMiningReward() { balance += 24.0; updateBalanceDisplay(); alert('🎉 সফল! +24.00 RS যোগ হয়েছে!'); }
    function toggleWalletModal() {
      const addr = 'EQBv...' + Math.floor(1000 + Math.random() * 9000);
      document.getElementById('wallet-btn-text').innerText = addr;
      document.getElementById('withdraw-address').value = addr;
      alert('✅ Tonkeeper ওয়ালেট কানেক্ট হয়েছে: ' + addr);
    }
    function processWithdrawal() {
      const addr = document.getElementById('withdraw-address').value;
      const amt = parseFloat(document.getElementById('withdraw-amount').value || '0');
      if (!addr) { alert('Tonkeeper ওয়ালেট অ্যাড্রেস দিন!'); return; }
      if (amt < 500) { alert('মিনিমাম উইথড্র লিমিট ৫০০ RS!'); return; }
      if (amt > balance) { alert('পর্যাপ্ত ব্যালেন্স নেই!'); return; }
      balance -= amt; updateBalanceDisplay();
      alert('🚀 সফল! ২৪ ঘণ্টার মধ্যে ' + amt + ' RS টোকেন স্বয়ংক্রিয়ভাবে ' + addr + '-এ ট্রান্সফার হবে।');
    }
    function watchVideoAd() {
      const btn = document.getElementById('ad-btn');
      btn.innerText = 'অপেক্ষা করুন... (10s)'; btn.disabled = true;
      let count = 10;
      const t = setInterval(() => {
        count--;
        if (count > 0) btn.innerText = count + 's';
        else { clearInterval(t); balance += 25; updateBalanceDisplay(); btn.innerText = 'সম্পন্ন ✅'; alert('🎉 +25 RS যোগ হয়েছে!'); }
      }, 1000);
    }
    function drawChart() {
      const c = document.getElementById('priceChart'); if(!c) return;
      const ctx = c.getContext('2d'); c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
      ctx.clearRect(0, 0, c.width, c.height);
      const pts = [20, 35, 30, 48, 42, 60, 55, 75, 70, 95];
      const step = c.width / (pts.length - 1);
      ctx.beginPath(); ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 3;
      pts.forEach((p, i) => { const y = c.height - (p / 100) * c.height; if (i === 0) ctx.moveTo(0, y); else ctx.lineTo(i * step, y); });
      ctx.stroke();
    }
  </script>
</body>
</html>"""

class WebServiceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode('utf-8'))
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

def run():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServiceHandler)
    print(f"🚀 RS TOKEN Server running on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run()
