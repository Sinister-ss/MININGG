# ⛏️ Telegram Mining Bot

Bot game mining lengkap untuk Telegram, dibangun dengan Python + aiogram 3.
Siap deploy ke **Railway** langsung dari **GitHub**.

---

## 🎮 Fitur Game

### ⛏️ 13 Alat Mining (7 Tier)
| Tier | Alat | Harga | Power |
|------|------|-------|-------|
| 1 Starter | ⛏️ Beliung Batu | **GRATIS** | 2 |
| 2 Basic | 🔨 Beliung Tembaga | 800 | 5 |
| 2 Basic | ⚒️ Beliung Besi | 2.500 | 12 |
| 3 Advanced | 🔩 Bor Baja | 8.000 | 28 |
| 3 Advanced | ⚡ Bor Listrik | 20.000 | 55 |
| 4 Expert | 🏗️ Pneumatic Jackhammer | 60.000 | 120 |
| 4 Expert | 💠 Diamond Drill | 150.000 | 250 |
| 5 Master | 🔬 Laser Cutter Pro | 400.000 | 500 |
| 5 Master | 🌟 Plasma Drill | 900.000 | 1.000 |
| 6 Legendary | 💎 Quantum Miner X | 3.000.000 | 2.500 |
| 6 Legendary | 🕳️ Void Extractor | 8.000.000 | 5.000 |
| 7 Mythical | ☄️ Celestial War Hammer | 25.000.000 | 12.000 |

### 🪨 15 Jenis Ore (dari umum hingga sangat langka)
- 🪨 Batu Bara → 🗿 Batu → ⬛ Besi → 🟤 Tembaga → ⬜ Perak
- 🟡 Emas → 🔵 Safir → 💚 Zamrud → ❤️ Rubi → 💎 Berlian
- 💜 Ametis → 🔮 Mithril → 🐉 Batu Naga → ✨ Debu Bintang → 🌑 Void Shard

### 🌍 6 Zona Mining
| Zona | Level | Biaya | Bonus Ore |
|------|-------|-------|-----------|
| 🏔️ Permukaan | 1 | Gratis | - |
| 🕯️ Gua Dalam | 5 | 3.000 | Besi & Perak +50% |
| ⛰️ Bawah Tanah | 15 | 30.000 | Emas & Safir +80% |
| 🌋 Gua Lava | 25 | 150.000 | Rubi & Berlian 2x |
| 🔮 Cavern Kristal | 40 | 600.000 | Ametis 2.5x, Mithril 2x |
| 🌑 Void Realm | 60 | 5.000.000 | Dragonstone 3x, Void Shard 2.5x |

### 🎒 8 Item Consumable
- ⚡ Energy Potion — pulihkan 50 energy
- ⚡⚡ Energy Potion XL — energy penuh
- 🍀 Luck Elixir — +20% rare ore 30 menit
- 💰 Double Coin Scroll — 2x koin 20 menit
- ⭐ XP Booster — 3x XP 20 menit
- 🤖 Auto Miner 1 jam
- 📦 Mystery Box — hadiah acak!
- 🔄 Rebirth Token — reset + permanent +50% coin bonus

### ✨ Mekanik Tambahan
- **💥 Critical Hit** — 2x koin (base 10% + bonus alat)
- **🍀 Lucky Strike** — 1.5x koin (base 5% + bonus alat)
- **🌟 Special Abilities** — tiap alat tier tinggi punya kemampuan unik
- **⭐ Sistem Level** — 1–100, XP dari tiap mining
- **🔥 Daily Streak** — bonus multiplier makin besar tiap hari
- **🏅 12 Achievement** — dengan hadiah koin
- **🔗 Referral** — bonus 300 koin untuk pemberi & penerima
- **🔄 Rebirth System** — prestige dengan permanent bonus

### 🔐 Fitur Admin
- Akun admin tidak terkena biaya apapun
- Beli alat/item/zona GRATIS
- 15+ perintah admin `/admin_*`
- Broadcast ke semua user
- Manajemen user lengkap

---

## 🚀 Deploy ke Railway (Langkah Demi Langkah)

### LANGKAH 1 — Persiapan Bot Token

1. Buka Telegram, cari **@BotFather**
2. Kirim `/newbot`
3. Ikuti instruksi, beri nama bot
4. Copy **token** yang diberikan (format: `123456:ABCdef...`)

### LANGKAH 2 — Cari ID Telegram Kamu (untuk Admin)

1. Chat **@userinfobot** di Telegram
2. Catat **ID** yang muncul (angka, contoh: `123456789`)

### LANGKAH 3 — Upload ke GitHub

