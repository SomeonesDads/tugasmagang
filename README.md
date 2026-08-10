![diagram](tugasmagang.drawio.png)

# Menjalankan Backend dan Bot Telegram

## Environment modes

The backend accepts `NODE_ENV=development`, `staging`, or `production`.
`prod` is accepted as an alias for `production`. Database settings use the
`DATABASE_*` variables documented in the example files.

### Local development

Development is disposable and does not use the office database. Start the
local PostgreSQL, backend, and idempotent development seed with:

```powershell
docker compose -f .\docker-compose.local.yml up --build
```

The API is available at `http://127.0.0.1:8000`. The seed uses only
`proposedtables.sql`, inserts sample tickets and Telegram assignments, and
leaves the production pipeline disabled. To reset the database completely:

```powershell
docker compose -f .\docker-compose.local.yml down -v
```

To run the Telegram bot in Docker, set `TELEGRAM_BOT_TOKEN` in the shell and
enable its Compose profile:

```powershell
$env:TELEGRAM_BOT_TOKEN = "your-token"
docker compose -f .\docker-compose.local.yml --profile bot up --build
```

### Staging

Copy `backend/.env.staging.example` to `backend/.env.staging`, fill in the
staging database values, and run the backend locally or with:

```powershell
docker compose -f .\docker-compose.staging.yml up --build
```

The Telegram bot remains a local process and should use its local staging
`.env` with `API_BASE_URL=http://127.0.0.1:8000/api`.

### Production

Copy the production example files to `.env.production` files, fill them from
the infrastructure team's database and Telegram values, and deploy the
Compose stack on the office VM:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

Production Compose does not create a database container; it connects to the
approved production database through injected `DATABASE_*` variables. Never
commit the production env files. SSH port, database host/port, firewall rules,
Docker installation, and the production database credentials are still needed
from infrastructure before deployment.

Panduan ini menjalankan backend FastAPI serta bot Telegram secara lokal di
Windows/PowerShell. Bot membaca tiket dari backend dan command
`/notify_engineers` mengirim lima tiket mock ke masing-masing engineer:
`8887960178` dan `8510386982`.

## 1. Siapkan Python environment

Dari folder root repository, buat virtual environment (cukup sekali):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\backend\requirements.txt
pip install -r .\frontend\TelegramBotRCA\requirements.txt
```

Jika PowerShell menolak `Activate.ps1`, jalankan sekali pada terminal tersebut:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. Konfigurasi bot

Salin contoh konfigurasi lalu isi token bot yang aktif dari BotFather:

```powershell
Copy-Item .\frontend\TelegramBotRCA\.env.example .\frontend\TelegramBotRCA\.env
```

Isi `frontend/.env` seperti berikut:

```env
TELEGRAM_BOT_TOKEN=token_baru_dari_botfather
API_BASE_URL=http://127.0.0.1:8000/api
ENGINEER_DISTRICT=DISTRICT-8887960178
```

`ENGINEER_DISTRICT` dipakai untuk memilih district saat mengirim notifikasi.
Menu **View Ticket** sekarang mengirimkan Telegram ID pengguna ke backend; the
backend resolves that engineer's district from `telegram_district_role`.

> Jangan commit file `.env` atau membagikan token bot. Bila token pernah
> tersimpan di source code, buat token baru melalui BotFather sebelum menjalankan bot.

## 3. Jalankan backend

Buka terminal pertama dari root repository dan aktifkan environment bila belum:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location .\backend
uvicorn api:app --reload
```

Backend tersedia pada `http://127.0.0.1:8000`; dokumentasi endpoint ada di
`http://127.0.0.1:8000/docs`.

After migrating `proposedtables.sql`, seed the normalized RCA lookup tables
from the backend directory:

```powershell
python .\seed_rca.py
```

The command is safe to rerun. The bot reads RCA categories and details through
`GET /api/rca-options`; it does not contain local dummy RCA data.

