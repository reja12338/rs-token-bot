import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# সার্ভারে শেয়ার্ড ডাটা
APP_STATE = {
    "notice": "📢 RS TOKEN মাইনিং লাইভ! প্রতি ঘণ্টায় ৬০ RS টোকেন ফ্রিতে ক্লাউড মাইনিং করুন।",
    "tokenPriceUSD": 0.054,
    "miningRatePerHour": 60,
    "totalJoinedUsers": 14820,
    "onlineUsersCount": 1248,
    "minWithdrawRS": 500,
    "autoPayoutEnabled": True
}

# ১. সাধারণ ইউজারদের জন্য মিনি অ্যাপ (৫টি ট্যাব, অ্যাডমিন ট্যাব সম্পূর্ণ লুকানো)
USER_HTML = """<!DOCTYPE html>
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
    ::-webkit-scrollbar { display: none; }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between pb-24 select-none">

  <!-- Header -->
  <header class="p-4 border-b border-slate-800 glass sticky top-0 z-40">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- RS লোগোতে ৩ বার ক্লিক করলে সিক্রেট অ্যাডমিন লগইন আসবে -->
        <div onclick="handleLogoClick()" class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-cyan-500/20 cursor-pointer active:scale-95">
          RS
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="font-bold text-sm text-white">RS TOKEN</h1>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">TON</span>
          </div>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
            <span class="text-[11px] text-slate-400 font-mono" id="online-counter">1,248 Online</span>
          </div>
        </div>
      </div>

      <button onclick="toggleWalletModal()" id="wallet-btn" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold hover:bg-cyan-500/20 transition-all">
        <i class="fa-solid fa-wallet"></i>
        <span id="wallet-btn-text">Connect Wallet</span>
      </button>
    </div>

    <!-- Live Notice -->
    <div id="notice-banner" class="mt-3 px-3 py-2 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center gap-2 text-xs text-cyan-200">
      <i class="fa-solid fa-bullhorn text-cyan-400 animate-bounce"></i>
      <span class="truncate" id="notice-text">📢 RS TOKEN মাইনিং লাইভ! প্রতি ঘণ্টায় ৬০ RS টোকেন ফ্রিতে ক্লাউড মাইনিং করুন।</span>
    </div>
  </header>

  <!-- Main Tabs -->
  <main class="flex-1 p-4 max-w-md mx-auto w-full">

    <!-- 1. MINING TAB -->
    <section id="tab-mining" class="space-y-4">
      <div class="p-5 rounded-2xl glass glow-cyan text-center relative overflow-hidden">
        <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">আপনার মোট ব্যালেন্স</p>
        <div class="flex items-baseline justify-center gap-2">
          <span class="text-4xl font-extrabold text-white tracking-tight font-mono tabular-nums" id="balance-display">250.00</span>
          <span class="text-lg font-bold text-cyan-400">RS</span>
        </div>
        <p class="text-xs text-slate-400 mt-1 font-mono">≈ $<span id="usd-value">13.50</span> USD · ≈ <span id="ton-value">2.45</span> TON</p>

        <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5 text-slate-400">
            <i class="fa-solid fa-chart-line text-cyan-400"></i>
            <span>RS রেট:</span>
            <span class="text-white font-mono font-bold" id="rate-display">$0.054</span>
          </div>
          <span class="text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <i class="fa-solid fa-arrow-trend-up"></i> +14.2% ↗
          </span>
        </div>
      </div>

      <div class="p-5 rounded-2xl glass text-center relative overflow-hidden">
        <div class="relative w-44 h-44 mx-auto mb-3 flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border-4 border-slate-800"></div>
          <div class="absolute inset-0 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" style="animation-duration: 3.5s;"></div>
          
          <div class="w-36 h-36 rounded-full bg-slate-900 border border-slate-700 flex flex-col items-center justify-center shadow-inner">
            <i class="fa-solid fa-cube text-cyan-400 text-3xl mb-1 animate-pulse"></i>
            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Cloud Mining</span>
            <span class="text-xs font-mono font-bold text-emerald-400" id="speed-display">+60 RS/hr</span>
          </div>
        </div>

        <div class="flex items-center justify-center gap-2 mb-3">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 pulse-ring"></span>
          <span class="text-xs font-semibold text-emerald-400">অটোমেটিক ক্লাউড মাইনিং সক্রিয় (ট্যাপ পয়েন্ট নয়)</span>
        </div>

        <button onclick="toggleMining()" id="mining-toggle-btn" class="w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2">
          <i class="fa-solid fa-pause" id="mining-icon"></i>
          <span id="mining-btn-text">মাইনিং পজ করুন</span>
        </button>
      </div>

      <!-- Live Community Stats -->
      <div class="grid grid-cols-2 gap-2.5">
        <div class="p-3.5 rounded-xl glass text-center">
          <i class="fa-solid fa-users text-cyan-400 text-base mb-1"></i>
          <p class="text-[10px] text-slate-400 uppercase font-bold">মোট জয়েন মেম্বার</p>
          <p class="text-lg font-extrabold text-white font-mono" id="stat-joined">14,820+</p>
        </div>
        <div class="p-3.5 rounded-xl glass text-center">
          <i class="fa-solid fa-circle-nodes text-emerald-400 text-base mb-1"></i>
          <p class="text-[10px] text-slate-400 uppercase font-bold">অনলাইনে সক্রিয়</p>
          <p class="text-lg font-extrabold text-emerald-400 font-mono" id="stat-online">1,248 LIVE</p>
        </div>
      </div>

      <!-- Leaderboard -->
      <div class="p-4 rounded-2xl glass">
        <h3 class="text-xs font-bold text-slate-300 uppercase mb-3 flex items-center gap-1.5">
          <i class="fa-solid fa-trophy text-amber-400"></i> শীর্ষ মাইনার্স লিডারবোর্ড
        </h3>
        <div class="space-y-2 text-xs font-mono">
          <div class="flex justify-between items-center p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <span class="text-amber-400 font-bold">🥇 1. @ton_whale99</span><span class="text-white font-bold">48,750 RS</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded-lg bg-slate-800/80">
            <span class="text-slate-300 font-bold">🥈 2. @crypto_reja</span><span class="text-white font-bold">39,400 RS</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded-lg bg-amber-700/10">
            <span class="text-amber-600 font-bold">🥉 3. @shakib_ton</span><span class="text-white font-bold">32,150 RS</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. ADS TAB -->
    <section id="tab-ads" class="space-y-4 hidden">
      <div class="p-4 rounded-2xl glass">
        <h2 class="text-sm font-bold text-white mb-1">ভিডিও অ্যাড দেখুন</h2>
        <p class="text-xs text-slate-400">প্রতিটি ভিডিও অ্যাড দেখে ইনস্ট্যান্ট ফ্রি RS টোকেন পান।</p>
      </div>

      <div class="space-y-2.5">
        <div class="p-3.5 rounded-xl glass flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center"><i class="fa-solid fa-play"></i></div>
            <div><p class="text-xs font-bold text-white">Tonkeeper Web3 ইকোসিস্টেম</p><p class="text-[11px] text-emerald-400 font-mono font-bold">+25 RS</p></div>
          </div>
          <button onclick="watchVideoAd(1, 25)" id="ad-btn-1" class="px-3.5 py-1.5 rounded-lg bg-cyan-500 text-white text-xs font-bold">দেখুন</button>
        </div>
        <div class="p-3.5 rounded-xl glass flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center"><i class="fa-solid fa-video"></i></div>
            <div><p class="text-xs font-bold text-white">Telegram Launchpool স্পন্সর</p><p class="text-[11px] text-emerald-400 font-mono font-bold">+30 RS</p></div>
          </div>
          <button onclick="watchVideoAd(2, 30)" id="ad-btn-2" class="px-3.5 py-1.5 rounded-lg bg-cyan-500 text-white text-xs font-bold">দেখুন</button>
        </div>
      </div>
    </section>

    <!-- 3. TASKS TAB -->
    <section id="tab-tasks" class="space-y-4 hidden">
      <div class="p-4 rounded-2xl glass">
        <h2 class="text-sm font-bold text-white mb-1">কমিউনিটি টাস্ক সেন্টার</h2>
        <p class="text-xs text-slate-400">টাস্ক সম্পন্ন করে বোনাস টোকেন ক্লেইম করুন।</p>
      </div>
      <div class="space-y-2.5">
        <div class="p-3.5 rounded-xl glass flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center"><i class="fa-brands fa-telegram"></i></div>
            <div><p class="text-xs font-bold text-white">অফিসিয়াল Telegram চ্যানেল</p><p class="text-[11px] text-emerald-400 font-mono font-bold">+50 RS</p></div>
          </div>
          <button onclick="doTask('channel', 50, 'https://t.me/RSTokenOfficial')" id="task-channel" class="px-3.5 py-1.5 rounded-lg bg-slate-800 text-white text-xs font-bold">ক্লেম</button>
        </div>
        <div class="p-3.5 rounded-xl glass flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center"><i class="fa-solid fa-users"></i></div>
            <div><p class="text-xs font-bold text-white">অফিসিয়াল চ্যাট গ্রুপ</p><p class="text-[11px] text-emerald-400 font-mono font-bold">+50 RS</p></div>
          </div>
          <button onclick="doTask('group', 50, 'https://t.me/RSTokenChat')" id="task-group" class="px-3.5 py-1.5 rounded-lg bg-slate-800 text-white text-xs font-bold">ক্লেম</button>
        </div>
      </div>
    </section>

    <!-- 4. REFERRAL TAB -->
    <section id="tab-referral" class="space-y-4 hidden">
      <div class="p-5 rounded-2xl glass text-center">
        <div class="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-2 text-xl">
          <i class="fa-solid fa-user-plus"></i>
        </div>
        <h2 class="text-sm font-bold text-white mb-1">বন্ধুদের ইনভাইট করুন</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">প্রতি রেফারে ১০০ RS টোকেন ইনস্ট্যান্ট বোনাস পান!</p>
      </div>

      <div class="p-4 rounded-xl glass space-y-3">
        <label class="text-[11px] font-bold text-slate-400 uppercase">আপনার পার্সোনাল রেফারেল লিংক:</label>
        <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between gap-2">
          <span class="text-xs font-mono text-cyan-300 truncate" id="ref-link">https://t.me/rs_token_mining_bot?start=ref7450</span>
          <button onclick="copyRefLink()" class="px-3 py-1 rounded-lg bg-cyan-500 text-white text-xs font-bold">কপি</button>
        </div>
        <button onclick="shareOnTelegram()" class="w-full py-3 rounded-xl bg-blue-600 text-white font-bold text-xs flex items-center justify-center gap-2">
          <i class="fa-brands fa-telegram"></i> টেলিগ্রামে শেয়ার করুন
        </button>
      </div>
    </section>

    <!-- 5. WALLET TAB -->
    <section id="tab-wallet" class="space-y-4 hidden">
      <div class="p-4 rounded-2xl glass">
        <div class="flex items-center justify-between mb-3">
          <div><h2 class="text-sm font-bold text-white">RS / USDT লাইভ মার্কেট</h2><p class="text-xs text-slate-400 font-mono">TON DEX</p></div>
          <div class="text-right"><p class="text-base font-bold text-emerald-400 font-mono" id="chart-price">$0.0542</p><p class="text-[11px] text-emerald-400">Bullish ↗</p></div>
        </div>
        <div class="h-40 w-full bg-slate-950 rounded-xl p-2 flex items-end"><canvas id="priceChart" class="w-full h-full"></canvas></div>
        <div class="grid grid-cols-3 gap-2 mt-3">
          <button onclick="alert('🛒 Tonkeeper ওপেন হচ্ছে... $0.054 রেটে RS টোকেন কিনুন।')" class="py-2.5 rounded-xl bg-emerald-500 text-white font-bold text-xs">বাই (Buy)</button>
          <button onclick="alert('🔒 RS টোকেন হোল্ড লক সক্রিয়! +18.5% APY বোনাস')" class="py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs">হোল্ড (Hold)</button>
          <button onclick="alert('💸 সেল অর্ডার প্রস্তুত! মিনিমাম সেল ৫০০ RS।')" class="py-2.5 rounded-xl bg-rose-600 text-white font-bold text-xs">সেল (Sell)</button>
        </div>
      </div>

      <!-- 24h Auto Payout -->
      <div class="p-5 rounded-2xl glass border-cyan-500/30">
        <h3 class="text-sm font-bold text-white mb-1"><i class="fa-solid fa-bolt-lightning text-cyan-400 mr-1"></i> ২৪ ঘণ্টা অটো পেমেন্ট উইথড্র</h3>
        <p class="text-xs text-slate-400 mb-3">Tonkeeper ওয়ালেট অ্যাড্রেস দিন। ২৪ ঘণ্টা পর উইথড্র বাটনে ক্লিক করার সাথে সাথে ব্যালেন্স ট্রান্সফার হবে।</p>
        <div class="space-y-3">
          <input type="text" id="withdraw-address" placeholder="EQBv... বা UQBv... (Tonkeeper)" class="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono focus:border-cyan-400 focus:outline-none">
          <input type="number" id="withdraw-amount" value="500" min="500" class="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono focus:border-cyan-400 focus:outline-none">
          <button onclick="processWithdrawal()" class="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold text-xs shadow-lg active:scale-95">
            উইথড্র রিকোয়েস্ট পাঠান
          </button>
        </div>
      </div>
    </section>
  </main>

  <!-- ৫টি নির্দিষ্ট বটম ট্যাব (অ্যাডমিন সম্পূর্ণ লুকানো) -->
  <nav class="fixed bottom-0 inset-x-0 glass border-t border-slate-800 px-2 py-2 flex items-center justify-around z-40 max-w-md mx-auto">
    <button onclick="openTab('mining')" id="nav-mining" class="flex flex-col items-center gap-1 text-cyan-400 min-w-[56px]"><i class="fa-solid fa-cube text-base"></i><span class="text-[10px] font-bold">মাইনিং</span></button>
    <button onclick="openTab('ads')" id="nav-ads" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-video text-base"></i><span class="text-[10px] font-bold">অ্যাড</span></button>
    <button onclick="openTab('tasks')" id="nav-tasks" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-list-check text-base"></i><span class="text-[10px] font-bold">টাস্ক</span></button>
    <button onclick="openTab('referral')" id="nav-referral" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-users text-base"></i><span class="text-[10px] font-bold">রেফারেল</span></button>
    <button onclick="openTab('wallet')" id="nav-wallet" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-wallet text-base"></i><span class="text-[10px] font-bold">ওয়ালেট</span></button>
  </nav>

  <!-- Wallet Modal -->
  <div id="wallet-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4 hidden">
    <div class="w-full max-w-sm rounded-2xl glass p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-sm font-bold text-white">TON ওয়ালেট কানেক্ট</h3>
        <button onclick="toggleWalletModal()" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <button onclick="selectWallet('Tonkeeper')" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between hover:border-cyan-400">
        <div class="flex items-center gap-2.5">
          <span class="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs">TK</span>
          <span class="text-xs font-bold text-white">Tonkeeper (রেকমেন্ডেড)</span>
        </div>
        <i class="fa-solid fa-chevron-right text-xs text-slate-500"></i>
      </button>
    </div>
  </div>

  <script>
    if (window.Telegram && window.Telegram.WebApp) { window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand(); }
    let balance = parseFloat(localStorage.getItem('rs_balance') || '250.00');
    let isMining = true;
    let connectedWallet = localStorage.getItem('rs_wallet') || null;

    fetch('/api/settings').then(r => r.json()).then(data => {
      if (data.notice) document.getElementById('notice-text').innerText = data.notice;
      if (data.tokenPriceUSD) { document.getElementById('rate-display').innerText = '$' + data.tokenPriceUSD; document.getElementById('chart-price').innerText = '$' + data.tokenPriceUSD; }
      if (data.miningRatePerHour) document.getElementById('speed-display').innerText = '+' + data.miningRatePerHour + ' RS/hr';
      if (data.totalJoinedUsers) document.getElementById('stat-joined').innerText = data.totalJoinedUsers.toLocaleString() + '+';
      if (data.onlineUsersCount) { document.getElementById('online-counter').innerText = data.onlineUsersCount.toLocaleString() + ' Online'; document.getElementById('stat-online').innerText = data.onlineUsersCount.toLocaleString() + ' LIVE'; }
    }).catch(e => console.log(e));

    function updateBalanceDisplay() {
      document.getElementById('balance-display').innerText = balance.toFixed(2);
      document.getElementById('usd-value').innerText = (balance * 0.054).toFixed(2);
      document.getElementById('ton-value').innerText = (balance * 0.0098).toFixed(2);
      localStorage.setItem('rs_balance', balance.toString());
    }
    updateBalanceDisplay();

    setInterval(() => { if (isMining) { balance += 0.0166; updateBalanceDisplay(); } }, 1000);

    function toggleMining() {
      isMining = !isMining;
      document.getElementById('mining-btn-text').innerText = isMining ? 'মাইনিং পজ করুন' : 'মাইনিং শুরু করুন';
      document.getElementById('mining-icon').className = isMining ? 'fa-solid fa-pause' : 'fa-solid fa-play';
    }

    function openTab(id) {
      ['mining','ads','tasks','referral','wallet'].forEach(t => {
        document.getElementById('tab-'+t).classList.add('hidden');
        document.getElementById('nav-'+t).className = 'flex flex-col items-center gap-1 text-slate-400 min-w-[56px]';
      });
      document.getElementById('tab-'+id).classList.remove('hidden');
      document.getElementById('nav-'+id).className = 'flex flex-col items-center gap-1 text-cyan-400 min-w-[56px]';
      if (id === 'wallet') drawChart();
    }

    function toggleWalletModal() { document.getElementById('wallet-modal').classList.toggle('hidden'); }
    function selectWallet(name) {
      connectedWallet = 'EQBv...' + Math.floor(1000 + Math.random() * 9000);
      localStorage.setItem('rs_wallet', connectedWallet);
      document.getElementById('wallet-btn-text').innerText = connectedWallet;
      document.getElementById('withdraw-address').value = connectedWallet;
      toggleWalletModal();
      alert('✅ ' + name + ' ওয়ালেট কানেক্ট সফল: ' + connectedWallet);
    }
    if (connectedWallet) {
      document.getElementById('wallet-btn-text').innerText = connectedWallet;
      document.getElementById('withdraw-address').value = connectedWallet;
    }

    function processWithdrawal() {
      const addr = document.getElementById('withdraw-address').value;
      const amt = parseFloat(document.getElementById('withdraw-amount').value || '0');
      if (!addr) { alert('অনুগ্রহ করে Tonkeeper ওয়ালেট দিন!'); return; }
      if (amt < 500) { alert('মিনিমাম উইথড্র লিমিট ৫০০ RS!'); return; }
      if (amt > balance) { alert('পর্যাপ্ত ব্যালেন্স নেই!'); return; }
      balance -= amt; updateBalanceDisplay();
      alert('🚀 সফল! ২৪ ঘণ্টার মধ্যে ' + amt + ' RS টোকেন ' + addr + '-এ ট্রান্সফার হবে।');
    }

    function watchVideoAd(id, reward) {
      const btn = document.getElementById('ad-btn-' + id);
      btn.disabled = true; let count = 10;
      const timer = setInterval(() => {
        count--;
        if (count > 0) btn.innerText = count + 's';
        else { clearInterval(timer); balance += reward; updateBalanceDisplay(); btn.innerText = 'সম্পন্ন ✅'; alert('🎉 +' + reward + ' RS ব্যালেন্সে যুক্ত হয়েছে!'); }
      }, 1000);
    }

    function doTask(id, reward, link) {
      window.open(link, '_blank');
      balance += reward; updateBalanceDisplay();
      document.getElementById('task-' + id).innerText = 'কমপ্লিট ✅';
      document.getElementById('task-' + id).disabled = true;
    }

    function copyRefLink() {
      navigator.clipboard.writeText('https://t.me/rs_token_mining_bot?start=ref7450');
      alert('✅ রেফারেল লিংক কপি করা হয়েছে!');
    }
    function shareOnTelegram() {
      window.open('https://t.me/share/url?url=https://t.me/rs_token_mining_bot?start=ref7450&text=🚀 RS TOKEN ফ্রি ক্লাউড মাইনিং-এ জয়েন করুন!');
    }

    // লোগোতে ৩ বার ক্লিক করলে সিক্রেট পাসওয়ার্ড বক্স আসবে
    let logoClicks = 0;
    function handleLogoClick() {
      logoClicks++;
      if (logoClicks >= 3) {
        logoClicks = 0;
        const pass = prompt('🔐 অ্যাডমিন প্যানেল পাসওয়ার্ড দিন:');
        if (pass === 'admin' || pass === '2026') {
          window.location.href = '/admin';
        } else if (pass) {
          alert('ভুল পাসওয়ার্ড!');
        }
      }
    }

    function drawChart() {
      const c = document.getElementById('priceChart'); if(!c) return;
      const ctx = c.getContext('2d'); c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
      ctx.clearRect(0, 0, c.width, c.height);
      const pts = [20, 32, 28, 45, 40, 58, 52, 72, 68, 92];
      const step = c.width / (pts.length - 1);
      ctx.beginPath(); ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 3;
      pts.forEach((p, i) => {
        const y = c.height - (p / 100) * c.height;
        if (i === 0) ctx.moveTo(0, y); else ctx.lineTo(i * step, y);
      });
      ctx.stroke();
    }
  </script>
</body>
</html>"""

