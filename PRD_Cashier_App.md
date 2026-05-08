# Product Requirements Document
## Cashier Application (Point of Sale System)

**Project Name:** Cashier App — Renal  
**Version:** 1.0  
**Date:** 2026-05-08  
**Reference UI:** Sangkasir Solutions / Repstart System

---

## 1. Overview

A desktop-based Point of Sale (POS) system for retail stores. The system manages cashier transactions, purchasing, finance, product master data, and reporting. It integrates with a **barcode scanner** to scan products and a **thermal printer** to print receipts.

---

## 2. Goals

- Speed up cashier transactions by scanning barcodes instead of manual entry
- Support tiered pricing (quantity-based discounts)
- Accurately record transactions, purchases, and cash flow
- Provide reports for business monitoring
- Print receipts instantly via thermal printer

---

## 3. System Modules

| Module | Description |
|---|---|
| **KASIR** | Point of sale — scan, add items, process payment, print receipt |
| **PURCHAS** | Record and manage incoming stock/purchases from suppliers |
| **KEUANGAN** | Finance — track income, expenses, and cash balance |
| **LAPORAN** | Reports — sales, product, finance summaries |
| **MASTER** | Master data — products, suppliers, users, categories |
| **SETTING** | Application configuration — store info, printer, scanner |

---

## 4. User Roles

| Role | Access |
|---|---|
| **Kasir (Cashier)** | KASIR module only |
| **Admin** | All modules |
| **Owner** | All modules + financial reports |

---

## 5. Hardware Requirements

### 5.1 Barcode Scanner
- USB or serial barcode scanner (HID keyboard mode)
- Triggered automatically on the POS screen — scanned barcode is matched against product master data
- If barcode is found → product is added to the transaction table
- If barcode is not found → show error notification

### 5.2 Thermal Printer
- ESC/POS compatible thermal receipt printer
- Connected via USB or serial port
- Configured in SETTING module (port, baud rate)
- Triggered automatically after payment is confirmed
- Receipt width: 58mm or 80mm (configurable)

---

## 6. Functional Requirements

### 6.1 Authentication & Session Management

**Login**
- User logs in with username and password
- System records login time and active cashier name

**Session Screen (on opening POS)**
- Option 1: **Mulai Baru** — Start a fresh transaction (clears previous held state)
- Option 2: **Lanjutkan Transaksi** — Resume a previously held/paused transaction

**Logout**
- LOGOFF button in the main menu
- Prompts confirmation before logging out
- Unsaved/open transactions should be held or warned

---

### 6.2 KASIR — Point of Sale

This is the primary module used by cashiers for daily transactions.

#### 6.2.1 POS Main Screen Layout

```
+-----------------------------------------------------------------------+
| [KASIR] [PURCHAS] [KEUANGAN] [LAPORAN] [MASTER] [SETTING] [LOGOFF]   |
+-------------------------------------------------------+---------------+
| Transaction Table                                     | Action Panel  |
|                                                       |               |
| NO | Nama Barang | SAT | QTY | HPP | Harga | Diskon | Total | Ket   |
|----|-------------|-----|-----|-----|-------|--------|-------|-------|
|    |             |     |     |     |       |        |       |       |
|                                                       | [Delete]      |
|                                                       | [Edit Qty]    |
|                                                       | [Discount]    |
|                                                       | [Hold]        |
|                                                       | [Cancel Row]  |
|                                                       | [Clear All]   |
|                                                       | ...           |
+-------------------------------------------------------+               |
| [Barcode Input Field] [Scanner Icon] [Keyboard Icon]  |               |
|                                        TRANSAKSI: 0   |               |
|                                                       | [BAYAR]       |
+-----------------------------------------------------------------------+
|                        POINT OF SALE                                  |
+-----------------------------------------------------------------------+
```

#### 6.2.2 Transaction Table Columns

