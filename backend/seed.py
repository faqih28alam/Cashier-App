from datetime import datetime, timedelta
from database import SessionLocal
from models.user import User
from models.kategori import Kategori
from models.supplier import Supplier
from models.barang import Barang
from models.setting import Setting
from models.pembelian import Pembelian, PembelianDetail
from models.transaksi import Transaksi, TransaksiDetail
from models.keuangan import Keuangan
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()


def seed(model, unique_field, rows):
    created = 0
    for row in rows:
        if not db.query(model).filter(getattr(model, unique_field) == row[unique_field]).first():
            db.add(model(**row))
            created += 1
    db.flush()
    print(f"{model.__tablename__}: {created} created, {len(rows)-created} skipped")


# ── Users ──────────────────────────────────────────────────────────────────────
USERS = [
    {"username": "admin",  "password": "admin123",  "nama": "Administrator", "role": "owner",  "is_active": True},
    {"username": "kasir1", "password": "kasir123",  "nama": "Budi Santoso",  "role": "kasir",  "is_active": True},
    {"username": "kasir2", "password": "kasir123",  "nama": "Siti Rahayu",   "role": "kasir",  "is_active": True},
    {"username": "manager","password": "manager123","nama": "Andi Wijaya",   "role": "admin",  "is_active": True},
]
for u in USERS:
    if not db.query(User).filter(User.username == u["username"]).first():
        db.add(User(username=u["username"], password=pwd.hash(u["password"]),
                    nama=u["nama"], role=u["role"], is_active=u["is_active"]))
        print(f"  + user: {u['username']} / {u['password']} ({u['role']})")
    else:
        print(f"  ~ user: {u['username']} already exists")
db.flush()

# ── Kategori ───────────────────────────────────────────────────────────────────
seed(Kategori, "kode_kategori", [
    {"kode_kategori": "MIN", "nama_kategori": "Minuman"},
    {"kode_kategori": "MAK", "nama_kategori": "Makanan"},
    {"kode_kategori": "SNK", "nama_kategori": "Snack & Cemilan"},
    {"kode_kategori": "ROK", "nama_kategori": "Rokok"},
    {"kode_kategori": "KEB", "nama_kategori": "Kebersihan & Perawatan"},
    {"kode_kategori": "ATK", "nama_kategori": "Alat Tulis"},
    {"kode_kategori": "LBK", "nama_kategori": "Lain-lain"},
])

# ── Supplier ───────────────────────────────────────────────────────────────────
seed(Supplier, "kode_supplier", [
    {"kode_supplier": "SUP-001", "nama_supplier": "PT Indo Distributor Utama",
     "alamat": "Jl. Gatot Subroto No. 45, Jakarta Selatan", "telepon": "021-5551234", "kontak": "Pak Hendra"},
    {"kode_supplier": "SUP-002", "nama_supplier": "CV Sumber Makmur Jaya",
     "alamat": "Jl. Raya Bogor Km. 28, Depok", "telepon": "021-7782345", "kontak": "Bu Wati"},
    {"kode_supplier": "SUP-003", "nama_supplier": "UD Bintang Sejahtera",
     "alamat": "Jl. Pahlawan No. 12, Bekasi", "telepon": "021-8843456", "kontak": "Pak Dedi"},
])

# ── Setting (singleton row id=1) ───────────────────────────────────────────────
if not db.get(Setting, 1):
    db.add(Setting(
        id=1,
        nama_toko="Toko Renal",
        alamat="Jl. Merdeka No. 7, Kelurahan Sukamaju, Kota Bekasi",
        telepon="0812-3456-7890",
        printer_port="",
        printer_width=80,
        receipt_footer="Terima kasih telah berbelanja!\nBarang yang sudah dibeli tidak dapat dikembalikan.",
        tax_rate=0,
    ))
    print("setting: 1 created")
else:
    print("setting: already exists, skipped")
db.flush()

# ── Barang ─────────────────────────────────────────────────────────────────────
kat = {k.kode_kategori: k.id for k in db.query(Kategori).all()}