Untuk memastikan data mock tersedia, dari terminal lain jalankan:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/engineers/DISTRICT-8887960178
Invoke-RestMethod http://127.0.0.1:8000/api/tickets/8887960178
Invoke-RestMethod http://127.0.0.1:8000/api/mock/engineers/8887960178/tickets
```

Engineer routing rows can be added directly after migrating the schema:

```sql
INSERT INTO mba_sumbagut.telegram_district_role
    (telegram_id, district_operation_do, role)
VALUES
    (8887960178, 'DISTRICT-8887960178', 'engineer');
```

## 4. Jalankan bot

Buka terminal kedua dari root repository:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location .\frontend\TelegramBotRCA
python .\main.py
```

Biarkan kedua terminal tetap berjalan selama pengujian.

## 5. Mulai chat dengan bot di Telegram

1. Di Telegram, cari username bot yang dibuat melalui **@BotFather**, atau buka
   tautan `https://t.me/<username_bot>`.
2. Buka chat bot lalu tekan **Start** atau kirim `/start` dari kedua akun
   engineer (`8887960178` dan `8510386982`). Ini wajib dilakukan sekali agar
   Telegram mengizinkan bot mengirim pesan ke mereka.
3. Dari chat bot mana pun, kirim `/notify_engineers`.
4. Kedua engineer akan menerima pesan penugasan berisi lima tiket mock. Mereka
   dapat memilih **Engineer Field** → **View Ticket** untuk melihat dan mengisi
   RCA pada tiket yang ditampilkan.

Jika hasil command menyatakan pesan gagal dikirim, pastikan ID Telegram itu
benar, akun tersebut sudah mengirim `/start`, dan `TELEGRAM_BOT_TOKEN` valid.

## 6. Mount staging dan production dengan Docker Compose

Staging dan production memakai database PostgreSQL yang disediakan di luar
Compose. Compose menjalankan backend; production juga menjalankan Telegram bot.

### Staging

Dari root repository, buat file konfigurasi lalu isi kredensial database staging:

```powershell
Copy-Item .\backend\.env.staging.example .\backend\.env.staging
```

Untuk pengujian manual, biarkan `ENABLE_PIPELINE=false` agar scheduler tidak
mengubah data otomatis. Start staging dengan:

```powershell
docker compose -f .\docker-compose.staging.yml up --build -d
```

Periksa status dan log:

```powershell
docker compose -f .\docker-compose.staging.yml ps
docker compose -f .\docker-compose.staging.yml logs -f backend
```

API tersedia di `http://127.0.0.1:8000` dan dokumentasinya di
`http://127.0.0.1:8000/docs`. Hentikan staging dengan:

```powershell
docker compose -f .\docker-compose.staging.yml down
```

### Production

Buat dan isi kedua file berikut pada host production. Jangan commit file ini
atau membagikan token dan passwordnya:

```powershell
Copy-Item .\backend\.env.production.example .\backend\.env.production
Copy-Item .\frontend\.env.production.example .\frontend\.env.production
```

Isi `backend/.env.production` dengan database production. Set
`ENABLE_PIPELINE=true` hanya bila scheduler memang diinginkan; atur
`PIPELINE_HOUR` dan `PIPELINE_MINUTE` sesuai timezone host/container. Pada
`frontend/.env.production`, gunakan `API_BASE_URL=http://backend:8000/api`
karena bot mengakses backend melalui jaringan Compose internal.

Start production:

```powershell
docker compose -f .\docker-compose.production.yml up --build -d
```

Periksa status dan log:

```powershell
docker compose -f .\docker-compose.production.yml ps
docker compose -f .\docker-compose.production.yml logs -f backend telegram-bot
```

Update image setelah perubahan kode dengan perintah yang sama (`up --build -d`).
Untuk menghentikan layanan tanpa menghapus konfigurasi:

```powershell
docker compose -f .\docker-compose.production.yml down
```

Sebelum deployment, validasi Compose dengan `docker compose ... config` dan
pastikan database dapat diakses dari host. Port `8000` hanya dibuka untuk API;
reverse proxy, TLS, firewall, dan SSH access control tetap menjadi tanggung
jawab infrastructure.