| Column | Description |
|---|---|
| NO | Row number |
| Nama Barang | Product name (from master data) |
| SAT | Unit (PCS, BOX, KG, etc.) |
| QTY | Quantity (editable via numpad popup) |
| HPP | Cost price (Harga Pokok Penjualan) |
| Harga | Selling price (auto-selected based on qty tier) |
| Diskon | Discount amount or percentage |
| Total | QTY × Harga − Diskon |
| Keterangan | Notes (optional) |

#### 6.2.3 Adding Items

**Via Barcode Scanner:**
1. Cashier focuses the barcode input field (auto-focused by default)
2. Scanner reads barcode → system looks up product in master data
3. If found → product row is added to the transaction table with QTY = 1
4. If already in table → QTY increments by 1
5. If not found → show error: "Barcode tidak ditemukan"

**Via Manual Barcode Entry:**
1. Cashier types barcode manually into the input field and presses Enter
2. Same lookup logic as scanner

#### 6.2.4 Quantity Input (Numpad Popup)

- Triggered by clicking a row's QTY cell or pressing a shortcut key
- Popup displays:
  - Product name
  - Current quantity with unit (e.g., "5 PCS")
  - Numpad: 1–9, 0, 00, backspace, confirm (✓), cancel (✗)
- Confirms on Enter or ✓ button
- QTY update triggers automatic price tier recalculation

#### 6.2.5 Tiered Pricing (Harga Bertingkat)

Prices are automatically selected based on quantity:

| Tier | Condition | Price Used |
|---|---|---|
| Harga 1 | Default (QTY = 1) | Standard price |
| Harga 2 | QTY > threshold 2 (e.g., > 5) | Discounted price |
| Harga 3 | QTY > threshold 3 (e.g., > 10) | Further discounted price |

- Thresholds are configured per product in MASTER
- When QTY changes, the price tier recalculates automatically

#### 6.2.6 Transaction Summary

- Bottom of the screen shows running **TRANSAKSI** total
- Updates in real time as items are added, removed, or quantities change

#### 6.2.7 Action Panel (Right Sidebar)

| Button | Action |
|---|---|
| Delete | Remove selected row from transaction |
| Edit Qty | Open numpad popup for selected row |
| Discount | Apply discount to selected row |
| Hold | Pause current transaction (save for later) |
| Cancel / Clear | Cancel entire transaction |
| BAYAR | Proceed to payment |

---

#### 6.2.8 Payment Screen (Pembayaran)

Opened when cashier clicks **BAYAR**.

```
+--------------------------------------------+------------------+
| Total Transaksi: 188,000                   |  PEMBAYARAN      |
|                                            |                  |
| [50K]  [100K]  [200K]  [500K]  [1000K]    |  [1]  [2]  [3]  |
|                                [BAYAR PCS] |  [4]  [5]  [6]  |
|                                            |  [7]  [8]  [9]  |
| Bayar: [  200,000  ]                       |  [0]  [00] [←]  |
|                                            |                  |
| Kembalian: 12,000                          |                  |
|                                            |                  |
| [  KONFIRMASI  ]           [  X  ]         |                  |
+--------------------------------------------+------------------+
```

**Fields:**
- **Total Transaksi** — calculated transaction total (read-only)
- **Quick denomination buttons** — 50K, 100K, 200K, 500K, 1000K (sets the Bayar field)
- **BAYAR PCS** — pay exact amount (sets Bayar = Total)
- **Bayar** — cash input field (editable via numpad or keyboard)
- **Kembalian** — change = Bayar − Total (auto-calculated, real-time)
- **KONFIRMASI** — confirm payment (only enabled if Bayar ≥ Total)
- **X** — cancel, return to POS screen

**Validation:**
- Cannot confirm if Bayar < Total
- Kembalian is always ≥ 0

---

#### 6.2.9 Receipt Flow

After KONFIRMASI:
1. System saves the transaction to the database
2. Receipt preview popup is shown on screen:
   - Store name, address, phone
   - Date and time
   - Cashier name
   - List of items: name, QTY, unit price, total
   - Subtotal
   - Cash paid (Bayar)
   - Change (Kembalian)
3. System sends print job to thermal printer automatically
4. After print: popup closes, POS screen resets for next transaction

