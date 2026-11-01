import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Real Dynamic Database stored on Server
DB = {
    "notice": "🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই TON ব্লকচেইনে শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!",
    "miningSpeed": 60,
    "tokenPriceUSD": 0.054,
    "tokenPriceTON": 0.0098,
    "trend": "BULLISH",
    "baseJoined": 0,           # রিয়েল মেম্বার হিসাব: শুরুতে ০ থাকবে
    "baseOnline": 1,           # শুরুতে ১ জন (বর্তমান ইউজার)
    "require1DollarHold": True,
    "minWithdrawRS": 100,
    "autoPayoutEnabled": True,
    "masterHotWallet": "EQD_RS_AutoPayout_MasterPool_TON99",
    "contractAddress": "EQBv_RSTOKEN_Official_Jetton_MasterPool_99",
    "dexSwapUrl": "https://ston.fi/swap?chartVisible=true",
    "refReward": 25,
    "refCommission": 10,
    "users": {},               # { user_id: { "name": ..., "coins": ..., "wallet": ..., "lastSeen": ... } }
    "leaderboard": [],         # রিয়েল মেম্বার লিডারবোর্ড (শুরুতে ফাঁকা)
    "ads": [
        {"id": 1, "name": "Monetag SmartLink", "duration": 15, "reward": 15, "url": "https://example.com/monetag"},
        {"id": 2, "name": "Adsterra High CPM Ad #2", "duration": 20, "reward": 20, "url": "https://example.com/adsterra"},
        {"id": 3, "name": "PropellerAds Popunder #3", "duration": 15, "reward": 10, "url": "https://example.com/propeller"}
    ],
    "tasks": [
        {"id": 1, "title": "Join Official RS TOKEN Channel", "members": "Official", "reward": 50, "url": "https://t.me/RSTokenOfficial"},
        {"id": 2, "title": "Join RS TOKEN Community Chat", "members": "Community", "reward": 40, "url": "https://t.me/RSTokenChat"},
        {"id": 3, "title": "Join RS VIP Signals & News", "members": "VIP", "reward": 30, "url": "https://t.me/RSTokenSignals"}
    ],
    "payoutHistory": []
}

