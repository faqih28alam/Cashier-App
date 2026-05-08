"use client";
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "@/lib/api";
import { toast } from "@/components/shared/Toast";
import { DataTable } from "@/components/shared/DataTable";

function today() { return new Date().toISOString().slice(0, 10); }
function firstOfMonth() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-01`; }
function fmt(n: number) { return Number(n).toLocaleString("id-ID"); }

interface PenjualanRow { tanggal: string; jumlah_transaksi: number; total_penjualan: number; }
interface TopRow { barcode: string; nama_barang: string; total_qty: number; total_penjualan: number; }

export default function LaporanPage() {
  const [from, setFrom] = useState(firstOfMonth());
  const [to, setTo] = useState(today());
  const [penjualan, setPenjualan] = useState<PenjualanRow[]>([]);
  const [top, setTop] = useState<TopRow[]>([]);

  async function load() {
    try {
      const [p, t] = await Promise.all([
        api.get<PenjualanRow[]>("/laporan/penjualan", { tgl_mulai: from, tgl_selesai: to }),
        api.get<TopRow[]>("/laporan/produk-terlaris", { tgl_mulai: from, tgl_selesai: to, limit: 10 }),
      ]);
      setPenjualan(p);
      setTop(t);
    } catch (err) { toast((err as Error).message, "error"); }
  }

  useEffect(() => { load(); }, []);

  const totalPenjualan = penjualan.reduce((s, r) => s + Number(r.total_penjualan), 0);
  const totalTrx = penjualan.reduce((s, r) => s + Number(r.jumlah_transaksi), 0);

  return (
    <div className="p-5 space-y-5">
      <div>
        <h1 className="text-lg font-bold text-gray-800">Laporan Penjualan</h1>
        <p className="text-xs text-gray-500 mt-0.5 mb-3">Ringkasan pendapatan harian dan 10 produk terlaris dalam rentang tanggal yang dipilih.</p>
      </div>
      <div className="flex items-center gap-3 flex-wrap">
        <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="border rounded px-2 py-1 text-sm" />
        <span className="text-gray-400">s/d</span>
        <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="border rounded px-2 py-1 text-sm" />
        <button onClick={load} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-1.5 rounded text-sm">Tampilkan</button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <p className="text-xs text-gray-500">Total Penjualan</p>
          <p className="text-2xl font-bold text-gray-800">Rp {fmt(totalPenjualan)}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <p className="text-xs text-gray-500">Jumlah Transaksi</p>
          <p className="text-2xl font-bold text-gray-800">{totalTrx}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">Penjualan Harian</p>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={penjualan.map((r) => ({ ...r, total_penjualan: Number(r.total_penjualan) }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="tanggal" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
            <Tooltip formatter={(v) => [`Rp ${fmt(Number(v))}`, "Penjualan"]} />
            <Bar dataKey="total_penjualan" fill="#1f2937" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg border p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">Produk Terlaris</p>
        <DataTable
          columns={[
            { key: "nama_barang", label: "Nama Barang", className: "font-medium" },
            { key: "total_qty", label: "Total QTY", render: (r: TopRow) => fmt(r.total_qty) },
            { key: "total_penjualan", label: "Total Penjualan", render: (r: TopRow) => `Rp ${fmt(r.total_penjualan)}` },
          ]}
          data={top}
          keyField="barcode"
        />
      </div>
    </div>
  );
}
