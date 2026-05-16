import os
from sqlalchemy.orm import Session
from models.transaksi import Transaksi
from models.setting import Setting

LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "logo.png")


def print_receipt(db: Session, trx: Transaksi) -> None:
    setting = db.get(Setting, 1)
    if not setting or not setting.printer_port:
        raise RuntimeError("Printer port belum dikonfigurasi")

    from escpos.printer import Serial, Usb, Win32Raw
    from escpos import exceptions

    try:
        port = setting.printer_port
        if port.startswith("COM") or port.startswith("/dev/tty"):
            p = Serial(port, baudrate=9600)
        elif port.upper() == "USB":
            p = Usb(0x2AAF, 0x6020)
        else:
            p = Win32Raw(port)  # Windows printer name, e.g. "XH-58PRO"
    except Exception as e:
        raise RuntimeError(str(e))

    width = setting.printer_width or 80
    cols = 48 if width == 80 else 32

    if os.path.exists(LOGO_PATH):
        from PIL import Image, ImageOps
        max_px = 360 if width == 58 else 512
        logo = Image.open(LOGO_PATH).convert("RGBA")
        # crop transparent/white padding so logo sits tight above store name
        bg = Image.new("RGBA", logo.size, (255, 255, 255, 255))
        bg.paste(logo, mask=logo.split()[3])
        logo = bg.convert("RGB")
        bbox = logo.getbbox()
        if bbox:
            logo = logo.crop(bbox)
        if logo.width > max_px:
            ratio = max_px / logo.width
            logo = logo.resize((max_px, int(logo.height * ratio)), Image.LANCZOS)
        p.set(align="center")
        p.image(logo)

    p.set(align="center", bold=True, double_height=False, double_width=False)
    p.text(f"{setting.nama_toko}\n")
    p.set(align="center", bold=False, double_height=False)
    if setting.alamat:
        p.text(f"{setting.alamat}\n")
    if setting.telepon:
        p.text(f"Telp: {setting.telepon}\n")
    p.text("-" * cols + "\n")

    p.set(align="left")
    p.text(f"No : {trx.no_transaksi}\n")
    p.text(f"Tgl: {trx.tanggal.strftime('%d-%b-%Y %H:%M')}\n")
    if trx.user:
        p.text(f"Kasir: {trx.user.nama}\n")
    p.text("-" * cols + "\n")

    for item in trx.detail:
        p.text(f"{item.nama_barang}\n")
        line = f"  {float(item.qty):.0f} {item.sat} x {float(item.harga):,.0f}"
        total_str = f"{float(item.total):>10,.0f}"
        p.text(f"{line:<{cols - 10}}{total_str}\n")

    p.text("-" * cols + "\n")
    p.set(bold=True)
    p.text(f"{'Total':<{cols - 10}}{float(trx.total):>10,.0f}\n")
    p.set(bold=False)
    p.text(f"{'Bayar':<{cols - 10}}{float(trx.bayar):>10,.0f}\n")
    p.text(f"{'Kembali':<{cols - 10}}{float(trx.kembalian):>10,.0f}\n")
    p.text("=" * cols + "\n")

    p.set(align="center")
    p.text(f"{setting.receipt_footer or 'Terima Kasih!'}\n")
    p.text("\n\n\n")
    p.cut()
    p.close()