# USER MINI APP (৫টি ট্যাব — মোবাইল ও টেলিগ্রাম WebApp ফ্রেন্ডলি, ইনস্ট্যান্ট নেভিগেশন)
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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050811; color: #f1f5f9; -webkit-tap-highlight-color: transparent; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .card-dark { background: #0c1222; border: 1px solid #1e293b; border-radius: 1.25rem; }
    .card-glow { box-shadow: 0 0 35px -5px rgba(6, 182, 212, 0.25); border-color: rgba(6, 182, 212, 0.3); }
    .coin-ring { animation: pulseGlow 2.5s infinite ease-in-out; }
    @keyframes pulseGlow { 0%, 100% { filter: drop-shadow(0 0 15px rgba(6, 182, 212, 0.4)); } 50% { filter: drop-shadow(0 0 30px rgba(6, 182, 212, 0.8)); } }
    ::-webkit-scrollbar { display: none; }
    .tab-btn { cursor: pointer; -webkit-tap-highlight-color: rgba(6, 182, 212, 0.25); touch-action: manipulation; }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between pb-28">

  <!-- TOP HEADER -->
  <header class="w-full bg-[#0a0f1d] border-b border-slate-800 sticky top-0 z-30 px-4 py-3 shadow-md">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div onclick="handleSecretAdminClick()" class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white font-black text-sm cursor-pointer active:scale-95">
          RS
        </div>
        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="text-sm font-extrabold text-white">RS TOKEN</h1>
            <span class="text-[10px] bg-cyan-500/20 text-cyan-400 font-mono px-1.5 py-0.5 rounded border border-cyan-500/30 font-bold">TON</span>
          </div>
          <p class="text-[10px] text-slate-400">Mining & Distribution</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button onclick="toggleWalletModal()" type="button" id="header-wallet-btn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold hover:bg-cyan-500/20 active:scale-95 transition-all">
          <i class="fa-solid fa-wallet"></i>
          <span id="header-wallet-text">Connect Wallet</span>
        </button>
      </div>
    </div>

    <!-- Announcement Banner -->
    <div class="mt-2.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-2 text-xs text-amber-300">
      <i class="fa-solid fa-fire text-amber-400"></i>
      <div class="truncate text-[11px]" id="notice-text">
        🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!
      </div>
    </div>

    <!-- Telemetry strip -->
    <div class="mt-2 flex items-center justify-between text-xs px-1">
      <div class="flex items-center gap-1.5 text-slate-400 font-semibold text-[11px]">
        <span class="w-2 h-2 rounded-full bg-cyan-400 inline-block animate-ping"></span>
        <span class="text-cyan-400 font-mono">TON BLOCKCHAIN</span>
        <span>·</span>
        <span class="text-slate-300">RS</span>
      </div>
      <div class="flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-emerald-400 font-mono">
        <span id="header-price-display">$ 1 RS = $0.054 USD</span>
      </div>
    </div>
  </header>

  <!-- MAIN TAB CONTENT -->
  <main class="flex-1 p-4 max-w-md mx-auto w-full space-y-4 pt-2">

    <!-- ১. মাইনিং ট্যাব -->
    <section id="tab-mining" class="space-y-4" style="display: block;">
      <!-- Balance Card -->
      <div class="card-dark card-glow p-5 text-center relative overflow-hidden">
        <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">আপনার ব্যালেন্স</p>
        <div class="flex items-center justify-center gap-2.5">
          <span class="text-3xl text-cyan-400">💎</span>
          <span class="text-4xl font-black tracking-tight text-white font-mono tabular-nums" id="balance-display">0.00</span>
          <span class="text-lg font-bold text-cyan-400 font-mono">RS</span>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-mono">
          ≈ <span class="text-emerald-400 font-semibold" id="usd-val">$0.00 USD</span> · ≈ <span class="text-sky-400 font-semibold" id="ton-val">0.000 TON</span>
        </p>
      </div>

      <!-- 3D Coin Mining Center -->
      <div class="card-dark p-6 text-center relative">
        <div class="relative w-48 h-48 mx-auto mb-3 flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border-4 border-slate-800"></div>
          <div class="absolute inset-0 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" style="animation-duration: 3s;" id="spinner-ring"></div>
          
          <div class="w-40 h-40 rounded-full bg-gradient-to-tr from-[#0b1329] to-[#152347] border-2 border-cyan-500/40 flex flex-col items-center justify-center shadow-2xl coin-ring">
            <span class="text-3xl mb-1">💎</span>
            <span class="text-sm font-black text-white tracking-wider">RS TOKEN</span>
            <span class="text-[10px] text-cyan-300 font-mono">TON Jetton</span>
          </div>
        </div>

        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-300 mb-3">
          <i class="fa-solid fa-shield-halved text-cyan-400"></i>
          <span>অটোমেটিক ক্লাউড মাইনিং সক্রিয় (ম্যানুয়াল ট্যাপ পয়েন্ট নিষ্ক্রিয়)</span>
        </div>

        <div class="flex items-center justify-between text-xs px-2 mb-3">
          <div class="flex items-center gap-1.5 text-slate-400">
            <i class="fa-solid fa-bolt text-cyan-400"></i>
            <span>মাইনিং স্পিড:</span>
            <span class="text-white font-mono font-bold" id="speed-text">+60 RS / hr</span>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" id="status-pill">
            <i class="fa-solid fa-circle-notch fa-spin mr-1"></i> মাইনিং সক্রিয়
          </span>
        </div>

        <button onclick="toggleMining()" type="button" id="mining-btn" class="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 active:scale-95 transition-all flex items-center justify-center gap-2">
          <i class="fa-solid fa-pause" id="mining-btn-icon"></i>
          <span id="mining-btn-label">মাইনিং পজ করুন</span>
        </button>
      </div>

      <!-- Real Live Community Stats -->
      <div class="grid grid-cols-2 gap-2.5">
        <div class="card-dark p-4">
          <div class="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
            <i class="fa-solid fa-users text-blue-400"></i>
            <span>মোট জয়েন করা ইউজার</span>
          </div>
          <div class="flex items-baseline gap-1">
            <span class="text-xl font-black text-white font-mono" id="stat-joined">0</span>
            <span class="text-xs text-blue-400 font-bold">জন</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-0.5">রিয়েল মেম্বার জয়েন করেছে</p>
        </div>

        <div class="card-dark p-4">
          <div class="flex items-center justify-between text-xs mb-1">
            <div class="flex items-center gap-1.5 text-slate-400">
              <i class="fa-solid fa-tower-broadcast text-emerald-400 animate-pulse"></i>
              <span>লাইভ অনলাইনে সক্রিয়</span>
            </div>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">LIVE</span>
          </div>
          <p class="text-xl font-black text-emerald-400 font-mono" id="stat-online">1</p>
          <p class="text-[10px] text-slate-500 mt-0.5">এখন লাইভ মাইনিং করছে</p>
        </div>
      </div>

      <!-- Real Leaderboard -->
      <div class="card-dark p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <i class="fa-solid fa-trophy text-amber-400"></i>
            <h3 class="text-xs font-bold text-white uppercase">শীর্ষ মাইনার্স লিডারবোর্ড</h3>
          </div>
          <span class="text-[10px] text-slate-500 font-mono">REAL MINERS</span>
        </div>

        <div class="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-between text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-[11px]" id="my-rank">#1</span>
            <div>
              <p class="font-bold text-white" id="my-username">আপনার প্রোফাইল (You)</p>
              <p class="text-[10px] text-slate-400 font-sans">রিয়েল মাইনার</p>
            </div>
          </div>
          <div class="text-right">
            <p class="font-bold text-cyan-300" id="user-rank-coins">0.00 RS</p>
            <p class="text-[10px] text-slate-400" id="user-rank-usd">≈ $0.00</p>
          </div>
        </div>

        <div class="space-y-2 text-xs font-mono" id="leaderboard-list">
          <div class="p-3 rounded-xl bg-slate-900 text-center text-slate-400 text-xs">
            নতুন মেম্বাররা বটে জয়েন করে মাইনিং শুরু করলে তাদের নাম ও পয়েন্ট এখানে লাইভ চলে আসবে!
          </div>
        </div>
      </div>
    </section>

    <!-- ২. বিজ্ঞাপন দেখে টোকেন আয় -->
    <section id="tab-ads" class="space-y-4" style="display: none;">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-cyan-500/20">
          <i class="fa-solid fa-tv"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">বিজ্ঞাপন দেখে টোকেন আয়</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">সরাসরি অ্যাড লিংকে ক্লিক করে নির্দিষ্ট সময় দেখুন এবং ইনস্ট্যান্ট RS টোকেন রিওয়ার্ড নিন!</p>
      </div>

      <div class="space-y-3" id="ads-list">
        <div class="card-dark p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-cyan-400 text-xs">AD</div>
            <div>
              <span class="text-xs font-bold text-white">Monetag SmartLink</span>
              <p class="text-xs text-emerald-400 font-mono font-bold mt-0.5">⏱️ 15s · +15 RS TOKEN</p>
            </div>
          </div>
          <button onclick="playAd(1, 15, 15, 'https://example.com/monetag')" type="button" id="ad-btn-1" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-black text-xs active:scale-95">অ্যাড দেখুন ↗</button>
        </div>
        <div class="card-dark p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-cyan-400 text-xs">AD</div>
            <div>
              <span class="text-xs font-bold text-white">Adsterra High CPM Ad #2</span>
              <p class="text-xs text-emerald-400 font-mono font-bold mt-0.5">⏱️ 20s · +20 RS TOKEN</p>
            </div>
          </div>
          <button onclick="playAd(2, 20, 20, 'https://example.com/adsterra')" type="button" id="ad-btn-2" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-black text-xs active:scale-95">অ্যাড দেখুন ↗</button>
        </div>
        <div class="card-dark p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-cyan-400 text-xs">AD</div>
            <div>
              <span class="text-xs font-bold text-white">PropellerAds Popunder #3</span>
              <p class="text-xs text-emerald-400 font-mono font-bold mt-0.5">⏱️ 15s · +10 RS TOKEN</p>
            </div>
          </div>
          <button onclick="playAd(3, 15, 10, 'https://example.com/propeller')" type="button" id="ad-btn-3" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-black text-xs active:scale-95">অ্যাড দেখুন ↗</button>
        </div>
      </div>
    </section>

    <!-- ৩. টেলিগ্রাম চ্যানেল ও গ্রুপ টাস্ক -->
    <section id="tab-tasks" class="space-y-4" style="display: none;">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-blue-500/20">
          <i class="fa-solid fa-paper-plane"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">টেলিগ্রাম চ্যানেল ও গ্রুপ টাস্ক</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">আমাদের চ্যানেল এবং গ্রুপগুলোতে জয়েন করুন এবং সাথে সাথে RS টোকেন আনলক করুন!</p>
      </div>

      <div class="space-y-3" id="tasks-list">
        <div class="card-dark p-4 space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center text-lg"><i class="fa-brands fa-telegram"></i></div>
            <div>
              <h4 class="text-xs font-bold text-white">Join Official RS TOKEN Channel</h4>
              <p class="text-[11px] text-slate-400 mt-0.5"><span class="text-emerald-400 font-bold font-mono">+50 RS</span></p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="window.open('https://t.me/RSTokenOfficial', '_blank')" type="button" class="py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold">জয়েন করুন ↗</button>
            <button onclick="claimTaskReward(1, 50)" type="button" id="task-btn-1" class="py-2 rounded-xl bg-cyan-500 text-slate-950 font-black text-xs">যাচাই করুন</button>
          </div>
        </div>
        <div class="card-dark p-4 space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center text-lg"><i class="fa-brands fa-telegram"></i></div>
            <div>
              <h4 class="text-xs font-bold text-white">Join RS TOKEN Community Chat</h4>
              <p class="text-[11px] text-slate-400 mt-0.5"><span class="text-emerald-400 font-bold font-mono">+40 RS</span></p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="window.open('https://t.me/RSTokenChat', '_blank')" type="button" class="py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold">জয়েন করুন ↗</button>
            <button onclick="claimTaskReward(2, 40)" type="button" id="task-btn-2" class="py-2 rounded-xl bg-cyan-500 text-slate-950 font-black text-xs">যাচাই করুন</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ৪. রেফারেল প্রোগ্রাম -->
    <section id="tab-referral" class="space-y-4" style="display: none;">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-emerald-500/20">
          <i class="fa-solid fa-users"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">রেফারেল প্রোগ্রাম</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">বন্ধুদের ইনভাইট করুন এবং প্রতিটি ভেরিফাইড রেফারে পান <span class="text-emerald-400 font-bold" id="ref-rew-text">+25 RS</span> এবং তাদের মোট মাইনিংয়ের <span class="text-cyan-400 font-bold" id="ref-comm-text">10%</span> কমিশন লাইফটাইম!</p>
      </div>

      <div class="card-dark p-5 space-y-3">
        <p class="text-xs font-bold text-slate-300">আপনার নিজস্ব রেফারেল লিংক:</p>
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300 break-all select-all" id="ref-url">
          https://t.me/rs_token_mining_bot?start=ref
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button onclick="copyRefLink()" type="button" class="py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs shadow-lg active:scale-95 flex items-center justify-center gap-1.5">
            <i class="fa-solid fa-copy"></i><span>লিংক কপি</span>
          </button>
          <button onclick="shareTelegramRef()" type="button" class="py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg active:scale-95 flex items-center justify-center gap-1.5">
            <i class="fa-solid fa-share-nodes"></i><span>শেয়ার করুন</span>
          </button>
        </div>
      </div>
    </section>

    <!-- ৫. TON ওয়ালেট ও উইথড্র (রিয়েল Tonkeeper ইন্টিগ্রেশন) -->
    <section id="tab-wallet" class="space-y-4" style="display: none;">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-cyan-500/20">
          <i class="fa-solid fa-wallet"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">TON ওয়ালেট ও উইথড্র</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto mb-4">আপনার Tonkeeper ওয়ালেট কানেক্ট করে সরাসরি আপনার ওয়ালেটে RS টোকেন উইথড্র করুন।</p>
        <button onclick="toggleWalletModal()" type="button" id="connect-wallet-main-btn" class="w-full py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs shadow-lg active:scale-95">
          Tonkeeper ওয়ালেট কানেক্ট করুন 💎
        </button>
      </div>

      <!-- Smart Contract -->
      <div class="card-dark p-4 space-y-2">
        <div class="flex items-center justify-between text-xs font-bold text-slate-300">
          <span>RS TOKEN Smart Contract (TON Jetton)</span>
          <button onclick="navigator.clipboard.writeText(document.getElementById('contract-addr').innerText); alert('কপি হয়েছে!');" type="button"><i class="fa-solid fa-copy"></i></button>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-300 truncate" id="contract-addr">
          EQBv_RSTOKEN_Official_Jetton_MasterPool_99
        </div>
      </div>

      <!-- $1 Hold Lock Section -->
      <div class="card-dark p-5 space-y-3 border border-amber-500/30">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-lock text-amber-400"></i> উইথড্র অপশন লক করা আছে
          </h4>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">LOCKED</span>
        </div>
        <p class="text-xs text-slate-300">বট স্প্যাম প্রতিরোধ ও লিকুইডিটি যাচাইকরণের জন্য ব্যবহারকারীকে $১ ডলারের RS TOKEN কিনে ২৪ ঘণ্টার জন্য হোল্ড করতে হবে। ২৪ ঘণ্টা পর স্বয়ংক্রিয়ভাবে উইথড্র আনলক হয়ে যাবে।</p>
        <button onclick="openTonkeeperBuy()" type="button" class="w-full py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs shadow-lg flex items-center justify-center gap-2 active:scale-95">
          <i class="fa-solid fa-shield"></i>
          <span>$১ ডলারের RS টোকেন কিনুন ও আনলক করুন (Open Tonkeeper)</span>
        </button>
      </div>
    </section>

  </main>

  <!-- ৫টি নির্দিষ্ট বটম বাটন (সর্বোচ্চ z-index ও সরাসরি টাচ রেসপন্সিভ) -->
  <nav class="fixed bottom-0 inset-x-0 bg-[#0a0f1d] border-t border-slate-800 px-2 py-2 flex items-center justify-around max-w-md mx-auto" style="z-index: 9999;">
    <button onclick="switchTab('mining')" type="button" id="nav-mining" class="tab-btn flex flex-col items-center gap-1 text-cyan-400 font-bold min-w-[56px] py-1 px-2 rounded-xl bg-cyan-500/10 transition-all">
      <i class="fa-solid fa-cube text-base"></i>
      <span class="text-[10px]">১. মাইনিং</span>
    </button>
    <button onclick="switchTab('ads')" type="button" id="nav-ads" class="tab-btn flex flex-col items-center gap-1 text-slate-400 font-medium min-w-[56px] py-1 px-2 rounded-xl transition-all">
      <i class="fa-solid fa-tv text-base"></i>
      <span class="text-[10px]">২. অ্যাডস</span>
    </button>
    <button onclick="switchTab('tasks')" type="button" id="nav-tasks" class="tab-btn flex flex-col items-center gap-1 text-slate-400 font-medium min-w-[56px] py-1 px-2 rounded-xl transition-all">
      <i class="fa-solid fa-list-check text-base"></i>
      <span class="text-[10px]">৩. টাস্ক</span>
    </button>
    <button onclick="switchTab('referral')" type="button" id="nav-referral" class="tab-btn flex flex-col items-center gap-1 text-slate-400 font-medium min-w-[56px] py-1 px-2 rounded-xl transition-all">
      <i class="fa-solid fa-users text-base"></i>
      <span class="text-[10px]">৪. রেফারেল</span>
    </button>
    <button onclick="switchTab('wallet')" type="button" id="nav-wallet" class="tab-btn flex flex-col items-center gap-1 text-slate-400 font-medium min-w-[56px] py-1 px-2 rounded-xl transition-all">
      <i class="fa-solid fa-wallet text-base"></i>
      <span class="text-[10px]">৫. ওয়ালেট</span>
    </button>
  </nav>

  <!-- REAL TONKEEPER WALLET CONNECT MODAL -->
  <div id="wallet-modal" style="display: none; z-index: 10000;" class="fixed inset-0 bg-black/85 backdrop-blur-sm flex items-end sm:items-center justify-center p-4">
    <div class="w-full max-w-sm rounded-2xl bg-[#0c1222] border border-slate-800 p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <i class="fa-solid fa-wallet text-cyan-400"></i> Tonkeeper ওয়ালেট কানেক্ট
        </h3>
        <button onclick="closeWalletModal()" type="button" class="text-slate-400 hover:text-white p-1 text-base"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <!-- Step 1: Open Real Tonkeeper App Button -->
      <a href="https://app.tonkeeper.com" target="_blank" rel="noopener noreferrer" class="w-full p-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-between transition-all active:scale-95">
        <div class="flex items-center gap-2.5">
          <span class="w-8 h-8 rounded-lg bg-white/20 text-white flex items-center justify-center font-black text-xs">TK</span>
          <div class="text-left">
            <p class="text-xs font-bold">Tonkeeper অ্যাপ খুলুন ↗</p>
            <p class="text-[10px] text-blue-200">সরাসরি Tonkeeper অ্যাপে নিয়ে যাবে</p>
          </div>
        </div>
        <i class="fa-solid fa-arrow-up-right-from-square text-xs"></i>
      </a>

      <!-- Step 2: Paste Real Address -->
      <div class="space-y-2 pt-2 border-t border-slate-800">
        <label class="text-[11px] font-bold text-slate-300">আপনার আসল Tonkeeper ওয়ালেট অ্যাড্রেস দিন:</label>
        <div class="relative">
          <input type="text" id="real-ton-input" placeholder="EQ... বা UQ... (Tonkeeper)" class="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono focus:border-cyan-400 focus:outline-none pr-16">
          <button onclick="pasteFromClipboard()" type="button" class="absolute right-1.5 top-1.5 px-2.5 py-1 rounded-lg bg-slate-800 text-cyan-400 font-bold text-[10px]">
            পেস্ট
          </button>
        </div>
        <p class="text-[10px] text-slate-500">Tonkeeper অ্যাপে গিয়ে Receive চাপলে আপনার অ্যাড্রেস পাবেন, সেটি এখানে বসিয়ে দিন।</p>
      </div>

      <button onclick="saveRealWalletAddress()" type="button" class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs shadow-lg active:scale-95">
        ওয়ালেট কানেক্ট সম্পন্ন করুন ✅
      </button>
    </div>
  </div>

  <script>
    // Safe storage helper prevents crashes on Android WebViews with storage restrictions
    const SafeStorage = {
      get: function(key, fallback) {
        try {
          const val = localStorage.getItem(key);
          return val !== null ? val : fallback;
        } catch (e) {
          return fallback;
        }
      },
      set: function(key, val) {
        try {
          localStorage.setItem(key, val);
        } catch (e) {}
      }
    };

    const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    try {
      if (tg) { tg.ready(); tg.expand(); }
    } catch(e) {}

    const tgUser = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user : null;
    const myUid = tgUser ? String(tgUser.id) : ('miner_' + Math.floor(Math.random() * 89999 + 10000));
    const myName = tgUser ? (tgUser.first_name + (tgUser.last_name ? ' ' + tgUser.last_name : '')) : 'আপনার প্রোফাইল (You)';

    const userEl = document.getElementById('my-username');
    if (userEl) userEl.innerText = myName;

    const refEl = document.getElementById('ref-url');
    if (refEl) refEl.innerText = 'https://t.me/rs_token_mining_bot?start=' + myUid;

    let balance = parseFloat(SafeStorage.get('rs_balance_' + myUid, '0.00')) || 0.00;
    let isMining = true;
    let connectedWallet = SafeStorage.get('rs_real_wallet_' + myUid, null);

    if (connectedWallet) {
      const hw = document.getElementById('header-wallet-text');
      if (hw) hw.innerText = connectedWallet.slice(0, 4) + '...' + connectedWallet.slice(-4);
      const cw = document.getElementById('connect-wallet-main-btn');
      if (cw) cw.innerText = connectedWallet + ' (কানেক্টেড)';
      const ri = document.getElementById('real-ton-input');
      if (ri) ri.value = connectedWallet;
    }

    // Tab switcher with instant responsive DOM manipulation
    window.switchTab = function(t) {
      const tabs = ['mining', 'ads', 'tasks', 'referral', 'wallet'];
      for (let i = 0; i < tabs.length; i++) {
        const id = tabs[i];
        const tabEl = document.getElementById('tab-' + id);
        const navEl = document.getElementById('nav-' + id);
        if (tabEl) {
          if (id === t) {
            tabEl.style.display = 'block';
          } else {
            tabEl.style.display = 'none';
          }
        }
        if (navEl) {
          if (id === t) {
            navEl.className = 'tab-btn flex flex-col items-center gap-1 text-cyan-400 font-bold min-w-[56px] py-1 px-2 rounded-xl bg-cyan-500/10 transition-all';
          } else {
            navEl.className = 'tab-btn flex flex-col items-center gap-1 text-slate-400 font-medium min-w-[56px] py-1 px-2 rounded-xl transition-all';
          }
        }
      }
      try {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch(e) {}
    };

    window.toggleMining = function() {
      isMining = !isMining;
      const lbl = document.getElementById('mining-btn-label');
      const ico = document.getElementById('mining-btn-icon');
      const st = document.getElementById('status-pill');
      if (lbl) lbl.innerText = isMining ? 'মাইনিং পজ করুন' : 'মাইনিং শুরু করুন 🚀';
      if (ico) ico.className = isMining ? 'fa-solid fa-pause' : 'fa-solid fa-play';
      if (st) st.innerText = isMining ? 'মাইনিং সক্রিয়' : 'মাইনিং বন্ধ রয়েছে';
    };

    window.toggleWalletModal = function() {
      const m = document.getElementById('wallet-modal');
      if (m) {
        m.style.display = (m.style.display === 'none' || m.style.display === '') ? 'flex' : 'none';
      }
    };

    window.closeWalletModal = function() {
      const m = document.getElementById('wallet-modal');
      if (m) m.style.display = 'none';
    };

    window.pasteFromClipboard = async function() {
      try {
        const text = await navigator.clipboard.readText();
        if (text) document.getElementById('real-ton-input').value = text.trim();
      } catch (e) {
        alert('ক্লিপবোর্ড থেকে পেস্ট করতে ব্যর্থ হয়েছে। অনুগ্রহ করে হাতে লিখুন বা পেস্ট করুন।');
      }
    };

    window.saveRealWalletAddress = function() {
      const input = document.getElementById('real-ton-input');
      const addr = input ? input.value.trim() : '';
      if (!addr) {
        alert('অনুগ্রহ করে আপনার Tonkeeper ওয়ালেট অ্যাড্রেস দিন!');
        return;
      }
      if (!addr.startsWith('EQ') && !addr.startsWith('UQ')) {
        alert('সতর্কতা: TON ওয়ালেট অ্যাড্রেস সাধারণত EQ বা UQ দিয়ে শুরু হয়। আপনার অ্যাড্রেসটি চেক করুন।');
      }
      connectedWallet = addr;
      SafeStorage.set('rs_real_wallet_' + myUid, connectedWallet);
      const hw = document.getElementById('header-wallet-text');
      if (hw) hw.innerText = connectedWallet.slice(0, 4) + '...' + connectedWallet.slice(-4);
      const cw = document.getElementById('connect-wallet-main-btn');
      if (cw) cw.innerText = connectedWallet + ' (কানেক্টেড)';
      closeWalletModal();
      syncUserWithServer();
      alert('✅ আপনার আসল Tonkeeper ওয়ালেট সফলভাবে কানেক্ট করা হয়েছে:\n' + connectedWallet);
    };

    window.playAd = function(id, sec, rew, url) {
      if (url && url !== '#') {
        try { window.open(url, '_blank'); } catch(e) {}
      }
      const b = document.getElementById('ad-btn-' + id);
      if (b) {
        b.disabled = true;
        let r = sec;
        const itv = setInterval(() => {
          r--;
          if (r > 0) {
            b.innerText = r + 's';
          } else {
            clearInterval(itv);
            balance += rew;
            updateBalance();
            b.innerText = 'দেখা হয়েছে ✅';
            syncUserWithServer();
            alert('🎉 +' + rew + ' RS ব্যালেন্সে যোগ হয়েছে!');
          }
        }, 1000);
      }
    };

    window.claimTaskReward = function(id, rew) {
      balance += rew;
      updateBalance();
      const b = document.getElementById('task-btn-' + id);
      if (b) {
        b.innerText = 'যাচাইকৃত ✅';
        b.disabled = true;
      }
      syncUserWithServer();
      alert('🎉 +' + rew + ' RS ব্যালেন্সে যোগ হয়েছে!');
    };

    window.openTonkeeperBuy = function() {
      try { window.open('https://app.tonkeeper.com', '_blank'); } catch(e) {}
      alert('Tonkeeper ওপেন হচ্ছে... $১ ডলারের RS টোকেন কিনে ২৪ ঘণ্টা হোল্ড রাখুন।');
    };

    window.copyRefLink = function() {
      const el = document.getElementById('ref-url');
      if (el) {
        navigator.clipboard.writeText(el.innerText);
        alert('✅ রেফারেল লিংক কপি করা হয়েছে!');
      }
    };

    window.shareTelegramRef = function() {
      const el = document.getElementById('ref-url');
      const url = el ? el.innerText : '';
      window.open('https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent('🔥 RS TOKEN ফ্রি ক্লাউড মাইনিং-এ জয়েন করুন এবং ইনকাম করুন!'));
    };

    let secretClicks = 0;
    window.handleSecretAdminClick = function() {
      secretClicks++;
      if (secretClicks >= 4) {
        secretClicks = 0;
        window.location.href = '/admin';
      }
    };

    function updateBalance() {
      const bd = document.getElementById('balance-display');
      if (bd) bd.innerText = balance.toFixed(2);
      const urc = document.getElementById('user-rank-coins');
      if (urc) urc.innerText = balance.toFixed(2) + ' RS';
      const uv = document.getElementById('usd-val');
      if (uv) uv.innerText = '$' + (balance * 0.054).toFixed(2) + ' USD';
      const uru = document.getElementById('user-rank-usd');
      if (uru) uru.innerText = '≈ $' + (balance * 0.054).toFixed(2);
      const tv = document.getElementById('ton-val');
      if (tv) tv.innerText = (balance * 0.0098).toFixed(3) + ' TON';
      SafeStorage.set('rs_balance_' + myUid, balance.toString());
    }
    updateBalance();

    // Live mining counter
    setInterval(() => {
      if (isMining) {
        balance += 0.0166;
        updateBalance();
      }
    }, 1000);

    // Sync with server
    function syncUserWithServer() {
      fetch('/api/user/sync', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          uid: myUid,
          name: myName,
          coins: balance,
          wallet: connectedWallet
        })
      }).then(r => r.json()).then(data => {
        if (!data) return;
        const sj = document.getElementById('stat-joined');
        if (sj && data.joinedCount !== undefined) sj.innerText = data.joinedCount;
        const so = document.getElementById('stat-online');
        if (so && data.onlineCount !== undefined) so.innerText = data.onlineCount;
        const nt = document.getElementById('notice-text');
        if (nt && data.notice) nt.innerText = data.notice;
        const hp = document.getElementById('header-price-display');
        if (hp && data.tokenPriceUSD) hp.innerText = '$ 1 RS = $' + data.tokenPriceUSD + ' USD';
        const st = document.getElementById('speed-text');
        if (st && data.miningSpeed) st.innerText = '+' + data.miningSpeed + ' RS / hr';
        const ca = document.getElementById('contract-addr');
        if (ca && data.contractAddress) ca.innerText = data.contractAddress;

        if (data.leaderboard && data.leaderboard.length > 0) {
          const c = document.getElementById('leaderboard-list');
          if (c) {
            c.innerHTML = data.leaderboard.map((m, idx) => `
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-lg ${idx === 0 ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-300'} flex items-center justify-center font-bold text-xs">${idx + 1}</span>
                  <div>
                    <p class="font-bold text-white">${m.name}</p>
                    <p class="text-[10px] text-slate-400">${m.username || 'রিয়েল মাইনার'}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-bold text-emerald-400">${parseFloat(m.coins || 0).toFixed(2)} RS</p>
                  <p class="text-[10px] text-slate-400">≈ $${((m.coins || 0) * 0.054).toFixed(2)}</p>
                </div>
              </div>
            `).join('');
          }
        }
      }).catch(e => console.log('Sync error:', e));
    }
    syncUserWithServer();
    setInterval(syncUserWithServer, 10000);

    // Attach touch event listeners for immediate mobile reaction
    document.addEventListener('DOMContentLoaded', () => {
      ['mining', 'ads', 'tasks', 'referral', 'wallet'].forEach(tabName => {
        const btn = document.getElementById('nav-' + tabName);
        if (btn) {
          btn.addEventListener('click', () => switchTab(tabName));
          btn.addEventListener('touchend', (e) => {
            e.preventDefault();
            switchTab(tabName);
          });
        }
      });
    });
  </script>
