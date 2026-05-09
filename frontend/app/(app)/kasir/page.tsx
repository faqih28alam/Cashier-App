"use client";
import { useRef, useState, useCallback, useEffect } from "react";
import { Trash2, Edit3 } from "lucide-react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";
import { useDebounce } from "@/lib/useDebounce";
import { toast } from "@/components/shared/Toast";
import { NumpadPopup } from "@/components/pos/NumpadPopup";
import { PaymentScreen } from "@/components/pos/PaymentScreen";
import { ReceiptPreview } from "@/components/pos/ReceiptPreview";

interface StoreSetting {
  nama_toko: string;
  alamat: string;
  telepon: string;
  receipt_footer: string;
}

interface Barang {
  barcode: string;
  nama_barang: string;
  sat: string;
  hpp: number;
  harga_1: number;
  harga_2: number;
  min_qty_harga_2: number;
  harga_3: number;
  min_qty_harga_3: number;
}

interface TransaksiItem {
  barcode: string;
  nama_barang: string;
  sat: string;
  qty: number;
  hpp: number;
  harga: number;
  diskon: number;
  total: number;
}

function resolvePrice(b: Barang, qty: number): number {
  if (Number(b.min_qty_harga_3) > 0 && qty >= Number(b.min_qty_harga_3)) return Number(b.harga_3);
  if (Number(b.min_qty_harga_2) > 0 && qty >= Number(b.min_qty_harga_2)) return Number(b.harga_2);
  return Number(b.harga_1);
}

function fmt(n: number | string) {
  return Number(n).toLocaleString("id-ID");
}

