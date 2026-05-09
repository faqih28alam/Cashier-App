# Panduan Pengiriman Aplikasi Kasir - Renal

Dokumen ini menjelaskan cara menginstal dan menjalankan Aplikasi Kasir di komputer Windows Anda.

---

## 🇮🇩 VERSI BAHASA INDONESIA

### 📋 Prasyarat

Sebelum menjalankan aplikasi, pastikan Anda telah menginstal hal-hal berikut:

1.  **Python 3.9 atau yang lebih baru**
    *   [Unduh Python](https://www.python.org/downloads/windows/)
    *   *Penting:* Saat instalasi, centang kotak yang bertuliskan **"Add Python to PATH"**.
2.  **Node.js (Versi LTS)**
    *   [Unduh Node.js](https://nodejs.org/)

### 🚀 Instalasi (Lakukan Sekali Saja)

1.  Ekstrak folder proyek ke lokasi yang Anda inginkan (contoh: `C:\Aplikasi_Kasir`).
2.  Buka folder tersebut dan klik dua kali pada file **`setup.bat`**.
3.  Tunggu hingga skrip selesai menginstal semua dependensi dan menyiapkan database. Ini mungkin memakan waktu 2-5 menit tergantung kecepatan internet Anda.
4.  Setelah selesai, Anda akan melihat pesan "SETUP COMPLETE!".

### 💻 Menjalankan Aplikasi

1.  Untuk memulai aplikasi, klik dua kali pada file **`start.bat`**.
2.  Skrip akan memulai layanan backend dan frontend.
3.  Setelah beberapa detik, browser web Anda akan otomatis terbuka ke alamat `http://localhost:3000`.

### ⚙️ Konfigurasi (Admin)

#### 1. Printer Termal (Thermal Printer)
*   Hubungkan printer Anda melalui USB atau Serial.
*   Buka menu **SETTING** di dalam aplikasi.
*   Konfigurasikan **Printer Port** (contoh: `COM3` di Windows).
*   Atur **Lebar Kertas** (58mm atau 80mm).

#### 2. Barcode Scanner
*   Pasang Barcode Scanner USB Anda.
*   Sistem membacanya sebagai input keyboard.
*   Pastikan kursor berada di kolom "Barcode" pada modul **KASIR**.

---

## 🇺🇸 ENGLISH VERSION

### 📋 Prerequisites

Before running the application, make sure you have the following installed:

1.  **Python 3.9 or newer**
    *   [Download Python](https://www.python.org/downloads/windows/)
    *   *Important:* During installation, check the box that says **"Add Python to PATH"**.
2.  **Node.js (LTS version)**
    *   [Download Node.js](https://nodejs.org/)

### 🚀 Installation (One-time Setup)

1.  Extract the project folder to your desired location (e.g., `C:\Cashier_App`).
2.  Open the folder and double-click **`setup.bat`**.
3.  Wait for the script to finish installing all dependencies and setting up the database. This might take 2-5 minutes depending on your internet speed.
4.  Once finished, you will see a "SETUP COMPLETE!" message.

### 💻 Running the App

1.  To start the application, double-click **`start.bat`**.
2.  The script will start the backend and frontend services.
3.  After a few seconds, your default web browser will automatically open to `http://localhost:3000`.

### ⚙️ Configuration (Admin)

#### 1. Thermal Printer
*   Connect your printer via USB or Serial.
*   Go to the **SETTING** menu in the app.
*   Configure the **Printer Port** (e.g., `COM3` on Windows).
*   Set the **Paper Width** (58mm or 80mm).

#### 2. Barcode Scanner
*   Plug in your USB Barcode Scanner.
*   The system treats it as keyboard input.
*   Ensure the cursor is in the "Barcode" field in the **KASIR** module.

---
*Developed for Renal - 2026*