```bash
# 1. Buat repo baru di github.com (jangan centang README)

# 2. Di folder miningbot, jalankan:
git init
git add .
git commit -m "🚀 Initial commit - Mining Bot"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

> ⚠️ **PENTING:** Pastikan `.env` TIDAK ikut ter-upload (sudah ada di `.gitignore`)

### LANGKAH 4 — Deploy di Railway

1. Buka **https://railway.app** → Login dengan GitHub
2. Klik **"New Project"** → **"Deploy from GitHub repo"**
3. Pilih repo mining bot kamu
4. Railway akan otomatis detect konfigurasi

### LANGKAH 5 — Set Environment Variables di Railway

Di dashboard Railway, klik project → tab **"Variables"** → tambahkan:

| Variable | Value | Keterangan |
|----------|-------|------------|
| `BOT_TOKEN` | `123456:ABCdef...` | Token dari BotFather |
| `ADMIN_IDS` | `123456789` | ID Telegram admin |

> Untuk lebih dari 1 admin: `123456789,987654321` (pisahkan koma)

### LANGKAH 6 — Deploy!

1. Setelah variabel disimpan, klik **"Deploy"**
2. Cek tab **"Logs"** untuk memastikan bot berjalan
3. Lihat pesan: `🚀 Bot is polling...` = sukses!

### LANGKAH 7 — Test Bot

Buka Telegram, cari username bot kamu, ketik `/start`

---

## 🏗️ Struktur Proyek

```
miningbot/
├── bot.py              # Entry point utama
├── config.py           # Semua data game (alat, ore, item, zona)
├── database.py         # Operasi database SQLite
├── game.py             # Logic game (mining, shop, level, dll)
├── keyboards.py        # Semua tombol Telegram
├── middlewares.py      # Throttling & auto-register
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start & menu utama
│   ├── mining.py       # Panel mining & aksi mine
│   ├── shop.py         # Toko alat, item, zona
│   ├── equipment.py    # Lihat & ganti peralatan
│   ├── inventory.py    # Inventaris & gunakan item
│   ├── profile.py      # Profil, statistik, prestasi
│   ├── leaderboard.py  # Papan peringkat
│   ├── daily.py        # Bonus harian
│   ├── admin.py        # Panel admin lengkap
│   └── help.py         # Panduan pemain
├── requirements.txt    # Dependencies Python
├── Procfile            # Untuk Railway
├── railway.toml        # Konfigurasi Railway
├── .env.example        # Contoh environment variable
└── .gitignore          # File yang diabaikan git
```

---

## ⌨️ Perintah Bot

### Pemain Biasa
| Perintah | Fungsi |
|----------|--------|
| `/start` | Menu utama & registrasi |
| `/mine` | Panel mining |
| `/profile` | Lihat profil & statistik |
| `/shop` | Toko peralatan |
| `/equipment` | Kelola peralatan |
| `/inventory` | Inventaris item |
| `/daily` | Klaim bonus harian |
| `/leaderboard` | Papan peringkat |
| `/help` | Panduan bermain |

### Admin (ADMIN_IDS)
| Perintah | Fungsi |
|----------|--------|
| `/adminhelp` | Panduan lengkap admin |
| `/admin_stats` | Statistik bot |
| `/admin_users` | Daftar semua user |
| `/admin_info <id>` | Info detail user |
| `/admin_addcoin <id> <jumlah>` | Tambah koin user |
| `/admin_setlevel <id> <level>` | Set level user |
| `/admin_setenergy <id> <jumlah>` | Set energy user |
| `/admin_givetool <id> <tool_id>` | Beri alat ke user |
| `/admin_giveitem <id> <item_id> [qty]` | Beri item ke user |
| `/admin_givezone <id> <zone_id>` | Buka zona untuk user |
| `/admin_reset <id>` | Reset data user |
| `/admin_broadcast <pesan>` | Broadcast ke semua user |
| `/admin_tools` | Daftar semua tool_id |
| `/admin_items` | Daftar semua item_id |
| `/admin_zones` | Daftar semua zone_id |

---

## 🔧 Kustomisasi

Semua data game ada di `config.py`:
- Tambah alat baru di `TOOLS`
- Tambah ore baru di `ORES`
- Tambah item baru di `ITEMS`
- Tambah zona baru di `ZONES`
- Ubah ekonomi game: `STARTING_BALANCE`, `DAILY_BONUS_BASE`, dll

---

## 📊 Tips Performa Railway

- Railway **free tier** cukup untuk bot skala kecil-menengah
- Database SQLite tersimpan di server Railway (tidak persisten jika restart!)
- Untuk produksi skala besar, upgrade ke PostgreSQL via Railway plugin
- Monitor penggunaan di dashboard Railway → tab "Metrics"

---

## 🆘 Troubleshooting

**Bot tidak merespons?**
→ Cek tab "Logs" di Railway, pastikan tidak ada error
→ Pastikan `BOT_TOKEN` sudah benar di Variables

**"Unauthorized" error?**
→ Token salah atau sudah kedaluwarsa, generate token baru di BotFather

**Database error?**
→ Railway restart menghapus SQLite. Pertimbangkan Railway PostgreSQL untuk data permanen

**Bot lambat?**
→ Throttling middleware aktif (0.8 detik). Edit `limit` di `bot.py` jika perlu

---

Selamat bermain! ⛏️⛏️⛏️