export default function KasirPage() {
  const barcodeRef = useRef<HTMLInputElement>(null);
  const [barcode, setBarcode] = useState("");
  const [searchResults, setSearchResults] = useState<Barang[]>([]);
  const debouncedBarcode = useDebounce(barcode, 300);
  const [items, setItems] = useState<TransaksiItem[]>(() => {
    try { return JSON.parse(localStorage.getItem("kasir_cart") ?? "[]"); } catch { return []; }
  });
  const [numpadTarget, setNumpadTarget] = useState<number | null>(null);
  const [showPayment, setShowPayment] = useState(false);
  const [receipt, setReceipt] = useState<null | {
    id: number; noTransaksi: string; tanggal: string; bayar: number; kembalian: number;
    items: TransaksiItem[]; total: number;
  }>(null);
  const [paying, setPaying] = useState(false);
  const [setting, setSetting] = useState<StoreSetting>({ nama_toko: "Kasir App", alamat: "", telepon: "", receipt_footer: "Terima Kasih!" });
  const logoUrl = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/static/logo.png`;

  useEffect(() => {
    api.get<StoreSetting>("/setting/").then(setSetting).catch(() => {
      toast("Gagal memuat pengaturan toko", "error");
    });
  }, []);

  useEffect(() => {
    localStorage.setItem("kasir_cart", JSON.stringify(items));
  }, [items]);

  useEffect(() => {
    if (!debouncedBarcode.trim()) { setSearchResults([]); return; }
    api.get<Barang[]>("/master/barang", { q: debouncedBarcode.trim() })
      .then((res) => setSearchResults(res.slice(0, 8)))
      .catch(() => setSearchResults([]));
  }, [debouncedBarcode]);

  const total = items.reduce((s, i) => s + Number(i.total), 0);
  const user = getUser();

  const addBarang = useCallback((barang: Barang) => {
    setItems((prev) => {
      const idx = prev.findIndex((i) => i.barcode === barang.barcode);
      if (idx >= 0) {
        const updated = [...prev];
        const newQty = updated[idx].qty + 1;
        const harga = resolvePrice(barang, newQty);
        updated[idx] = { ...updated[idx], qty: newQty, harga, total: newQty * harga - updated[idx].diskon };
        return updated;
      }
      const harga = resolvePrice(barang, 1);
      return [...prev, { barcode: barang.barcode, nama_barang: barang.nama_barang, sat: barang.sat, qty: 1, hpp: Number(barang.hpp), harga, diskon: 0, total: harga }];
    });
  }, []);

  const lookupBarcode = useCallback(async (code: string) => {
    if (!code.trim()) return;
    setSearchResults([]);
    try {
      const barang = await api.get<Barang>(`/master/barang/${code.trim()}`);
      addBarang(barang);
    } catch {
      toast(`Barcode "${code}" tidak ditemukan`, "error");
    }
    setBarcode("");
    barcodeRef.current?.focus();
  }, [addBarang]);

  function selectFromSearch(barang: Barang) {
    addBarang(barang);
    setSearchResults([]);
    setBarcode("");
    barcodeRef.current?.focus();
  }

  function handleBarcodeKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") lookupBarcode(barcode);
  }

  function updateItem(idx: number, qty: number, diskon: number) {
    setItems((prev) => {
      const updated = [...prev];
      const item = { ...updated[idx], qty, diskon };
      item.total = qty * item.harga - diskon;
      updated[idx] = item;
      return updated;
    });
    setNumpadTarget(null);
    barcodeRef.current?.focus();
  }

  function removeItem(idx: number) {
    setItems((prev) => prev.filter((_, i) => i !== idx));
    barcodeRef.current?.focus();
  }

  function clearAll() {
    setItems([]);
    barcodeRef.current?.focus();
  }

  async function handlePayment(bayar: number) {
    setPaying(true);
    const snapshot = [...items];
    const snapshotTotal = snapshot.reduce((s, i) => s + i.total, 0);
    try {
      const res = await api.post<{ id: number; no_transaksi: string; tanggal: string; bayar: number; kembalian: number }>(
        "/kasir/transaksi",
        { bayar, detail: items.map((i) => ({ barcode: i.barcode, nama_barang: i.nama_barang, sat: i.sat, qty: i.qty, hpp: i.hpp, harga: i.harga, diskon: i.diskon })) }
      );
      setItems([]);
      setShowPayment(false);
      setReceipt({
        id: res.id,
        noTransaksi: res.no_transaksi,
        tanggal: new Date(res.tanggal).toLocaleString("id-ID"),
        bayar: res.bayar,
        kembalian: res.kembalian,
        items: snapshot,
        total: snapshotTotal,
      });
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setPaying(false);
    }
  }

  return (
    <div className="flex h-full bg-gray-100">
      {/* Transaction Table */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-800 text-white text-xs sticky top-0">
              <tr>
                {(["NO","NAMA BARANG","SAT","QTY","HARGA","DISKON","TOTAL",""] as const).map((h) => (
                  <th key={h} className={`px-3 py-2 font-medium ${["HARGA","DISKON","TOTAL"].includes(h) ? "text-right" : "text-left"}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {items.length === 0 ? (
                <tr><td colSpan={8} className="px-3 py-16 text-center text-gray-400 text-sm">Scan barcode atau ketik kode barang</td></tr>
              ) : items.map((item, idx) => (
                <tr key={idx} className="hover:bg-blue-50 cursor-pointer" onClick={() => setNumpadTarget(idx)}>
                  <td className="px-3 py-2 text-gray-500">{idx + 1}</td>
                  <td className="px-3 py-2 font-medium">{item.nama_barang}</td>
                  <td className="px-3 py-2 text-gray-500">{item.sat}</td>
                  <td className="px-3 py-2">
                    <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">
                      {Number(item.qty) % 1 === 0 ? item.qty : Number(item.qty).toFixed(3).replace(/\.?0+$/, "")}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right">{fmt(item.harga)}</td>
                  <td className="px-3 py-2 text-right text-gray-500">{fmt(item.diskon)}</td>
                  <td className="px-3 py-2 text-right font-semibold">{fmt(item.total)}</td>
                  <td className="px-3 py-2">
                    <div className="flex gap-1">
                      <button onClick={(e) => { e.stopPropagation(); setNumpadTarget(idx); }} className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-blue-600"><Edit3 size={14} /></button>
                      <button onClick={(e) => { e.stopPropagation(); removeItem(idx); }} className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-red-600"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Barcode input bar */}
        <div className="bg-white border-t px-4 py-2 flex items-center gap-3 relative">
          <div className="flex-1 relative">
            <input
              ref={barcodeRef}
              autoFocus
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              onKeyDown={handleBarcodeKey}
              onBlur={() => setTimeout(() => setSearchResults([]), 150)}
              placeholder="Scan barcode atau ketik nama barang..."
              className="w-full border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
            {searchResults.length > 0 && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-white border rounded shadow-lg z-20 max-h-64 overflow-y-auto">
                {searchResults.map((b) => (
                  <button
                    key={b.barcode}
                    onMouseDown={() => selectFromSearch(b)}
                    className="flex items-center justify-between w-full px-3 py-2 hover:bg-blue-50 text-sm border-b last:border-0 text-left"
                  >
                    <div>
                      <span className="font-medium text-gray-800">{b.nama_barang}</span>
                      <span className="text-gray-400 text-xs ml-2">{b.barcode}</span>
                    </div>
                    <span className="text-gray-600 font-medium ml-4">Rp {b.harga_1.toLocaleString("id-ID")}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <button onClick={() => lookupBarcode(barcode)} className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-1.5 rounded text-sm">Cari</button>
          <span className="text-gray-400 text-xs">|</span>
          <span className="text-sm text-gray-500">TRANSAKSI:</span>
          <span className="font-bold text-gray-800">{fmt(total)}</span>
        </div>
      </div>

      {/* Action Panel */}
      <div className="w-36 bg-gray-800 flex flex-col gap-2 p-3 flex-shrink-0">
        <button onClick={() => items.length > 0 && setNumpadTarget(items.length - 1)} className="bg-gray-600 hover:bg-gray-500 text-white text-xs py-2 px-2 rounded">Edit QTY / Diskon</button>
        <button onClick={clearAll} className="bg-gray-600 hover:bg-gray-500 text-white text-xs py-2 px-2 rounded">Hapus Semua</button>
        <div className="flex-1" />
        <button
          onClick={() => items.length > 0 && setShowPayment(true)}
          disabled={items.length === 0}
          className="bg-green-500 hover:bg-green-400 disabled:opacity-40 text-white font-bold py-4 rounded text-sm"
        >
          BAYAR
        </button>
      </div>

      {/* Numpad Popup */}
      {numpadTarget !== null && (
        <NumpadPopup
          productName={items[numpadTarget]?.nama_barang ?? ""}
          unit={items[numpadTarget]?.sat ?? "PCS"}
          harga={items[numpadTarget]?.harga ?? 0}
          initialQty={items[numpadTarget]?.qty ?? 1}
          initialDiskon={items[numpadTarget]?.diskon ?? 0}
          onConfirm={(qty, diskon) => updateItem(numpadTarget, qty, diskon)}
          onCancel={() => { setNumpadTarget(null); barcodeRef.current?.focus(); }}
        />
      )}

      {/* Payment */}
      {showPayment && (
        <PaymentScreen
          total={total}
          onConfirm={handlePayment}
          onCancel={() => { setShowPayment(false); barcodeRef.current?.focus(); }}
          loading={paying}
        />
      )}

      {/* Receipt */}
      {receipt && (
        <ReceiptPreview
          noTransaksi={receipt.noTransaksi}
          tanggal={receipt.tanggal}
          kasir={user?.nama ?? ""}
          items={receipt.items}
          total={receipt.total}
          bayar={receipt.bayar}
          kembalian={receipt.kembalian}
          storeName={setting.nama_toko}
          storeAddress={setting.alamat}
          storeTelepon={setting.telepon}
          footer={setting.receipt_footer}
          logoUrl={logoUrl}
          transaksiId={receipt.id}
          onClose={() => { setReceipt(null); barcodeRef.current?.focus(); }}
        />
      )}
    </div>
  );
}