**Receipt Content:**
```
================================
       SANGKASIR SOLUTIONS
       Jl. [Alamat Toko]
       Telp: [No. Telp]
================================
No. Transaksi : TRX-20210210-001
Tanggal       : 10-Feb-2021 10:30
Kasir         : [Nama Kasir]
--------------------------------
Djarum Super 12
  5 PCS x 19,000      95,000
[Item 2...]
--------------------------------
Total                 188,000
Bayar                 200,000
Kembalian              12,000
================================
     Terima Kasih!
================================
```

---

### 6.3 PURCHAS — Purchasing Module

Manages incoming goods from suppliers.

**Features:**
- Record purchase transactions (supplier, date, items, qty, cost)
- Update stock quantities in master data upon purchase confirmation
- Purchase history list with filter by date/supplier

**Purchase Form Fields:**
- No. Faktur (Invoice number)
- Tanggal (Date)
- Supplier
- Items table: Barcode, Nama Barang, SAT, QTY, HPP (cost price)
- Total purchase value
- Status (Draft / Confirmed)

---

### 6.4 KEUANGAN — Finance Module

Tracks cash flow and financial position.

**Features:**
- Record income from sales (auto-posted from KASIR)
- Record manual expenses (operational costs)
- Cash balance summary
- Daily/monthly cash recap

**Data:**
- Tanggal, Keterangan, Debit (in), Kredit (out), Saldo (balance)

---

### 6.5 LAPORAN — Reports Module

**Available Reports:**

| Report | Description |
|---|---|
| Data Barang | Product list with HPP and all price tiers |
| Laporan Penjualan | Sales summary by date range |
| Laporan Stok | Current stock levels per product |
| Laporan Transaksi | Transaction detail log |
| Laporan Keuangan | Income and expense summary |

**Report Filters:** Date range, category, cashier

**Report Output:**
- Displayed on screen in a table
- Printable via thermal or regular printer

**Data Barang Report columns:**
- NO, Barcode, Nama Barang, SAT, HPP, Harga 1, Harga 2 (condition + price), Harga 3 (condition + price)

---

### 6.6 MASTER — Master Data Module

#### 6.6.1 Product Master (Barang)

| Field | Description |
|---|---|
| Barcode | Unique product barcode |
| Nama Barang | Product name |
| Kategori | Category |
| SAT | Unit (PCS, BOX, KG, etc.) |
| HPP | Cost price |
| Harga 1 | Standard selling price |
| Harga 2 | Price tier 2 (with min qty threshold) |
| Harga 3 | Price tier 3 (with min qty threshold) |
| Stok | Current stock quantity |
| Stok Minimum | Alert threshold for low stock |

**Actions:** Add, Edit, Delete, Search by name/barcode, filter by category

#### 6.6.2 Supplier Master

| Field | Description |
|---|---|
| Kode Supplier | Supplier code |
| Nama Supplier | Supplier name |
| Alamat | Address |
| Telepon | Phone number |
| Kontak | Contact person |

#### 6.6.3 Kategori (Category)

- Simple list: Kode Kategori, Nama Kategori
- Used for product grouping and report filtering

#### 6.6.4 User Management

| Field | Description |
|---|---|
| Username | Login username |
| Password | Hashed password |
| Nama | Full name |
| Role | Kasir / Admin / Owner |
| Status | Active / Inactive |

---

### 6.7 SETTING — Configuration Module

| Setting | Description |
|---|---|
| Nama Toko | Store name (printed on receipt) |
| Alamat | Store address |
| Telepon | Store phone |
| Logo | Store logo for receipt |
| Printer Port | Serial/USB port for thermal printer |
| Printer Width | 58mm or 80mm paper |
| Scanner Mode | USB HID / Serial |
| Receipt Footer | Custom footer text (e.g., "Terima Kasih!") |
| Tax | Tax rate (%) — optional |

---

## 7. System Flow

### 7.1 POS Transaction Flow

