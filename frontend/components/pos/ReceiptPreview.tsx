"use client";
import { Modal } from "@/components/shared/Modal";

interface Item {
  nama_barang: string;
  qty: number;
  sat: string;
  harga: number;
  total: number;
}

interface Props {
  noTransaksi: string;
  tanggal: string;
  kasir: string;
  items: Item[];
  total: number;
  bayar: number;
  kembalian: number;
  storeName: string;
  storeAddress?: string;
  storeTelepon?: string;
  footer?: string;
  onClose: () => void;
}

function fmt(n: number) {
  return n.toLocaleString("id-ID");
}

export function ReceiptPreview({
  noTransaksi, tanggal, kasir, items, total, bayar, kembalian,
  storeName, storeAddress, storeTelepon, footer, onClose,
}: Props) {
  return (
    <Modal title="Struk Transaksi" onClose={onClose} width="max-w-sm">
      <div className="font-mono text-xs bg-gray-50 p-4 rounded border">
        <p className="text-center font-bold text-sm">{storeName}</p>
        {storeAddress && <p className="text-center">{storeAddress}</p>}
        {storeTelepon && <p className="text-center">Telp: {storeTelepon}</p>}
        <p className="text-center">{"=".repeat(32)}</p>
        <p>No : {noTransaksi}</p>
        <p>Tgl: {tanggal}</p>
        <p>Kasir: {kasir}</p>
        <p>{"-".repeat(32)}</p>
        {items.map((item, i) => (
          <div key={i}>
            <p className="truncate">{item.nama_barang}</p>
            <div className="flex justify-between">
              <span>{item.qty} {item.sat} x {fmt(item.harga)}</span>
              <span>{fmt(item.total)}</span>
            </div>
          </div>
        ))}
        <p>{"-".repeat(32)}</p>
        <div className="flex justify-between font-bold"><span>Total</span><span>{fmt(total)}</span></div>
        <div className="flex justify-between"><span>Bayar</span><span>{fmt(bayar)}</span></div>
        <div className="flex justify-between"><span>Kembali</span><span>{fmt(kembalian)}</span></div>
        <p>{"=".repeat(32)}</p>
        <p className="text-center">{footer ?? "Terima Kasih!"}</p>
      </div>
      <button onClick={onClose} className="mt-4 w-full bg-gray-800 hover:bg-gray-700 text-white py-2 rounded text-sm font-medium">
        Tutup
      </button>
    </Modal>
  );
}