BARANG = [
    # Minuman
    {"barcode": "8998866900307", "nama_barang": "Aqua 600ml",           "id_kategori": kat["MIN"], "sat": "BTL", "hpp": 2500,  "harga_1": 3500,  "harga_2": 3300,  "min_qty_harga_2": 12, "harga_3": 3000,  "min_qty_harga_3": 24, "stok": 120, "stok_minimum": 24},
    {"barcode": "8998866900406", "nama_barang": "Aqua 1500ml",          "id_kategori": kat["MIN"], "sat": "BTL", "hpp": 4500,  "harga_1": 6000,  "harga_2": 5700,  "min_qty_harga_2": 6,  "harga_3": 5500,  "min_qty_harga_3": 12, "stok": 60,  "stok_minimum": 12},
    {"barcode": "8999999045555", "nama_barang": "Teh Botol Sosro 450ml","id_kategori": kat["MIN"], "sat": "BTL", "hpp": 3500,  "harga_1": 5000,  "harga_2": 4700,  "min_qty_harga_2": 12, "harga_3": 4500,  "min_qty_harga_3": 24, "stok": 96,  "stok_minimum": 24},
    {"barcode": "8888001122334", "nama_barang": "Coca-Cola 390ml",      "id_kategori": kat["MIN"], "sat": "BTL", "hpp": 5000,  "harga_1": 7000,  "harga_2": 6500,  "min_qty_harga_2": 12, "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 48,  "stok_minimum": 12},
    {"barcode": "8997013011150", "nama_barang": "Indomilk 115ml",       "id_kategori": kat["MIN"], "sat": "PCS", "hpp": 2000,  "harga_1": 3000,  "harga_2": 2800,  "min_qty_harga_2": 10, "harga_3": 2500,  "min_qty_harga_3": 20, "stok": 80,  "stok_minimum": 20},
    {"barcode": "8886468100032", "nama_barang": "Pocari Sweat 500ml",   "id_kategori": kat["MIN"], "sat": "BTL", "hpp": 7000,  "harga_1": 9500,  "harga_2": 9000,  "min_qty_harga_2": 6,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 36,  "stok_minimum": 12},
    # Makanan
    {"barcode": "8999999011111", "nama_barang": "Indomie Goreng",       "id_kategori": kat["MAK"], "sat": "PCS", "hpp": 2800,  "harga_1": 3500,  "harga_2": 3300,  "min_qty_harga_2": 5,  "harga_3": 3000,  "min_qty_harga_3": 40, "stok": 200, "stok_minimum": 40},
    {"barcode": "8999999022222", "nama_barang": "Indomie Soto",         "id_kategori": kat["MAK"], "sat": "PCS", "hpp": 2800,  "harga_1": 3500,  "harga_2": 3300,  "min_qty_harga_2": 5,  "harga_3": 3000,  "min_qty_harga_3": 40, "stok": 180, "stok_minimum": 40},
    {"barcode": "8991101020000", "nama_barang": "Biscuit Roma Kelapa",  "id_kategori": kat["MAK"], "sat": "PCS", "hpp": 4500,  "harga_1": 6000,  "harga_2": 5700,  "min_qty_harga_2": 6,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 60,  "stok_minimum": 12},
    {"barcode": "8992388011234", "nama_barang": "Roti Tawar Sari Roti", "id_kategori": kat["MAK"], "sat": "PCS", "hpp": 12000, "harga_1": 15000, "harga_2": 14000, "min_qty_harga_2": 5,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 30,  "stok_minimum": 10},
    # Snack
    {"barcode": "8999999033333", "nama_barang": "Chitato 68gr",         "id_kategori": kat["SNK"], "sat": "PCS", "hpp": 8000,  "harga_1": 11000, "harga_2": 10500, "min_qty_harga_2": 5,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 72,  "stok_minimum": 12},
    {"barcode": "8991101044444", "nama_barang": "Taro 70gr",            "id_kategori": kat["SNK"], "sat": "PCS", "hpp": 6500,  "harga_1": 9000,  "harga_2": 8500,  "min_qty_harga_2": 5,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 60,  "stok_minimum": 12},
    {"barcode": "8999999055555", "nama_barang": "Richeese Nabati 145gr","id_kategori": kat["SNK"], "sat": "PCS", "hpp": 10000, "harga_1": 14000, "harga_2": 13000, "min_qty_harga_2": 5,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 48,  "stok_minimum": 12},
    {"barcode": "8997210123456", "nama_barang": "Oreo Original 119gr",  "id_kategori": kat["SNK"], "sat": "PCS", "hpp": 10500, "harga_1": 14000, "harga_2": 13500, "min_qty_harga_2": 5,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 40,  "stok_minimum": 10},
    # Rokok
    {"barcode": "8992788000016", "nama_barang": "Gudang Garam Merah",   "id_kategori": kat["ROK"], "sat": "BKS", "hpp": 23000, "harga_1": 27000, "harga_2": 26500, "min_qty_harga_2": 10, "harga_3": 26000, "min_qty_harga_3": 20, "stok": 100, "stok_minimum": 20},
    {"barcode": "8992788000023", "nama_barang": "Surya 12",             "id_kategori": kat["ROK"], "sat": "BKS", "hpp": 22000, "harga_1": 26000, "harga_2": 25500, "min_qty_harga_2": 10, "harga_3": 25000, "min_qty_harga_3": 20, "stok": 80,  "stok_minimum": 20},
    {"barcode": "8998007300016", "nama_barang": "Djarum Super 16",      "id_kategori": kat["ROK"], "sat": "BKS", "hpp": 24000, "harga_1": 28000, "harga_2": 27500, "min_qty_harga_2": 10, "harga_3": 27000, "min_qty_harga_3": 20, "stok": 60,  "stok_minimum": 20},
    # Kebersihan
    {"barcode": "8996001300016", "nama_barang": "Sabun Lifebuoy 85gr",  "id_kategori": kat["KEB"], "sat": "PCS", "hpp": 4000,  "harga_1": 6000,  "harga_2": 5700,  "min_qty_harga_2": 6,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 50,  "stok_minimum": 10},
    {"barcode": "8999999066666", "nama_barang": "Shampoo Sunsilk 70ml", "id_kategori": kat["KEB"], "sat": "PCS", "hpp": 5500,  "harga_1": 8000,  "harga_2": 7500,  "min_qty_harga_2": 6,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 40,  "stok_minimum": 10},
    {"barcode": "8887290000111", "nama_barang": "Rinso 900gr",          "id_kategori": kat["KEB"], "sat": "PCS", "hpp": 20000, "harga_1": 25000, "harga_2": 24000, "min_qty_harga_2": 3,  "harga_3": 0,     "min_qty_harga_3": 0,  "stok": 30,  "stok_minimum": 10},
    # Alat Tulis
    {"barcode": "9999990011111", "nama_barang": "Pulpen Pilot 0.7mm",   "id_kategori": kat["ATK"], "sat": "PCS", "hpp": 5000,  "harga_1": 7000,  "harga_2": 6500,  "min_qty_harga_2": 5,  "harga_3": 6000,  "min_qty_harga_3": 10, "stok": 50,  "stok_minimum": 10},
    {"barcode": "9999990022222", "nama_barang": "Buku Tulis 58 Lembar", "id_kategori": kat["ATK"], "sat": "PCS", "hpp": 5500,  "harga_1": 8000,  "harga_2": 7500,  "min_qty_harga_2": 5,  "harga_3": 7000,  "min_qty_harga_3": 10, "stok": 40,  "stok_minimum": 10},
]

created_barang = 0
for b in BARANG:
    if not db.get(Barang, b["barcode"]):
        db.add(Barang(**b))
        created_barang += 1
db.flush()
print(f"barang: {created_barang} created, {len(BARANG)-created_barang} skipped")

# ── Pembelian (2 purchase orders) ──────────────────────────────────────────────
sup = {s.kode_supplier: s.id for s in db.query(Supplier).all()}
today = datetime.now()

if not db.query(Pembelian).filter(Pembelian.no_faktur == "PO-20260501-001").first():
    p1 = Pembelian(
        no_faktur="PO-20260501-001",
        tanggal=today - timedelta(days=7),
        id_supplier=sup["SUP-001"],
        total=0,
        status="confirmed",
    )
    db.add(p1)
    db.flush()

    p1_detail = [
        {"barcode": "8998866900307", "nama_barang": "Aqua 600ml",        "sat": "BTL", "qty": 48, "hpp": 2500, "total": 48*2500},
        {"barcode": "8999999011111", "nama_barang": "Indomie Goreng",     "sat": "PCS", "qty": 80, "hpp": 2800, "total": 80*2800},
        {"barcode": "8999999022222", "nama_barang": "Indomie Soto",       "sat": "PCS", "qty": 80, "hpp": 2800, "total": 80*2800},
        {"barcode": "8992788000016", "nama_barang": "Gudang Garam Merah", "sat": "BKS", "qty": 50, "hpp": 23000,"total": 50*23000},
        {"barcode": "8999999033333", "nama_barang": "Chitato 68gr",       "sat": "PCS", "qty": 36, "hpp": 8000, "total": 36*8000},
    ]
    total1 = sum(d["total"] for d in p1_detail)
    for d in p1_detail:
        db.add(PembelianDetail(id_pembelian=p1.id, **d))
    p1.total = total1

    # keuangan entry for confirmed purchase
    db.add(Keuangan(
        tanggal=today - timedelta(days=7),
        keterangan="Pembelian PO-20260501-001 — PT Indo Distributor Utama",
        debit=0, kredit=total1, ref_type="pembelian", ref_id=p1.id,
    ))
    print(f"pembelian: PO-20260501-001 created (confirmed, Rp {total1:,.0f})")

if not db.query(Pembelian).filter(Pembelian.no_faktur == "PO-20260507-001").first():
    p2 = Pembelian(
        no_faktur="PO-20260507-001",
        tanggal=today - timedelta(days=1),
        id_supplier=sup["SUP-002"],
        total=0,
        status="draft",
    )
    db.add(p2)
    db.flush()

    p2_detail = [
        {"barcode": "8999999045555", "nama_barang": "Teh Botol Sosro 450ml", "sat": "BTL", "qty": 24, "hpp": 3500,  "total": 24*3500},
        {"barcode": "8886468100032", "nama_barang": "Pocari Sweat 500ml",    "sat": "BTL", "qty": 12, "hpp": 7000,  "total": 12*7000},
        {"barcode": "8996001300016", "nama_barang": "Sabun Lifebuoy 85gr",   "sat": "PCS", "qty": 20, "hpp": 4000,  "total": 20*4000},
        {"barcode": "8887290000111", "nama_barang": "Rinso 900gr",           "sat": "PCS", "qty": 10, "hpp": 20000, "total": 10*20000},
    ]
    total2 = sum(d["total"] for d in p2_detail)
    for d in p2_detail:
        db.add(PembelianDetail(id_pembelian=p2.id, **d))
    p2.total = total2
    print(f"pembelian: PO-20260507-001 created (draft, Rp {total2:,.0f})")

db.flush()

# ── Transaksi ──────────────────────────────────────────────────────────────────
kasir_user = db.query(User).filter(User.username == "kasir1").first()
owner_user = db.query(User).filter(User.username == "admin").first()

TRX = [
    {
        "no_transaksi": "TRX-20260506-001",
        "tanggal": today - timedelta(days=2, hours=3),
        "id_user": kasir_user.id,
        "bayar": 50000,
        "status": "paid",
        "detail": [
            {"barcode": "8998866900307", "nama_barang": "Aqua 600ml",    "sat": "BTL", "qty": 3,  "hpp": 2500,  "harga": 3500,  "diskon": 0, "total": 3*3500},
            {"barcode": "8999999011111", "nama_barang": "Indomie Goreng", "sat": "PCS", "qty": 5,  "hpp": 2800,  "harga": 3300,  "diskon": 0, "total": 5*3300},
            {"barcode": "8999999033333", "nama_barang": "Chitato 68gr",  "sat": "PCS", "qty": 1,  "hpp": 8000,  "harga": 11000, "diskon": 0, "total": 11000},
        ],
    },
    {
        "no_transaksi": "TRX-20260506-002",
        "tanggal": today - timedelta(days=2, hours=1),
        "id_user": kasir_user.id,
        "bayar": 100000,
        "status": "paid",
        "detail": [
            {"barcode": "8992788000016", "nama_barang": "Gudang Garam Merah", "sat": "BKS", "qty": 2,  "hpp": 23000, "harga": 27000, "diskon": 0,    "total": 2*27000},
            {"barcode": "8998866900307", "nama_barang": "Aqua 600ml",         "sat": "BTL", "qty": 2,  "hpp": 2500,  "harga": 3500,  "diskon": 0,    "total": 2*3500},
            {"barcode": "8999999045555", "nama_barang": "Teh Botol Sosro",    "sat": "BTL", "qty": 3,  "hpp": 3500,  "harga": 5000,  "diskon": 1000, "total": 3*5000-1000},
        ],
    },
    {
        "no_transaksi": "TRX-20260507-001",
        "tanggal": today - timedelta(days=1, hours=5),
        "id_user": kasir_user.id,
        "bayar": 200000,
        "status": "paid",
        "detail": [
            {"barcode": "8999999011111", "nama_barang": "Indomie Goreng",      "sat": "PCS", "qty": 40, "hpp": 2800, "harga": 3000,  "diskon": 0, "total": 40*3000},
            {"barcode": "8999999022222", "nama_barang": "Indomie Soto",        "sat": "PCS", "qty": 10, "hpp": 2800, "harga": 3300,  "diskon": 0, "total": 10*3300},
            {"barcode": "8991101020000", "nama_barang": "Biscuit Roma Kelapa", "sat": "PCS", "qty": 3,  "hpp": 4500, "harga": 6000,  "diskon": 0, "total": 3*6000},
        ],
    },
    {
        "no_transaksi": "TRX-20260507-002",
        "tanggal": today - timedelta(days=1, hours=2),
        "id_user": kasir_user.id,
        "bayar": 80000,
        "status": "paid",
        "detail": [
            {"barcode": "8886468100032", "nama_barang": "Pocari Sweat 500ml",   "sat": "BTL", "qty": 4,  "hpp": 7000,  "harga": 9500,  "diskon": 0, "total": 4*9500},
            {"barcode": "8997210123456", "nama_barang": "Oreo Original 119gr",  "sat": "PCS", "qty": 2,  "hpp": 10500, "harga": 14000, "diskon": 0, "total": 2*14000},
            {"barcode": "9999990011111", "nama_barang": "Pulpen Pilot 0.7mm",   "sat": "PCS", "qty": 2,  "hpp": 5000,  "harga": 7000,  "diskon": 0, "total": 2*7000},
        ],
    },
    {
        "no_transaksi": "TRX-20260508-001",
        "tanggal": today - timedelta(hours=2),
        "id_user": kasir_user.id,
        "bayar": 50000,
        "status": "paid",
        "detail": [
            {"barcode": "8992788000023", "nama_barang": "Surya 12",        "sat": "BKS", "qty": 1,  "hpp": 22000, "harga": 26000, "diskon": 0, "total": 26000},
            {"barcode": "8998866900307", "nama_barang": "Aqua 600ml",      "sat": "BTL", "qty": 2,  "hpp": 2500,  "harga": 3500,  "diskon": 0, "total": 2*3500},
            {"barcode": "8999999055555", "nama_barang": "Richeese Nabati", "sat": "PCS", "qty": 1,  "hpp": 10000, "harga": 14000, "diskon": 0, "total": 14000},
        ],
    },
]

trx_created = 0
for t in TRX:
    if db.query(Transaksi).filter(Transaksi.no_transaksi == t["no_transaksi"]).first():
        continue
    detail = t.pop("detail")
    total = sum(d["total"] for d in detail)
    kembalian = t["bayar"] - total
    trx = Transaksi(**t, total=total, kembalian=kembalian)
    db.add(trx)
    db.flush()
    for d in detail:
        db.add(TransaksiDetail(id_transaksi=trx.id, **d))
    db.add(Keuangan(
        tanggal=trx.tanggal,
        keterangan=f"Penjualan {trx.no_transaksi}",
        debit=total, kredit=0, ref_type="transaksi", ref_id=trx.id,
    ))
    trx_created += 1

db.flush()
print(f"transaksi: {trx_created} created, {len(TRX)-trx_created} skipped")

# ── Keuangan — manual operational entries ──────────────────────────────────────
MANUAL_KAS = [
    {"tanggal": today - timedelta(days=5), "keterangan": "Saldo awal toko",        "debit": 5000000, "kredit": 0,      "ref_type": "manual", "ref_id": None},
    {"tanggal": today - timedelta(days=4), "keterangan": "Biaya listrik April",    "debit": 0,       "kredit": 350000, "ref_type": "manual", "ref_id": None},
    {"tanggal": today - timedelta(days=3), "keterangan": "Biaya sewa toko bulan ini","debit": 0,     "kredit": 1500000,"ref_type": "manual", "ref_id": None},
    {"tanggal": today - timedelta(days=2), "keterangan": "Gaji karyawan minggu ini","debit": 0,      "kredit": 800000, "ref_type": "manual", "ref_id": None},
]

kas_created = 0
for k in MANUAL_KAS:
    existing = db.query(Keuangan).filter(
        Keuangan.keterangan == k["keterangan"],
        Keuangan.ref_type == "manual",
    ).first()
    if not existing:
        db.add(Keuangan(**k))
        kas_created += 1

print(f"keuangan manual: {kas_created} created")

# ── Commit ─────────────────────────────────────────────────────────────────────
db.commit()
db.close()
print("\nSeed selesai.")
