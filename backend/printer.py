from sqlalchemy.orm import Session
from models.transaksi import Transaksi
from models.setting import Setting


def print_receipt(db: Session, trx: Transaksi) -> None:
    setting = db.get(Setting, 1)
    if not setting or not setting.printer_port:
        raise RuntimeError("Printer port belum dikonfigurasi")

    from escpos.printer import Serial, Usb
    from escpos import exceptions

    try:
        if setting.printer_port.startswith("COM") or setting.printer_port.startswith("/dev/tty"):
            p = Serial(setting.printer_port, baudrate=9600)
        else:
            p = Usb(0x04b8, 0x0202)  # fallback USB; configure VID/PID in setting if needed
    except exceptions.DeviceNotFoundUnusableError as e:
        raise RuntimeError(str(e))

    width = setting.printer_width or 80
    cols = 48 if width == 80 else 32

    p.set(align="center", bold=True, double_height=True, double_width=False)
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
