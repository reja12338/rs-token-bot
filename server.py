import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Shared Persistent State across Admin & Users
STATE = {
    "notice": "🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই TON ব্লকচেইনে শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!",
    "miningSpeed": 60,
    "tokenPriceUSD": 0.054,
    "tokenPriceTON": 0.0098,
    "trend": "BULLISH",
    "totalJoined": 14820,
    "liveOnline": 1253,
    "require1DollarHold": True,
    "minWithdrawRS": 100,
    "autoPayoutEnabled": True,
    "masterHotWallet": "EQD_RS_AutoPayout_MasterPool_TON99",
    "contractAddress": "EQBv_RSTOKEN_Official_Jetton_MasterPool_99",
    "refReward": 25,
    "refCommission": 10
}

# USER MINI APP (স্ক্রিনশট ১ থেকে ১২ এর হুবহু ইন্টারফেস)
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
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050811; color: #f1f5f9; touch-action: manipulation; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .card-dark { background: #0c1222; border: 1px solid #1e293b; border-radius: 1.25rem; }
    .card-glow { box-shadow: 0 0 35px -5px rgba(6, 182, 212, 0.25); border-color: rgba(6, 182, 212, 0.3); }
    .coin-ring { animation: pulseGlow 2.5s infinite ease-in-out; }
    @keyframes pulseGlow { 0%, 100% { filter: drop-shadow(0 0 15px rgba(6, 182, 212, 0.4)); } 50% { filter: drop-shadow(0 0 30px rgba(6, 182, 212, 0.8)); } }
    ::-webkit-scrollbar { display: none; }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between pb-24 select-none">

  <!-- TOP HEADER -->
  <header class="w-full bg-[#0a0f1d] border-b border-slate-800 sticky top-0 z-40 px-4 py-3">
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
        <button onclick="alert('সাউন্ড টগল')" class="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center text-xs">
          <i class="fa-solid fa-volume-high"></i>
        </button>
        <button class="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1">
          <i class="fa-solid fa-globe"></i>
          <span>বাংলা</span>
        </button>
      </div>
    </div>

    <!-- Scrolling Announcement Banner -->
    <div class="mt-2.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-2 text-xs text-amber-300">
      <i class="fa-solid fa-fire text-amber-400"></i>
      <div class="truncate text-[11px]" id="notice-text">
        🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!
      </div>
    </div>

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
  <main class="flex-1 p-4 max-w-md mx-auto w-full space-y-4">

    <!-- ১. মাইনিং ট্যাব -->
    <section id="tab-mining" class="space-y-4">
      <div class="card-dark card-glow p-5 text-center relative overflow-hidden">
        <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">আপনার ব্যালেন্স</p>
        <div class="flex items-center justify-center gap-2.5">
          <span class="text-3xl text-cyan-400">💎</span>
          <span class="text-4xl font-black tracking-tight text-white font-mono tabular-nums" id="balance-display">45.00</span>
          <span class="text-lg font-bold text-cyan-400 font-mono">RS</span>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-mono">
          ≈ <span class="text-emerald-400 font-semibold" id="usd-val">$2.43 USD</span> · ≈ <span class="text-sky-400 font-semibold" id="ton-val">0.441 TON</span>
        </p>
      </div>

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

        <button onclick="toggleMining()" id="mining-btn" class="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 active:scale-95 transition-all flex items-center justify-center gap-2">
          <i class="fa-solid fa-pause" id="mining-btn-icon"></i>
          <span id="mining-btn-label">মাইনিং পজ করুন</span>
        </button>
      </div>

      <div class="grid grid-cols-2 gap-2.5">
        <div class="card-dark p-4">
          <div class="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
            <i class="fa-solid fa-users text-blue-400"></i>
            <span>মোট জয়েন করা ইউজার</span>
          </div>
          <div class="flex items-baseline gap-1">
            <span class="text-xl font-black text-white font-mono" id="stat-joined">14,820</span>
            <span class="text-xs text-blue-400 font-bold">+</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-0.5">সদস্য জয়েন করেছে</p>
        </div>

        <div class="card-dark p-4">
          <div class="flex items-center justify-between text-xs mb-1">
            <div class="flex items-center gap-1.5 text-slate-400">
              <i class="fa-solid fa-tower-broadcast text-emerald-400 animate-pulse"></i>
              <span>লাইভ অনলাইনে সক্রিয়</span>
            </div>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">LIVE</span>
          </div>
          <p class="text-xl font-black text-emerald-400 font-mono" id="stat-online">1,253</p>
          <p class="text-[10px] text-slate-500 mt-0.5">এখন লাইভ মাইনিং করছে</p>
        </div>
      </div>

      <!-- Leaderboard -->
      <div class="card-dark p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <i class="fa-solid fa-trophy text-amber-400"></i>
            <h3 class="text-xs font-bold text-white uppercase">শীর্ষ মাইনার্স লিডারবোর্ড</h3>
          </div>
          <div class="flex items-center gap-1 bg-slate-900 p-0.5 rounded-lg border border-slate-800 text-[10px]">
            <button class="px-2 py-0.5 rounded bg-cyan-500 text-white font-bold">অল-টাইম</button>
            <button class="px-2 py-0.5 text-slate-400">আজকের সেরা</button>
          </div>
        </div>

        <div class="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-between text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-[11px]">#128</span>
            <div>
              <p class="font-bold text-white">আপনার প্রোফাইল (You)</p>
              <p class="text-[10px] text-slate-400 font-sans">আপনার বর্তমান র‍্যাংক: #128</p>
            </div>
          </div>
          <div class="text-right">
            <p class="font-bold text-cyan-300" id="user-rank-coins">45.00 RS</p>
            <p class="text-[10px] text-slate-400">≈ $2.43</p>
          </div>
        </div>

        <div class="space-y-2 text-xs font-mono">
          <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">1</span>
              <div>
                <p class="font-bold text-white">TON Whale Alpha 🇧🇩</p>
                <p class="text-[10px] text-slate-400">@ton_whale99 · TON Whale</p>
              </div>
            </div>
            <div class="text-right"><p class="font-bold text-amber-400">48,750 RS</p><p class="text-[10px] text-slate-400">≈ $2633 USD</p></div>
          </div>
          <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-lg bg-slate-700 text-slate-200 flex items-center justify-center font-bold">2</span>
              <div>
                <p class="font-bold text-white">Rejaul Crypto 🇧🇩</p>
                <p class="text-[10px] text-slate-400">@crypto_reja · Diamond Miner</p>
              </div>
            </div>
            <div class="text-right"><p class="font-bold text-slate-200">39,400 RS</p><p class="text-[10px] text-slate-400">≈ $2128 USD</p></div>
          </div>
          <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-lg bg-amber-800/40 text-amber-500 flex items-center justify-center font-bold">3</span>
              <div>
                <p class="font-bold text-white">Shakib TON Master 🇧🇩</p>
                <p class="text-[10px] text-slate-400">@shakib_ton · Gold Staker</p>
              </div>
            </div>
            <div class="text-right"><p class="font-bold text-amber-500">32,150 RS</p><p class="text-[10px] text-slate-400">≈ $1736 USD</p></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ২. বিজ্ঞাপন দেখে টোকেন আয় -->
    <section id="tab-ads" class="space-y-4 hidden">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-cyan-500/20">
          <i class="fa-solid fa-tv"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">বিজ্ঞাপন দেখে টোকেন আয়</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">সরাসরি অ্যাড লিংকে ক্লিক করে নির্দিষ্ট সময় দেখুন এবং ইনস্ট্যান্ট RS টোকেন রিওয়ার্ড নিন!</p>
      </div>

      <div class="space-y-3">
        <div class="card-dark p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-cyan-400 text-xs">AD</div>
            <div>
              <div class="flex items-center gap-1.5"><span class="text-xs font-bold text-white">Monetag SmartLink</span><span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-cyan-500/20 text-cyan-400">SmartLink</span></div>
              <p class="text-xs text-emerald-400 font-mono font-bold mt-0.5">⏱️ 15s · +15 RS TOKEN</p>
            </div>
          </div>
          <button onclick="playAd(1, 15, 15)" id="ad-play-1" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-bold text-xs shadow-md">অ্যাড দেখুন ↗</button>
        </div>

        <div class="card-dark p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-purple-400 text-xs">AD</div>
            <div>
              <div class="flex items-center gap-1.5"><span class="text-xs font-bold text-white">Adsterra High CPM Ad #2</span><span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-purple-500/20 text-purple-400">Direct</span></div>
              <p class="text-xs text-emerald-400 font-mono font-bold mt-0.5">⏱️ 20s · +20 RS TOKEN</p>
            </div>
          </div>
          <button onclick="playAd(2, 20, 20)" id="ad-play-2" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-bold text-xs shadow-md">অ্যাড দেখুন ↗</button>
        </div>
      </div>
    </section>

    <!-- ৩. টেলিগ্রাম চ্যানেল ও গ্রুপ টাস্ক -->
    <section id="tab-tasks" class="space-y-4 hidden">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-blue-500/20">
          <i class="fa-solid fa-paper-plane"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">টেলিগ্রাম চ্যানেল ও গ্রুপ টাস্ক</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">আমাদের চ্যানেল এবং গ্রুপগুলোতে জয়েন করুন এবং সাথে সাথে RS টোকেন আনলক করুন!</p>
        <p class="text-[11px] text-cyan-400 mt-2 font-medium">এডমিন প্যানেল থেকে আপনি যেকোনো সময় নতুন চ্যানেল বা গ্রুপ যুক্ত করতে পারবেন।</p>
      </div>

      <div class="space-y-3">
        <div class="card-dark p-4 space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center text-lg"><i class="fa-brands fa-telegram"></i></div>
            <div>
              <span class="text-[10px] font-bold text-slate-400 uppercase">Channel</span>
              <h4 class="text-xs font-bold text-white">Join Official RS TOKEN Channel</h4>
              <p class="text-[11px] text-slate-400 mt-0.5">👥 124,000 members · <span class="text-emerald-400 font-bold font-mono">+50 RS</span></p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="window.open('https://t.me/RSTokenOfficial', '_blank')" class="py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold">জয়েন করুন ↗</button>
            <button onclick="claimTaskReward(1, 50)" id="task-btn-1" class="py-2 rounded-xl bg-cyan-500 text-white text-xs font-bold">যাচাই করুন</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ৪. রেফার করুন ও আয় বাড়ান -->
    <section id="tab-referral" class="space-y-4 hidden">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-cyan-500/20">
          <i class="fa-solid fa-user-plus"></i>
        </div>
        <h2 class="text-base font-extrabold text-white mb-1">রেফার করুন ও আয় বাড়ান</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto">প্রতিটি সফল আমন্ত্রণে আপনি ও আপনার বন্ধু উভয়ই RS টোকেন পাবেন!</p>
        <div class="grid grid-cols-2 gap-3 mt-4 text-left">
          <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
            <p class="text-[11px] text-slate-400">প্রতি সফল রেফারে পাবেন</p>
            <p class="text-base font-black text-cyan-400 font-mono mt-1">+25 RS</p>
            <p class="text-[10px] text-cyan-300 font-bold">TOKEN</p>
          </div>
          <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
            <p class="text-[11px] text-slate-400">রেফারেলদের মাইনিং থেকে</p>
            <p class="text-base font-black text-emerald-400 font-mono mt-1">10%</p>
            <p class="text-[10px] text-emerald-400 font-bold">Commission</p>
          </div>
        </div>
      </div>

      <div class="card-dark p-4 space-y-3">
        <label class="text-[11px] font-bold text-slate-400 uppercase">আপনার পার্সোনাল রেফারেল লিংক:</label>
        <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between gap-2">
          <span class="text-xs font-mono text-cyan-300 truncate" id="ref-url">https://t.me/rs_token_mining_bot?start=ref7450</span>
          <button onclick="navigator.clipboard.writeText('https://t.me/rs_token_mining_bot?start=ref7450'); alert('কপি হয়েছে!');" class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-bold">লিংক কপি করুন</button>
        </div>
        <button onclick="window.open('https://t.me/share/url?url=https://t.me/rs_token_mining_bot?start=ref7450')" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs flex items-center justify-center gap-2">
          <i class="fa-solid fa-share-nodes"></i><span>টেলিগ্রামে শেয়ার করুন</span>
        </button>
      </div>

      <div class="card-dark p-4 flex items-center justify-between">
        <div>
          <p class="text-[11px] text-slate-400">মোট রেফারেল</p>
          <p class="text-lg font-black text-white font-mono mt-0.5">3 Users Invited</p>
          <p class="text-[11px] text-cyan-400 font-mono font-bold">Unclaimed: +75 RS</p>
        </div>
        <button onclick="balance+=75; updateBalance(); alert('+75 RS রেফারেল বোনাস যোগ হয়েছে!');" class="px-4 py-2.5 rounded-xl bg-emerald-500 text-white font-bold text-xs">
          🪄 রেফারেল বোনাস তুলুন
        </button>
      </div>
    </section>

    <!-- ৫. TON ওয়ালেট ও উইথড্র -->
    <section id="tab-wallet" class="space-y-4 hidden">
      <div class="card-dark p-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto mb-3 text-2xl border border-cyan-500/20"><i class="fa-solid fa-wallet"></i></div>
        <h2 class="text-base font-extrabold text-white mb-1">TON ওয়ালেট ও উইথড্র</h2>
        <p class="text-xs text-slate-400 max-w-xs mx-auto mb-4">আপনার Tonkeeper ওয়ালেট কানেক্ট করে সরাসরি আপনার ওয়ালেটে RS টোকেন উইথড্র করুন।</p>
        <button onclick="toggleWalletModal()" id="connect-wallet-main-btn" class="w-full py-3 rounded-xl bg-cyan-500 text-white font-bold text-xs shadow-lg">
          Tonkeeper ওয়ালেট কানেক্ট করুন 💎
        </button>
      </div>

      <div class="card-dark p-4 space-y-2">
        <div class="flex items-center justify-between text-xs font-bold text-slate-300">
          <span>RS TOKEN Smart Contract (TON Jetton)</span>
          <button onclick="navigator.clipboard.writeText('EQBv_RSTOKEN_Official_Jetton_MasterPool_99'); alert('কপি হয়েছে!');"><i class="fa-solid fa-copy"></i></button>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-300 truncate">EQBv_RSTOKEN_Official_Jetton_MasterPool_99</div>
      </div>

      <div class="card-dark p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs font-bold text-white uppercase">RS / USD LIVE TON CHART</h3>
            <div class="flex items-baseline gap-2 mt-1">
              <span class="text-xl font-black text-white font-mono">$0.0543</span>
              <span class="text-xs font-bold text-emerald-400 font-mono">↗+0.56%</span>
            </div>
          </div>
          <div class="text-right"><p class="text-[10px] text-slate-400 font-mono">TON Pair Value:</p><p class="text-xs font-bold text-cyan-300 font-mono">~0.0099 TON</p></div>
        </div>
        <div class="h-40 w-full bg-[#070b14] rounded-xl p-2 relative flex items-end"><canvas id="walletChart" class="w-full h-full"></canvas></div>
        <div class="grid grid-cols-2 gap-2">
          <button onclick="alert('টোকেন কিনুন Tonkeeper')" class="py-2.5 rounded-xl bg-emerald-500 text-white font-bold text-xs">টোকেন কিনুন (Buy)</button>
          <button onclick="alert('টোকেন বিক্রি')" class="py-2.5 rounded-xl bg-slate-800 text-slate-300 font-bold text-xs">টোকেন বিক্রি (Sell)</button>
        </div>
      </div>

      <div class="card-dark p-5 space-y-3 border-amber-500/30">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold text-white flex items-center gap-2"><i class="fa-solid fa-lock text-amber-400"></i> উইথড্র অপশন লক করা আছে</h4>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">LOCKED</span>
        </div>
        <p class="text-xs text-slate-300">বট স্প্যাম প্রতিরোধ ও লিকুইডিটি যাচাইকরণের জন্য ব্যবহারকারীকে $১ ডলারের RS TOKEN কিনে ২৪ ঘণ্টার জন্য হোল্ড করতে হবে। ২৪ ঘণ্টা পর স্বয়ংক্রিয়ভাবে উইথড্র আনলক হয়ে যাবে।</p>
        <button onclick="alert('Tonkeeper ওপেন হচ্ছে... $১ হোল্ড আনলক করুন')" class="w-full py-3.5 rounded-xl bg-amber-500 text-slate-950 font-black text-xs shadow-lg">
          🛡️ $১ ডলারের RS টোকেন কিনুন ও আনলক করুন (Open Tonkeeper)
        </button>
      </div>
    </section>

  </main>

  <!-- ৫টি নির্দিষ্ট বটম বাটন (স্ক্রিনশট ১-১২ এর হুবহু) -->
  <nav class="fixed bottom-0 inset-x-0 bg-[#0a0f1d]/95 backdrop-blur-md border-t border-slate-800 px-2 py-2 flex items-center justify-around z-40 max-w-md mx-auto">
    <button onclick="switchTab('mining')" id="nav-mining" class="flex flex-col items-center gap-1 text-cyan-400 min-w-[56px]"><i class="fa-solid fa-pickaxe text-base"></i><span class="text-[10px] font-bold">১. মাইনিং</span></button>
    <button onclick="switchTab('ads')" id="nav-ads" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-tv text-base"></i><span class="text-[10px] font-bold">২. অ্যাডস</span></button>
    <button onclick="switchTab('tasks')" id="nav-tasks" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-list-check text-base"></i><span class="text-[10px] font-bold">৩. টাস্ক</span></button>
    <button onclick="switchTab('referral')" id="nav-referral" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-users text-base"></i><span class="text-[10px] font-bold">৪. রেফারেল</span></button>
    <button onclick="switchTab('wallet')" id="nav-wallet" class="flex flex-col items-center gap-1 text-slate-400 min-w-[56px]"><i class="fa-solid fa-wallet text-base"></i><span class="text-[10px] font-bold">৫. ওয়ালেট</span></button>
  </nav>

  <!-- Tonkeeper Modal -->
  <div id="wallet-modal" class="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4 hidden">
    <div class="w-full max-w-sm rounded-2xl bg-[#0c1222] border border-slate-800 p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-sm font-bold text-white">TON ওয়ালেট কানেক্ট</h3>
        <button onclick="toggleWalletModal()" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <button onclick="walletAddr='EQBv...7450'; localStorage.setItem('rs_wallet', walletAddr); document.getElementById('connect-wallet-main-btn').innerText=walletAddr+' (কানেক্টেড)'; toggleWalletModal(); alert('Tonkeeper কানেক্ট সফল!');" class="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span class="text-xs font-bold text-white">Tonkeeper (অফিশিয়াল)</span>
        <i class="fa-solid fa-chevron-right text-xs text-slate-500"></i>
      </button>
    </div>
  </div>

  <script>
    if (window.Telegram && window.Telegram.WebApp) { window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand(); }
    let balance = parseFloat(localStorage.getItem('rs_balance') || '45.00');
    let isMining = true;
    let walletAddr = localStorage.getItem('rs_wallet') || null;

    fetch('/api/settings').then(r => r.json()).then(s => {
      if (s.notice) document.getElementById('notice-text').innerText = s.notice;
      if (s.tokenPriceUSD) document.getElementById('header-price-display').innerText = '$ 1 RS = $' + s.tokenPriceUSD + ' USD';
      if (s.miningSpeed) document.getElementById('speed-text').innerText = '+' + s.miningSpeed + ' RS / hr';
      if (s.totalJoined) document.getElementById('stat-joined').innerText = s.totalJoined.toLocaleString();
      if (s.liveOnline) document.getElementById('stat-online').innerText = s.liveOnline.toLocaleString();
    }).catch(e => console.log(e));

    function updateBalance() {
      document.getElementById('balance-display').innerText = balance.toFixed(2);
      document.getElementById('user-rank-coins').innerText = balance.toFixed(2) + ' RS';
      document.getElementById('usd-val').innerText = '$' + (balance * 0.054).toFixed(2) + ' USD';
      document.getElementById('ton-val').innerText = (balance * 0.0098).toFixed(3) + ' TON';
      localStorage.setItem('rs_balance', balance.toString());
    }
    updateBalance();

    setInterval(() => { if (isMining) { balance += 0.0166; updateBalance(); } }, 1000);

    function toggleMining() {
      isMining = !isMining;
      document.getElementById('mining-btn-label').innerText = isMining ? 'মাইনিং পজ করুন' : 'মাইনিং শুরু করুন 🚀';
      document.getElementById('mining-btn-icon').className = isMining ? 'fa-solid fa-pause' : 'fa-solid fa-play';
      document.getElementById('status-pill').innerText = isMining ? 'মাইনিং সক্রিয়' : 'মাইনিং বন্ধ রয়েছে';
    }

    function switchTab(t) {
      ['mining','ads','tasks','referral','wallet'].forEach(id => {
        document.getElementById('tab-' + id).classList.add('hidden');
        document.getElementById('nav-' + id).className = 'flex flex-col items-center gap-1 text-slate-400 min-w-[56px]';
      });
      document.getElementById('tab-' + t).classList.remove('hidden');
      document.getElementById('nav-' + t).className = 'flex flex-col items-center gap-1 text-cyan-400 min-w-[56px] font-bold';
      if (t === 'wallet') drawWalletChart();
    }

    function toggleWalletModal() { document.getElementById('wallet-modal').classList.toggle('hidden'); }
    function playAd(id, sec, rew) {
      const b = document.getElementById('ad-play-' + id);
      b.disabled = true; let r = sec;
      const itv = setInterval(() => {
        r--;
        if (r > 0) b.innerText = r + 's';
        else { clearInterval(itv); balance += rew; updateBalance(); b.innerText = 'দেখা হয়েছে ✅'; alert('🎉 +' + rew + ' RS যোগ হয়েছে!'); }
      }, 1000);
    }

    function claimTaskReward(id, rew) {
      balance += rew; updateBalance();
      document.getElementById('task-btn-' + id).innerText = 'যাচাইকৃত ✅';
      alert('🎉 +' + rew + ' RS যোগ হয়েছে!');
    }

    // Secret Admin Access via RS Logo (3 Taps)
    let clicks = 0;
    function handleSecretAdminClick() {
      clicks++;
      if (clicks >= 3) {
        clicks = 0;
        const pin = prompt('🔐 অ্যাডমিন সিক্রেট পিন দিন:');
        if (pin === '2026' || pin === 'admin') window.location.href = '/admin';
      }
    }

    function drawWalletChart() {
      const c = document.getElementById('walletChart'); if(!c) return;
      const ctx = c.getContext('2d');
      c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
      ctx.clearRect(0,0,c.width,c.height);
      const pts = [22, 35, 30, 48, 44, 70, 65, 85, 80, 95];
      const step = c.width / (pts.length - 1);
      ctx.beginPath(); ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 3;
      pts.forEach((p, i) => { const y = c.height - (p/100)*c.height; if(i===0) ctx.moveTo(0,y); else ctx.lineTo(i*step, y); });
      ctx.stroke();
    }
  </script>
