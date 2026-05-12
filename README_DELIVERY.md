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
3.  **Git**
    *   [Unduh Git](https://git-scm.com/download/win)
    *   Diperlukan untuk menerima pembaruan aplikasi.

### 🚀 Instalasi (Lakukan Sekali Saja)

1.  Ekstrak folder proyek ke lokasi yang Anda inginkan (contoh: `C:\Aplikasi_Kasir`).
2.  Buka folder tersebut dan klik dua kali pada file **`setup.bat`**.
3.  Tunggu hingga skrip selesai menginstal semua dependensi dan menyiapkan database. Ini mungkin memakan waktu 2-5 menit tergantung kecepatan internet Anda.
4.  Setelah selesai, Anda akan melihat pesan "SETUP COMPLETE!".

### 💻 Menjalankan Aplikasi

1.  Untuk memulai aplikasi, klik dua kali pada file **`start.bat`**.
2.  Skrip akan memulai layanan backend dan frontend.
3.  Setelah beberapa detik, browser web Anda akan otomatis terbuka ke alamat `http://localhost:3000`.
4.  Di jendela `start.bat` Anda akan melihat dua alamat:
    ```
    Access from this PC:   http://localhost:3000
    Access from phone/PC:  http://192.168.x.x:3000
    ```
    Alamat kedua digunakan untuk akses dari perangkat lain (lihat bagian berikut).

### 📱 Akses dari Ponsel / Perangkat Lain

Aplikasi dapat dibuka dari ponsel, tablet, atau laptop lain selama terhubung ke **Wi-Fi yang sama** dengan komputer kasir.

1.  Pastikan komputer kasir dan ponsel terhubung ke jaringan Wi-Fi yang sama.
2.  Jalankan **`start.bat`** di komputer kasir.
3.  Perhatikan alamat yang tampil di jendela, contoh:
    ```
    Access from phone/PC:  http://192.168.1.5:3000
    ```
4.  Buka browser di ponsel dan ketik alamat tersebut.
5.  Aplikasi akan terbuka di ponsel — tampilan sudah dioptimalkan untuk layar kecil.

> **Catatan:** Alamat IP (`192.168.x.x`) dapat berubah jika router memberikan IP baru ke komputer.
> Jika akses dari ponsel tiba-tiba tidak bisa, jalankan kembali **`setup.bat`** lalu **`start.bat`**.
> `start.bat` akan memberikan peringatan otomatis jika IP berubah.

### 🔄 Memperbarui Aplikasi

Jika pengembang mengirimkan pembaruan:

1.  Pastikan komputer terhubung ke internet.
2.  Klik dua kali pada file **`update.bat`**.
3.  Tunggu hingga proses selesai — aplikasi akan diperbarui secara otomatis.
4.  Setelah selesai, jalankan kembali **`start.bat`** seperti biasa.

### ⚙️ Konfigurasi (Admin)

#### 1. Printer Termal (Thermal Printer)
*   Hubungkan printer Anda melalui USB dan instal driver printer.
*   Buka menu **SETTING** di dalam aplikasi.
*   Klik tombol **Scan** di kolom Printer Port — pilih nama printer dari daftar yang muncul.
*   Atur **Lebar Kertas** (58mm atau 80mm).

#### 2. Barcode Scanner
*   Pasang Barcode Scanner USB Anda.
*   Sistem membacanya sebagai input keyboard.
*   Pastikan kursor berada di kolom "Barcode" pada modul **KASIR**.

### 🗑️ Menghapus Aplikasi (Uninstall)

1.  Jika aplikasi sedang berjalan, tutup terlebih dahulu dengan menutup jendela **`start.bat`**.
2.  Hapus seluruh folder aplikasi (contoh: `C:\Aplikasi_Kasir`).
3.  Selesai — tidak ada file sistem atau registry yang perlu dihapus.

> **Catatan:** Python, Node.js, dan Git tidak ikut terhapus karena mungkin digunakan oleh aplikasi lain. Hapus secara manual melalui *Settings → Apps* jika tidak diperlukan lagi.

---

## 🇺🇸 ENGLISH VERSION

### 📋 Prerequisites

Before running the application, make sure you have the following installed:

1.  **Python 3.9 or newer**
    *   [Download Python](https://www.python.org/downloads/windows/)
    *   *Important:* During installation, check the box that says **"Add Python to PATH"**.
2.  **Node.js (LTS version)**
    *   [Download Node.js](https://nodejs.org/)
3.  **Git**
    *   [Download Git](https://git-scm.com/download/win)
    *   Required to receive application updates.

### 🚀 Installation (One-time Setup)

1.  Extract the project folder to your desired location (e.g., `C:\Cashier_App`).
2.  Open the folder and double-click **`setup.bat`**.
3.  Wait for the script to finish installing all dependencies and setting up the database. This might take 2-5 minutes depending on your internet speed.
4.  Once finished, you will see a "SETUP COMPLETE!" message.

### 💻 Running the App

1.  To start the application, double-click **`start.bat`**.
2.  The script will start the backend and frontend services.
3.  After a few seconds, your default web browser will automatically open to `http://localhost:3000`.
4.  The `start.bat` window will show two addresses:
    ```
    Access from this PC:   http://localhost:3000
    Access from phone/PC:  http://192.168.x.x:3000
    ```
    The second address is used to access the app from other devices (see below).

### 📱 Access from Phone / Other Devices

The app can be opened from a phone, tablet, or another laptop as long as it is connected to the **same Wi-Fi** as the cashier PC.

1.  Make sure the cashier PC and the phone are on the same Wi-Fi network.
2.  Run **`start.bat`** on the cashier PC.
3.  Note the address shown in the window, for example:
    ```
    Access from phone/PC:  http://192.168.1.5:3000
    ```
4.  Open a browser on the phone and type that address.
5.  The app will open on the phone — the layout is optimized for small screens.

> **Note:** The IP address (`192.168.x.x`) may change if the router assigns a new IP to the PC.
> If phone access suddenly stops working, re-run **`setup.bat`** and then **`start.bat`**.
> `start.bat` will automatically warn you if the IP has changed.

### 🔄 Updating the App

When the developer sends an update:

1.  Make sure the computer is connected to the internet.
2.  Double-click **`update.bat`**.
3.  Wait for the process to finish — the app will be updated automatically.
4.  Once done, run **`start.bat`** as usual.

### ⚙️ Configuration (Admin)

#### 1. Thermal Printer
*   Connect your printer via USB and install the printer driver.
*   Go to the **SETTING** menu in the app.
*   Click the **Scan** button next to Printer Port — select your printer name from the list.
*   Set the **Paper Width** (58mm or 80mm).

#### 2. Barcode Scanner
*   Plug in your USB Barcode Scanner.
*   The system treats it as keyboard input.
*   Ensure the cursor is in the "Barcode" field in the **KASIR** module.

### 🗑️ Uninstalling the App

1.  If the app is running, close it first by closing the **`start.bat`** window.
2.  Delete the entire app folder (e.g., `C:\Cashier_App`).
3.  Done — no system files or registry entries need to be removed.

> **Note:** Python, Node.js, and Git are not removed as they may be used by other applications. Uninstall them manually via *Settings → Apps* if no longer needed.

---
*Developed for Renal - 2026*