</body>
</html>
"""

# SEPARATE DEDICATED ADMIN CONTROL PANEL (হুবহু স্ক্রিনশট ১৩ থেকে ২০)
ADMIN_HTML = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RS TOKEN এডমিন কন্ট্রোল প্যানেল</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #060913; color: #f1f5f9; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .card-dark { background: #0c1222; border: 1px solid #1e293b; border-radius: 1.25rem; }
  </style>
</head>
<body class="min-h-screen p-4 sm:p-6 max-w-2xl mx-auto space-y-5 pb-24 select-none">

  <!-- Admin Header -->
  <div class="card-dark p-5 flex items-center justify-between border-cyan-500/30">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-2xl font-bold border border-cyan-500/20">
        <i class="fa-solid fa-sliders"></i>
      </div>
      <div>
        <h1 class="text-base font-black text-white">RS TOKEN এডমিন কন্ট্রোল প্যানেল</h1>
        <p class="text-xs text-slate-400">মাইনিং স্পিড, টোকেনের ভ্যালু, অ্যাড নেটওয়ার্ক লিংক, চ্যানেল টাস্ক এবং উইথড্র রুলস কন্ট্রোল করুন</p>
      </div>
    </div>
    <a href="/" class="px-3.5 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold hover:bg-slate-700 flex items-center gap-1.5">
      <i class="fa-solid fa-arrow-left"></i> বটে ফিরে যান
    </a>
  </div>

  <!-- Save All Changes Button -->
  <button onclick="saveAllSettings()" class="w-full py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black text-sm shadow-xl flex items-center justify-center gap-2 active:scale-98 transition-all">
    <i class="fa-solid fa-floppy-disk"></i>
    <span>পরিবর্তনগুলো সেভ করুন</span>
  </button>

  <!-- ১. ইউজার ও অনলাইন অ্যানালিটিক্স ম্যানেজার (Screen 13 & 15) -->
  <div class="card-dark p-5 space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-bold text-white flex items-center gap-2">
        <i class="fa-solid fa-users text-cyan-400"></i>
        <span>👥 ইউজার ও অনলাইন অ্যানালিটিক্স ম্যানেজার</span>
      </h2>
      <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-mono">LIVE TELEMETRY</span>
    </div>
    <p class="text-xs text-slate-400 leading-relaxed">টেলিগ্রাম বটে মোট কতজন ইউজার জয়েন করেছে এবং বর্তমানে কতজন সক্রিয়ভাবে অনলাইনে মাইনিং করছে তা এখান থেকে সরাসরি পর্যবেক্ষণ ও পরিচালনা করুন।</p>

    <!-- Total Registered -->
    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <div class="flex justify-between items-center text-xs">
        <span class="text-slate-400 font-bold uppercase text-[11px]">মোট রেজিস্টার্ড ইউজার সংখ্যা (Base)</span>
        <span class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold text-[10px]">Registered</span>
      </div>
      <div class="flex items-center justify-between">
        <input type="number" id="input-joined" value="0" class="bg-transparent text-2xl font-black text-white font-mono w-40 focus:outline-none">
        <span class="text-xs text-slate-400">জন ইউজার (রিয়েল: <span id="real-users-count" class="text-cyan-400 font-bold">০</span>)</span>
      </div>
      <div class="flex gap-2 pt-1">
        <button onclick="addJoined(0)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 font-bold">০ রিসেট</button>
        <button onclick="addJoined(100)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 font-bold">+100</button>
        <button onclick="addJoined(500)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 font-bold">+500</button>
        <button onclick="addJoined(1000)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 font-bold">+1,000</button>
      </div>
    </div>

    <!-- Live Online -->
    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <div class="flex justify-between items-center text-xs">
        <span class="text-slate-400 font-bold uppercase text-[11px]">লাইভ অনলাইন ইউজার সংখ্যা (Base)</span>
        <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">Active Online</span>
      </div>
      <div class="flex items-center justify-between">
        <input type="number" id="input-online" value="1" class="bg-transparent text-2xl font-black text-emerald-400 font-mono w-40 focus:outline-none">
        <span class="text-xs text-slate-400">জন অনলাইন</span>
      </div>
      <div class="flex gap-2 pt-1">
        <button onclick="setOnline(1)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-emerald-300 font-bold">১ জন (রিয়েল)</button>
        <button onclick="addOnline(25)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-emerald-300 font-bold">+25</button>
        <button onclick="addOnline(50)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-emerald-300 font-bold">+50</button>
        <button onclick="addOnline(100)" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-emerald-300 font-bold">+100</button>
      </div>
    </div>
  </div>

  <!-- ২. শীর্ষ লিডারবোর্ড প্লেয়ারস কন্ট্রোল (Screen 14 & 15) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-trophy text-amber-400"></i>
        <h2 class="text-sm font-bold text-white">🏆 শীর্ষ লিডারবোর্ড প্লেয়ারস কন্ট্রোল</h2>
      </div>
      <button onclick="addLeaderboardPlayer()" class="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs flex items-center gap-1.5">
        <i class="fa-solid fa-plus"></i>
        <span>নতুন প্লেয়ার যোগ করুন</span>
      </button>
    </div>
    <div class="space-y-2 text-xs font-mono" id="admin-leaderboard-container">
      <!-- Players rendered dynamically -->
    </div>
  </div>

  <!-- ৩. টেলিগ্রাম বট ব্রডকাস্ট নোটিশ ম্যানেজার (Screen 17) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-bullhorn text-amber-400"></i>
        <h2 class="text-sm font-bold text-white">টেলিগ্রাম বট ব্রডকাস্ট নোটিশ ম্যানেজার</h2>
      </div>
      <button onclick="promptNotice()" class="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs flex items-center gap-1.5">
        <i class="fa-solid fa-plus"></i>
        <span>নতুন ব্রডকাস্ট নোটিশ পাঠান</span>
      </button>
    </div>
    <p class="text-xs text-slate-400">টেলিগ্রাম বটে যুক্ত সকল ব্যবহারকারীর কাছে নোটিশ, আপডেট বা এয়ারড্রপের ঘোষণা সরাসরি ব্রডকাস্ট মেসেজ হিসেবে পাঠান।</p>

    <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <div class="flex items-center justify-between">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400">AIRDROP</span>
        <button onclick="document.getElementById('admin-notice-input').value=''" class="text-slate-500 hover:text-rose-400"><i class="fa-solid fa-trash"></i></button>
      </div>
      <textarea id="admin-notice-input" rows="2" class="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-amber-400 font-medium">🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই TON ব্লকচেইনে শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!</textarea>
    </div>
  </div>

  <!-- ৪. আপনার নিজস্ব TON ব্লকচেইন টোকেন ও DEX কন্ট্রাক্ট সেটিংস (Screen 17) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-arrow-right-arrow-left text-cyan-400"></i>
      <h2 class="text-sm font-bold text-white">↔️ আপনার নিজস্ব TON ব্লকচেইন টোকেন ও DEX কন্ট্রাক্ট সেটিংস</h2>
    </div>

    <div class="space-y-3 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">RS TOKEN Jetton Contract Address (on TON Blockchain):</label>
        <input type="text" id="input-contract" value="EQBv_RSTOKEN_Official_Jetton_MasterPool_99" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-cyan-300 font-mono text-xs">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">STON.fi or DeDust DEX Buy/Swap URL:</label>
        <input type="text" id="input-dex-url" value="https://ston.fi/swap?chartVisible=true" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-cyan-300 font-mono text-xs">
      </div>
    </div>
  </div>

  <!-- ৫. TOKEN & MINING CONTROLS (Screen 14 & 18) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-chart-line text-cyan-400"></i>
      <h2 class="text-sm font-bold text-white uppercase tracking-wider">📈 TOKEN & MINING CONTROLS</h2>
    </div>

    <div class="space-y-3 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মাইনিং স্পিড (RS টোকেন / ঘণ্টা):</label>
        <input type="number" id="input-speed" value="60" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] font-bold text-slate-400 uppercase">টোকেনের লাইভ দাম ($USD):</label>
          <input type="number" step="0.001" id="input-price-usd" value="0.054" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
        </div>
        <div>
          <label class="text-[11px] font-bold text-slate-400 uppercase">টোকেনের লাইভ দাম (TON):</label>
          <input type="number" step="0.0001" id="input-price-ton" value="0.0098" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
        </div>
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">Live Chart Trend Direction:</label>
        <select id="input-trend" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-bold">
          <option value="BULLISH">BULLISH ↗ (Upward momentum)</option>
          <option value="BEARISH">BEARISH ↘ (Downward correction)</option>
        </select>
      </div>
    </div>
  </div>

  <!-- ৬. INSTANT AUTO-PAYMENT & WITHDRAW RULES (Screen 14, 16 & 18) -->
  <div class="card-dark p-5 space-y-4 border-amber-500/20">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-bolt text-amber-400"></i>
      <h2 class="text-sm font-bold text-white uppercase tracking-wider">⚡ INSTANT AUTO-PAYMENT & WITHDRAW RULES</h2>
    </div>

    <div class="space-y-3 text-xs">
      <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="font-bold text-white">ইনস্ট্যান্ট অটো-পেমেন্ট সিস্টেম চালু রাখুন</span>
        <input type="checkbox" id="check-autopay" checked class="w-5 h-5 accent-cyan-500">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">TON Payout Master Hot Wallet:</label>
        <input type="text" id="input-hotwallet" value="EQD_RS_AutoPayout_MasterPool_TON99" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-cyan-300 font-mono text-xs">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মিনিমাম উইথড্র লিমিট (RS):</label>
        <input type="number" id="input-min-withdraw" value="100" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
      <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="font-bold text-white">২৪ ঘণ্টার $১ ডলার হোল্ড রুল সক্রিয় রাখুন</span>
        <input type="checkbox" id="check-holdrule" checked class="w-5 h-5 accent-cyan-500">
      </div>
    </div>
  </div>

  <!-- ৭. REFERRAL PROGRAM CONFIGURATION (Screen 16 & 19) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center gap-2">
      <i class="fa-solid fa-dollar-sign text-emerald-400"></i>
      <h2 class="text-sm font-bold text-white uppercase tracking-wider">💲 REFERRAL PROGRAM CONFIGURATION</h2>
    </div>
    <div class="grid grid-cols-2 gap-3 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">প্রতি রেফারে রিওয়ার্ড (RS):</label>
        <input type="number" id="input-ref-reward" value="25" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">রেফারেল মাইনিং কমিশন (%):</label>
        <input type="number" id="input-ref-comm" value="10" class="w-full mt-1 p-3 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
    </div>
  </div>

  <!-- ৮. অ্যাড নেটওয়ার্ক ও ডাইরেক্ট লিংক ম্যানেজার (Screen 16 & 19) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-tv text-cyan-400"></i>
        <h2 class="text-sm font-bold text-white">📺 অ্যাড নেটওয়ার্ক ও ডাইরেক্ট লিংক ম্যানেজার</h2>
      </div>
      <button onclick="addAdPrompt()" class="px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-black text-xs flex items-center gap-1.5">
        <i class="fa-solid fa-plus"></i>
        <span>নতুন অ্যাড লিংক যোগ করুন</span>
      </button>
    </div>
    <div class="space-y-2 text-xs" id="admin-ads-container">
      <!-- Ads rendered dynamically -->
    </div>
  </div>

  <!-- ৯. টেলিগ্রাম চ্যানেল ও গ্রুপ ম্যানেজার (Screen 20) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-paper-plane text-blue-400"></i>
        <h2 class="text-sm font-bold text-white">✈️ টেলিগ্রাম চ্যানেল ও গ্রুপ ম্যানেজার</h2>
      </div>
      <button onclick="addTaskPrompt()" class="px-3 py-1.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-black text-xs flex items-center gap-1.5">
        <i class="fa-solid fa-plus"></i>
        <span>নতুন চ্যানেল বা গ্রুপ যোগ করুন</span>
      </button>
    </div>
    <div class="space-y-2 text-xs" id="admin-tasks-container">
      <!-- Tasks rendered dynamically -->
    </div>
  </div>

  <!-- ১০. অটো-পেমেন্ট হিস্ট্রি (Instant TON Transfers) (Screen 20) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-wallet text-emerald-400"></i>
        <h2 class="text-sm font-bold text-white">💳 অটো-পেমেন্ট হিস্ট্রি (Instant TON Transfers)</h2>
      </div>
      <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">LIVE ON-CHAIN</span>
    </div>
    <div class="p-4 rounded-xl bg-slate-900 text-center text-slate-400 text-xs">
      এখনও কোনো অটো-পেমেন্ট ট্রানজ্যাকশন হয়নি।
    </div>
  </div>

  <script>
    let localLeaderboard = [];
    let localAds = [];
    let localTasks = [];

    fetch('/api/settings').then(r => r.json()).then(s => {
      document.getElementById('admin-notice-input').value = s.notice || '';
      document.getElementById('input-joined').value = s.baseJoined || 0;
      document.getElementById('input-online').value = s.baseOnline || 1;
      document.getElementById('input-speed').value = s.miningSpeed || 60;
      document.getElementById('input-price-usd').value = s.tokenPriceUSD || 0.054;
      document.getElementById('input-price-ton').value = s.tokenPriceTON || 0.0098;
      document.getElementById('input-contract').value = s.contractAddress || '';
      document.getElementById('input-dex-url').value = s.dexSwapUrl || '';
      document.getElementById('input-hotwallet').value = s.masterHotWallet || '';
      document.getElementById('input-min-withdraw').value = s.minWithdrawRS || 100;
      document.getElementById('input-ref-reward').value = s.refReward || 25;
      document.getElementById('input-ref-comm').value = s.refCommission || 10;
      document.getElementById('check-autopay').checked = s.autoPayoutEnabled !== false;
      document.getElementById('check-holdrule').checked = s.require1DollarHold !== false;
      document.getElementById('real-users-count').innerText = s.realUsersCount || 0;

      localLeaderboard = s.leaderboard || [];
      localAds = s.ads || [];
      localTasks = s.tasks || [];

      renderAdminLeaderboard();
      renderAdminAds();
      renderAdminTasks();
    });

    function addJoined(n) {
      const el = document.getElementById('input-joined');
      if (n === 0) el.value = 0;
      else el.value = parseInt(el.value || 0) + n;
    }

    function setOnline(n) { document.getElementById('input-online').value = n; }
    function addOnline(n) {
      const el = document.getElementById('input-online');
      el.value = parseInt(el.value || 0) + n;
    }

    function renderAdminLeaderboard() {
      const c = document.getElementById('admin-leaderboard-container');
      if (localLeaderboard.length === 0) {
        c.innerHTML = '<p class="text-xs text-slate-500 p-2 text-center">কোনো কাস্টম প্লেয়ার নেই। রিয়েল ইউজাররা মাইনিং করলে অটোমেটিক আসবে।</p>';
        return;
      }
      c.innerHTML = localLeaderboard.map((p, idx) => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center font-bold text-[10px]">#${idx+1}</span>
            <div>
              <p class="font-bold text-white">${p.name}</p>
              <p class="text-[10px] text-slate-400 font-sans">${p.username || ''}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-cyan-400 font-bold">${p.coins} RS</span>
            <button onclick="deletePlayer(${idx})" class="text-rose-400 hover:text-rose-300 p-1"><i class="fa-solid fa-trash"></i></button>
          </div>
        </div>
      `).join('');
    }

    function addLeaderboardPlayer() {
      const name = prompt('প্লেয়ারের নাম দিন (উদা: Shakib TON Master):');
      if (!name) return;
      const coins = prompt('RS টোকেনের পরিমাণ দিন (উদা: 25000):', '25000');
      localLeaderboard.push({ name: name, username: '@' + name.toLowerCase().replace(/ /g, '_'), coins: parseFloat(coins) || 1000 });
      renderAdminLeaderboard();
    }

    function deletePlayer(idx) {
      localLeaderboard.splice(idx, 1);
      renderAdminLeaderboard();
    }

    function promptNotice() {
      const n = prompt('নতুন ব্রডকাস্ট নোটিশের লেখা লিখুন:', document.getElementById('admin-notice-input').value);
      if (n) document.getElementById('admin-notice-input').value = n;
    }

    function renderAdminAds() {
      const c = document.getElementById('admin-ads-container');
      c.innerHTML = localAds.map((a, idx) => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <p class="font-bold text-white">${a.name}</p>
            <p class="text-[10px] text-slate-400 truncate max-w-xs font-mono">${a.url}</p>
            <p class="text-[10px] text-cyan-400 font-bold">${a.duration}s · +${a.reward} RS</p>
          </div>
          <button onclick="localAds.splice(${idx},1); renderAdminAds();" class="text-rose-400 p-1"><i class="fa-solid fa-trash"></i></button>
        </div>
      `).join('');
    }

    function addAdPrompt() {
      const name = prompt('বিজ্ঞাপনের নাম (উদা: Monetag Direct Link):');
      if (!name) return;
      const url = prompt('বিজ্ঞাপনের URL লিংক দিন:', 'https://');
      const rew = prompt('রিওয়ার্ড (RS টোকেন):', '15');
      localAds.push({ id: Date.now(), name: name, url: url, duration: 15, reward: parseFloat(rew) || 15 });
      renderAdminAds();
    }

    function renderAdminTasks() {
      const c = document.getElementById('admin-tasks-container');
      c.innerHTML = localTasks.map((t, idx) => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <p class="font-bold text-white">${t.title}</p>
            <p class="text-[10px] text-slate-400 font-mono">${t.url}</p>
            <p class="text-[10px] text-blue-400 font-bold">+${t.reward} RS</p>
          </div>
          <button onclick="localTasks.splice(${idx},1); renderAdminTasks();" class="text-rose-400 p-1"><i class="fa-solid fa-trash"></i></button>
        </div>
      `).join('');
    }

    function addTaskPrompt() {
      const title = prompt('চ্যানেল বা গ্রুপের নাম (উদা: Join Official Channel):');
      if (!title) return;
      const url = prompt('টেলিগ্রাম লিংক (উদা: https://t.me/...):', 'https://t.me/');
      const rew = prompt('রিওয়ার্ড (RS টোকেন):', '50');
      localTasks.push({ id: Date.now(), title: title, url: url, reward: parseFloat(rew) || 50, members: 'Official' });
      renderAdminTasks();
    }

    function saveAllSettings() {
      const payload = {
        notice: document.getElementById('admin-notice-input').value,
        baseJoined: parseInt(document.getElementById('input-joined').value || 0),
        baseOnline: parseInt(document.getElementById('input-online').value || 1),
        miningSpeed: parseFloat(document.getElementById('input-speed').value || 60),
        tokenPriceUSD: parseFloat(document.getElementById('input-price-usd').value || 0.054),
        tokenPriceTON: parseFloat(document.getElementById('input-price-ton').value || 0.0098),
        contractAddress: document.getElementById('input-contract').value,
        dexSwapUrl: document.getElementById('input-dex-url').value,
        masterHotWallet: document.getElementById('input-hotwallet').value,
        minWithdrawRS: parseFloat(document.getElementById('input-min-withdraw').value || 100),
        refReward: parseFloat(document.getElementById('input-ref-reward').value || 25),
        refCommission: parseFloat(document.getElementById('input-ref-comm').value || 10),
        autoPayoutEnabled: document.getElementById('check-autopay').checked,
        require1DollarHold: document.getElementById('check-holdrule').checked,
        leaderboard: localLeaderboard,
        ads: localAds,
        tasks: localTasks
      };

      fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      }).then(() => alert('🎉 অভিনন্দন! সমস্ত পরিবর্তন সফলভাবে সেভ হয়েছে এবং টেলিগ্রাম বটে লাইভ আপডেট হয়েছে!'));
    }
  </script>
</body>
</html>"""