# ২. আলাদা অ্যাডমিন কন্ট্রোল প্যানেল (শুধুমাত্র ওনারের জন্য /admin রুটে)
ADMIN_HTML = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RS TOKEN — অ্যাডমিন কন্ট্রোল প্যানেল (Owner Only)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #05070c; color: #f1f5f9; }
    .glass { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.25); }
  </style>
</head>
<body class="min-h-screen p-4 sm:p-6 max-w-2xl mx-auto space-y-6">

  <div class="p-5 rounded-2xl glass flex items-center justify-between border-purple-500/40">
    <div class="flex items-center gap-3">
      <div class="w-11 h-11 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center text-xl font-bold border border-purple-500/30">
        <i class="fa-solid fa-shield-halved"></i>
      </div>
      <div>
        <h1 class="text-base font-extrabold text-white">RS TOKEN অ্যাডমিন প্যানেল</h1>
        <p class="text-xs text-purple-300">ওনার কন্ট্রোল সেন্টার (গোপন এক্সেস)</p>
      </div>
    </div>
    <a href="/" class="px-3.5 py-1.5 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold hover:bg-slate-700">
      <i class="fa-solid fa-arrow-left mr-1"></i> বটে ফিরে যান
    </a>
  </div>

  <!-- লাইভ নোটিশ ব্রডকাস্ট -->
  <div class="p-5 rounded-2xl glass space-y-3">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-bullhorn text-purple-400"></i>
      <h2 class="text-sm font-bold text-white">টেলিগ্রাম বটে নোটিশ পাঠান</h2>
    </div>
    <p class="text-xs text-slate-400">এখানে নোটিশ লিখে সেভ করলে সমস্ত ইউজারদের টেলিগ্রাম বটে ও ড্যাশবোর্ডে এটি স্বয়ংক্রিয়ভাবে দেখাবে।</p>
    <textarea id="notice-input" rows="3" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-purple-400" placeholder="সকল ইউজারের জন্য নোটিশ লিখুন..."></textarea>
    <button onclick="saveNotice()" class="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-lg flex items-center justify-center gap-2">
      <i class="fa-solid fa-paper-plane"></i>
      <span>নোটিশ লাইভ ব্রডকাস্ট করুন</span>
    </button>
  </div>

  <!-- ইউজার ও রেট কন্ট্রোল -->
  <div class="p-5 rounded-2xl glass space-y-4">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-sliders text-cyan-400"></i>
      <h2 class="text-sm font-bold text-white">ইউজার ও রেট কন্ট্রোল</h2>
    </div>

    <div class="grid grid-cols-2 gap-3 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মোট মেম্বার সংখ্যা:</label>
        <input type="number" id="joined-input" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">অনলাইন একটিভ সংখ্যা:</label>
        <input type="number" id="online-input" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">টোকেন প্রাইস (USD):</label>
        <input type="number" step="0.001" id="price-input" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মাইনিং স্পিড (RS/hr):</label>
        <input type="number" id="speed-input" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono">
      </div>
    </div>

    <button onclick="saveStatsConfig()" class="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs">
      <i class="fa-solid fa-floppy-disk mr-1"></i> সেটিংস আপডেট করুন
    </button>
  </div>

  <script>
    fetch('/api/settings').then(r => r.json()).then(data => {
      document.getElementById('notice-input').value = data.notice || '';
      document.getElementById('joined-input').value = data.totalJoinedUsers || 14820;
      document.getElementById('online-input').value = data.onlineUsersCount || 1248;
      document.getElementById('price-input').value = data.tokenPriceUSD || 0.054;
      document.getElementById('speed-input').value = data.miningRatePerHour || 60;
    });

    function saveNotice() {
      const notice = document.getElementById('notice-input').value;
      fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({notice: notice})
      }).then(() => alert('✅ নোটিশ সফলভাবে পাবলিশ করা হয়েছে!'));
    }

    function saveStatsConfig() {
      const body = {
        totalJoinedUsers: parseInt(document.getElementById('joined-input').value),
        onlineUsersCount: parseInt(document.getElementById('online-input').value),
        tokenPriceUSD: parseFloat(document.getElementById('price-input').value),
        miningRatePerHour: parseInt(document.getElementById('speed-input').value),
      };
      fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      }).then(() => alert('✅ সেটিংস সফলভাবে আপডেট হয়েছে!'));
    }
  </script>
</body>
</html>"""

class WebServiceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Settings API
        if self.path.startswith('/api/settings'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(APP_STATE).encode('utf-8'))
            return

        # Render Health check
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode('utf-8'))
            return

        # শুধুমাত্র /admin ঠিকানায় আলাদা অ্যাডমিন প্যানেল লোড হবে
        if self.path.startswith('/admin'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode('utf-8'))
            return

        # সাধারণ ইউজারদের জন্য ৫টি মূল ট্যাব
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(USER_HTML.encode('utf-8'))

    def do_POST(self):
        if self.path.startswith('/api/settings'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                for k, v in data.items():
                    if k in APP_STATE:
                        APP_STATE[k] = v
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "state": APP_STATE}).encode('utf-8'))
                return
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()

def run():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServiceHandler)
    print(f"🚀 RS TOKEN Server running on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run()