```
[Login] 
   ↓
[Session Screen]
   ├── Mulai Baru → Clear transaction → [POS Main Screen]
   └── Lanjutkan Transaksi → Load held transaction → [POS Main Screen]
         ↓
[Scan Barcode / Manual Entry]
   ├── Barcode found → Add/update item in table
   └── Barcode not found → Show error
         ↓
[Adjust QTY via Numpad Popup]
   └── Price tier recalculates automatically
         ↓
[Apply Discount (optional)]
         ↓
[BAYAR → Payment Screen]
   ├── Select denomination / enter cash amount
   ├── Change auto-calculated
   └── KONFIRMASI (if Bayar ≥ Total)
         ↓
[Save Transaction to DB]
         ↓
[Print Receipt to Thermal Printer]
         ↓
[POS resets for next transaction]
```

### 7.2 Scanner Integration Flow

```
[Scanner reads barcode]
   ↓
[Barcode sent as keyboard input to active input field]
   ↓
[System queries product master by barcode]
   ├── Found → Add to transaction table (QTY = 1, or increment if exists)
   │           → Apply Harga 1 as default price
   │           → Update running total
   └── Not found → Display error toast: "Barcode [xxxx] tidak ditemukan"
```

### 7.3 Printer Integration Flow

```
[Payment confirmed]
   ↓
[Build receipt data (store info + items + totals)]
   ↓
[Send ESC/POS commands to configured printer port]
   ↓
[Printer outputs thermal receipt]
   ↓
[Show receipt preview on screen simultaneously]
   ↓
[Optionally: reprint button available in transaction history]
```

---

## 8. Data Models

### Transaction (Header)
```
- id_transaksi     : PK
- no_transaksi     : unique (e.g., TRX-20210210-001)
- tanggal          : datetime
- id_user          : FK → User
- total            : decimal
- bayar            : decimal
- kembalian        : decimal
- status           : enum (open, paid, cancelled)
```

### Transaction Detail (Items)
```
- id_detail        : PK
- id_transaksi     : FK → Transaction
- barcode          : string
- nama_barang      : string (snapshot)
- sat              : string
- qty              : decimal
- hpp              : decimal
- harga            : decimal
- diskon           : decimal
- total            : decimal
```

### Product (Barang)
```
- barcode          : PK
- nama_barang      : string
- id_kategori      : FK → Kategori
- sat              : string
- hpp              : decimal
- harga_1          : decimal
- harga_2          : decimal
- min_qty_harga_2  : int
- harga_3          : decimal
- min_qty_harga_3  : int
- stok             : decimal
- stok_minimum     : decimal
```

### Purchase (Header)
```
- id_pembelian     : PK
- no_faktur        : string
- tanggal          : datetime
- id_supplier      : FK → Supplier
- total            : decimal
- status           : enum (draft, confirmed)
```

### Purchase Detail
```
- id_detail        : PK
- id_pembelian     : FK → Purchase
- barcode          : FK → Product
- qty              : decimal
- hpp              : decimal
- total            : decimal
```

---

## 9. Non-Functional Requirements

| Aspect | Requirement |
|---|---|
| **Platform** | Desktop application (Windows) |
| **Response time** | Barcode lookup < 200ms |
| **Offline** | Fully functional without internet (local database) |
| **Database** | Local DB (SQLite or MySQL local) |
| **Reliability** | No data loss on power failure — transactions must be committed before receipt prints |
| **Usability** | Numpad-friendly UI; operable with mouse, keyboard, or touchscreen |
| **Security** | Role-based access control; passwords hashed |
| **Backup** | Data export/backup feature in SETTING |
| **Printer** | ESC/POS protocol support; graceful error if printer offline |
| **Scanner** | Works in HID mode (plug-and-play, no driver needed) |

---

## 10. Out of Scope (v1.0)

- Online/cloud sync
- Multi-branch support
- E-receipt (email/WhatsApp)
- Loyalty/points system
- Credit card / QRIS payment integration
- Mobile app

---

*Document generated from UI reference: UI_Reference.pdf / UI_Reference.docx (Sangkasir Solutions / Repstart System)*
