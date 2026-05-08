"use client";
import { useState, useEffect } from "react";
import { Plus, CheckCircle } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "@/components/shared/Toast";
import { DataTable } from "@/components/shared/DataTable";
import { Modal } from "@/components/shared/Modal";

interface PembelianRow { id: number; no_faktur: string; tanggal: string; total: number; status: string; }
interface DetailItem { barcode: string; nama_barang: string; sat: string; qty: number; hpp: number; }

function fmt(n: number) { return Number(n).toLocaleString("id-ID"); }

export default function PurchasPage() {
  const [data, setData] = useState<PembelianRow[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [header, setHeader] = useState({ no_faktur: "", tanggal: new Date().toISOString().slice(0,10) });
  const [detail, setDetail] = useState<DetailItem[]>([{ barcode: "", nama_barang: "", sat: "PCS", qty: 1, hpp: 0 }]);

  async function load() {
    try { setData(await api.get<PembelianRow[]>("/purchas/")); }
    catch (err) { toast((err as Error).message, "error"); }
  }

  useEffect(() => { load(); }, []);

  async function handleSave() {
    try {
      await api.post("/purchas/", { ...header, tanggal: new Date(header.tanggal).toISOString(), detail });
      toast("Pembelian disimpan", "success");
      setShowModal(false);
      load();
    } catch (err) { toast((err as Error).message, "error"); }
  }

  async function handleConfirm(id: number) {
    if (!confirm("Konfirmasi pembelian? Stok akan diperbarui.")) return;
    try {
      await api.post(`/purchas/${id}/confirm`, {});
      toast("Pembelian dikonfirmasi, stok diperbarui", "success");
      load();
    } catch (err) { toast((err as Error).message, "error"); }
  }

  function addRow() { setDetail([...detail, { barcode: "", nama_barang: "", sat: "PCS", qty: 1, hpp: 0 }]); }
  function updateRow(i: number, field: keyof DetailItem, val: string | number) {
    setDetail(detail.map((d, idx) => idx === i ? { ...d, [field]: val } : d));
  }

  return (
    <div className="p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold text-gray-800">Pembelian</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1.5 rounded text-sm">
          <Plus size={14} /> Buat Pembelian
        </button>
      </div>

      <DataTable
        columns={[
          { key: "no_faktur", label: "No. Faktur", className: "font-medium" },
          { key: "tanggal", label: "Tanggal", render: (r: PembelianRow) => new Date(r.tanggal).toLocaleDateString("id-ID") },
          { key: "total", label: "Total", render: (r: PembelianRow) => `Rp ${fmt(r.total)}` },
          { key: "status", label: "Status", render: (r: PembelianRow) => (
            <span className={`text-xs px-2 py-0.5 rounded font-medium ${r.status === "confirmed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
              {r.status}
            </span>
          )},
          { key: "actions", label: "", render: (r: PembelianRow) => r.status === "draft" && (
            <button onClick={() => handleConfirm(r.id)} className="flex items-center gap-1 text-xs text-green-600 hover:text-green-800">
              <CheckCircle size={14} /> Konfirmasi
            </button>
          )},
        ]}
        data={data}
        keyField="id"
      />

      {showModal && (
        <Modal title="Buat Pembelian" onClose={() => setShowModal(false)} width="max-w-3xl">
          <div className="grid grid-cols-2 gap-3 mb-4">
            {[["no_faktur","No. Faktur","text"],["tanggal","Tanggal","date"]].map(([k, label, type]) => (
              <div key={k}>
                <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                <input type={type} value={String(header[k as keyof typeof header])}
                  onChange={(e) => setHeader({ ...header, [k]: e.target.value })}
                  className="w-full border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300" />
              </div>
            ))}
          </div>
          <div className="overflow-x-auto mb-3">
            <table className="w-full text-xs">
              <thead className="bg-gray-100">
                <tr>{["Barcode","Nama","SAT","QTY","HPP"].map((h) => <th key={h} className="px-2 py-1.5 text-left font-medium">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y">
                {detail.map((row, i) => (
                  <tr key={i}>
                    {(["barcode","nama_barang","sat"] as const).map((f) => (
                      <td key={f} className="px-1 py-1">
                        <input value={row[f]} onChange={(e) => updateRow(i, f, e.target.value)}
                          className="w-full border rounded px-1.5 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-gray-300" />
                      </td>
                    ))}
                    {(["qty","hpp"] as const).map((f) => (
                      <td key={f} className="px-1 py-1 w-24">
                        <input type="number" value={row[f]} onChange={(e) => updateRow(i, f, Number(e.target.value))}
                          className="w-full border rounded px-1.5 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-gray-300" />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button onClick={addRow} className="text-xs text-blue-600 hover:underline mb-4">+ Tambah Baris</button>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm border rounded hover:bg-gray-50">Batal</button>
            <button onClick={handleSave} className="px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700">Simpan Draft</button>
          </div>
        </Modal>
      )}
    </div>
  );
}