</body>
</html>"""

# SEPARATE DEDICATED ADMIN CONTROL PANEL (স্ক্রিনশট ১৩ থেকে ২০ এর হুবহু ইন্টারফেস)
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
<body class="min-h-screen p-4 sm:p-6 max-w-2xl mx-auto space-y-5 pb-20 select-none">

  <!-- Admin Header -->
  <div class="card-dark p-5 flex items-center justify-between border-cyan-500/30">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-2xl font-bold border border-cyan-500/20">
        <i class="fa-solid fa-sliders"></i>
      </div>
      <div>
        <h1 class="text-base font-black text-white">RS TOKEN এডমিন কন্ট্রোল প্যানেল</h1>
        <p class="text-xs text-slate-400">মাইনিং স্পিড, টোকেনের ভ্যালু, অ্যাড নেটওয়ার্ক ও উইথড্র রুলস কন্ট্রোল</p>
      </div>
    </div>
    <a href="/" class="px-3.5 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold hover:bg-slate-700 flex items-center gap-1.5">
      <i class="fa-solid fa-arrow-left"></i> বটে ফিরে যান
    </a>
  </div>

  <!-- Save Button -->
  <button onclick="saveAllSettings()" class="w-full py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black text-sm shadow-xl flex items-center justify-center gap-2 active:scale-98">
    <i class="fa-solid fa-floppy-disk"></i><span>পরিবর্তনগুলো সেভ করুন</span>
  </button>

  <!-- ইউজার ও অনলাইন অ্যানালিটিক্স ম্যানেজার (স্ক্রিনশট ১৩) -->
  <div class="card-dark p-5 space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-users text-cyan-400"></i> 👥 ইউজার ও অনলাইন অ্যানালিটিক্স ম্যানেজার</h2>
      <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 font-mono">LIVE TELEMETRY</span>
    </div>
    <p class="text-xs text-slate-400">টেলিগ্রাম বটে মোট কতজন ইউজার জয়েন করেছে এবং বর্তমানে কতজন সক্রিয়ভাবে অনলাইনে মাইনিং করছে তা পরিচালনা করুন।</p>

    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <span class="text-slate-400 font-bold uppercase text-[11px]">মোট রেজিস্টার্ড ইউজার সংখ্যা (Base)</span>
      <div class="flex items-center justify-between">
        <input type="number" id="input-joined" value="14820" class="bg-transparent text-2xl font-black text-white font-mono w-40 focus:outline-none">
        <span class="text-xs text-slate-400">জন ইউজার</span>
      </div>
      <div class="flex gap-2 pt-1">
        <button onclick="document.getElementById('input-joined').value=parseInt(document.getElementById('input-joined').value)+100" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-cyan-300 font-bold">+100</button>
        <button onclick="document.getElementById('input-joined').value=parseInt(document.getElementById('input-joined').value)+500" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-cyan-300 font-bold">+500</button>
        <button onclick="document.getElementById('input-joined').value=parseInt(document.getElementById('input-joined').value)+1000" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-cyan-300 font-bold">+1,000</button>
      </div>
    </div>

    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <span class="text-slate-400 font-bold uppercase text-[11px]">লাইভ অনলাইন ইউজার সংখ্যা (Base)</span>
      <div class="flex items-center justify-between">
        <input type="number" id="input-online" value="1248" class="bg-transparent text-2xl font-black text-emerald-400 font-mono w-40 focus:outline-none">
        <span class="text-xs text-slate-400">জন অনলাইন</span>
      </div>
      <div class="flex gap-2 pt-1">
        <button onclick="document.getElementById('input-online').value=parseInt(document.getElementById('input-online').value)+25" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-emerald-300 font-bold">+25</button>
        <button onclick="document.getElementById('input-online').value=parseInt(document.getElementById('input-online').value)+50" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-emerald-300 font-bold">+50</button>
        <button onclick="document.getElementById('input-online').value=parseInt(document.getElementById('input-online').value)+100" class="px-3 py-1 rounded bg-slate-800 text-xs font-mono text-emerald-300 font-bold">+100</button>
      </div>
    </div>
  </div>

  <!-- ব্রডকাস্ট নোটিশ ম্যানেজার (স্ক্রিনশট ১৭) -->
  <div class="card-dark p-5 space-y-3">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-bullhorn text-amber-400"></i> টেলিগ্রাম বট ব্রডকাস্ট নোটিশ ম্যানেজার</h2>
      <button onclick="const m=prompt('নতুন নোটিশ লিখুন:'); if(m){document.getElementById('admin-notice-input').value=m; saveAllSettings();}" class="px-3 py-1.5 rounded-xl bg-amber-500 text-slate-950 font-black text-xs">+ নতুন নোটিশ পাঠান</button>
    </div>
    <textarea id="admin-notice-input" rows="2" class="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white">🔥 স্পেশাল আপডেট: RS TOKEN লিস্টিং ও এয়ারড্রপ খুব শীঘ্রই শুরু হতে চলেছে! সক্রিয় থাকুন এবং আপনার ওয়ালেট কানেক্ট রাখুন!</textarea>
  </div>

  <!-- TOKEN & MINING CONTROLS (স্ক্রিনশট ১৪) -->
  <div class="card-dark p-5 space-y-3">
    <h2 class="text-sm font-bold text-white uppercase"><i class="fa-solid fa-chart-line text-cyan-400 mr-1"></i> TOKEN & MINING CONTROLS</h2>
    <div class="space-y-3 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মাইনিং স্পিড (RS টোকেন / ঘণ্টা):</label>
        <input type="number" id="input-speed" value="60" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] font-bold text-slate-400 uppercase">টোকেন লাইভ দাম ($USD):</label>
          <input type="number" step="0.001" id="input-price-usd" value="0.054" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
        </div>
        <div>
          <label class="text-[11px] font-bold text-slate-400 uppercase">টোকেন লাইভ দাম (TON):</label>
          <input type="number" step="0.0001" id="input-price-ton" value="0.0098" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
        </div>
      </div>
    </div>
  </div>

  <!-- INSTANT AUTO-PAYMENT RULES (স্ক্রিনশট ১৬) -->
  <div class="card-dark p-5 space-y-3">
    <h2 class="text-sm font-bold text-white uppercase"><i class="fa-solid fa-bolt text-amber-400 mr-1"></i> AUTO-PAYMENT & WITHDRAW RULES</h2>
    <div class="space-y-2 text-xs">
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">TON Payout Master Hot Wallet:</label>
        <input type="text" id="input-hotwallet" value="EQD_RS_AutoPayout_MasterPool_TON99" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-cyan-300 font-mono text-xs">
      </div>
      <div>
        <label class="text-[11px] font-bold text-slate-400 uppercase">মিনিমাম উইথড্র লিমিট (RS):</label>
        <input type="number" id="input-min-withdraw" value="100" class="w-full mt-1 p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono font-bold">
      </div>
    </div>
  </div>

  <script>
    fetch('/api/settings').then(r => r.json()).then(s => {
      if (s.notice) document.getElementById('admin-notice-input').value = s.notice;
      if (s.totalJoined) document.getElementById('input-joined').value = s.totalJoined;
      if (s.liveOnline) document.getElementById('input-online').value = s.liveOnline;
      if (s.miningSpeed) document.getElementById('input-speed').value = s.miningSpeed;
      if (s.tokenPriceUSD) document.getElementById('input-price-usd').value = s.tokenPriceUSD;
      if (s.tokenPriceTON) document.getElementById('input-price-ton').value = s.tokenPriceTON;
      if (s.masterHotWallet) document.getElementById('input-hotwallet').value = s.masterHotWallet;
      if (s.minWithdrawRS) document.getElementById('input-min-withdraw').value = s.minWithdrawRS;
    });

    function saveAllSettings() {
      const payload = {
        notice: document.getElementById('admin-notice-input').value,
        totalJoined: parseInt(document.getElementById('input-joined').value),
        liveOnline: parseInt(document.getElementById('input-online').value),
        miningSpeed: parseInt(document.getElementById('input-speed').value),
        tokenPriceUSD: parseFloat(document.getElementById('input-price-usd').value),
        tokenPriceTON: parseFloat(document.getElementById('input-price-ton').value),
        masterHotWallet: document.getElementById('input-hotwallet').value,
        minWithdrawRS: parseInt(document.getElementById('input-min-withdraw').value)
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
    def do_GET(self):
        if self.path.startswith('/api/settings'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(STATE).encode('utf-8'))
            return

        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode('utf-8'))
            return

        if self.path.startswith('/admin'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode('utf-8'))
            return

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
                    if k in STATE:
                        STATE[k] = v
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "state": STATE}).encode('utf-8'))
                return
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()

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