class WebServiceHandler(BaseHTTPRequestHandler):
    def _send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self._send_cors()
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        # API: Return settings + real member counts
        if self.path.startswith('/api/settings'):
            real_count = len(DB["users"])
            joined_total = DB["baseJoined"] + real_count
            online_total = max(1, DB["baseOnline"] if DB["baseOnline"] > 0 else real_count)

            # Combined leaderboard: real miners + custom players sorted by coins
            combined_lb = list(DB["leaderboard"])
            for uid, u in DB["users"].items():
                combined_lb.append({
                    "name": u.get("name", "Miner"),
                    "user": "@" + str(uid),
                    "coins": u.get("coins", 0)
                })
            combined_lb.sort(key=lambda x: x.get("coins", 0), reverse=True)

            resp_data = dict(DB)
            resp_data["realUsersCount"] = real_count
            resp_data["joinedCount"] = joined_total
            resp_data["onlineCount"] = online_total
            resp_data["leaderboard"] = combined_lb[:10]

            self.send_response(200)
            self._send_cors()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp_data).encode('utf-8'))
            return

        # Render Health check
        if self.path in ('/health', '/healthz'):
            self.send_response(200)
            self._send_cors()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK", "service": "rs-token-bot"}).encode('utf-8'))
            return

        # Dedicated Owner Admin Control Panel (at /admin)
        if self.path.startswith('/admin'):
            self.send_response(200)
            self._send_cors()
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode('utf-8'))
            return

        # User Mini App (5 Tabs)
        self.send_response(200)
        self._send_cors()
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(USER_HTML.encode('utf-8'))

    def do_POST(self):
        # 1. Sync User Mining Coins & Real Registration
        if self.path.startswith('/api/user/sync'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                uid = str(data.get("uid", "miner_1"))
                DB["users"][uid] = {
                    "name": data.get("name", "Miner"),
                    "coins": float(data.get("coins", 0)),
                    "wallet": data.get("wallet", None),
                    "lastSeen": time.time()
                }

                real_count = len(DB["users"])
                joined_total = DB["baseJoined"] + real_count
                online_total = max(1, DB["baseOnline"] if DB["baseOnline"] > 0 else real_count)

                # Combined leaderboard
                combined_lb = list(DB["leaderboard"])
                for u_id, u_info in DB["users"].items():
                    combined_lb.append({
                        "name": u_info.get("name", "Miner"),
                        "user": "@" + str(u_id),
                        "coins": u_info.get("coins", 0)
                    })
                combined_lb.sort(key=lambda x: x.get("coins", 0), reverse=True)

                resp = {
                    "success": True,
                    "joinedCount": joined_total,
                    "onlineCount": online_total,
                    "notice": DB["notice"],
                    "miningSpeed": DB["miningSpeed"],
                    "tokenPriceUSD": DB["tokenPriceUSD"],
                    "contractAddress": DB["contractAddress"],
                    "leaderboard": combined_lb[:10],
                    "ads": DB["ads"],
                    "tasks": DB["tasks"]
                }
                self.send_response(200)
                self._send_cors()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(400)
                self._send_cors()
                self.end_headers()
                return

        # 2. Admin Save Settings
        if self.path.startswith('/api/settings'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                for k, v in data.items():
                    if k in DB:
                        DB[k] = v
                self.send_response(200)
                self._send_cors()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "db": DB}).encode('utf-8'))
                return
            except Exception:
                self.send_response(400)
                self._send_cors()
                self.end_headers()
                return

        self.send_response(404)
        self._send_cors()
        self.end_headers()

def run():
    # Automatically start bot.py in background if present
    if os.path.exists("bot.py"):
        try:
            import subprocess
            print("🤖 Launching bot.py in background...")
            subprocess.Popen(["python3", "bot.py"])
        except Exception:
            try:
                subprocess.Popen(["python", "bot.py"])
            except Exception as e:
                print(f"Bot auto-start notice: {e}")

    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting RS TOKEN Web Service on port {port}...")
    server = HTTPServer(('0.0.0.0', port), WebServiceHandler)
    server.serve_forever()

if __name__ == '__main__':
    run()
