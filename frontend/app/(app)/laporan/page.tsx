"use client";
import { useState, useEffect } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { TrendingUp, ShoppingCart, BarChart2, Package } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "@/components/shared/Toast";
import { DataTable } from "@/components/shared/DataTable";

function today() { return new Date().toISOString().slice(0, 10); }
function firstOfMonth() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-01`; }
function daysAgo(n: number) { const d = new Date(); d.setDate(d.getDate() - n + 1); return d.toISOString().slice(0, 10); }
function fmt(n: number) { return Number(n).toLocaleString("id-ID"); }
function fmtShort(n: number) { return n >= 1_000_000 ? `${(n/1_000_000).toFixed(1)}Jt` : n >= 1_000 ? `${(n/1_000).toFixed(0)}K` : String(n); }
function fmtDate(s: string) { const d = new Date(s); return `${d.getDate()}/${d.getMonth()+1}`; }

interface PenjualanRow { tanggal: string; jumlah_transaksi: number; total_penjualan: number; }
interface TopRow { barcode: string; nama_barang: string; total_qty: number; total_penjualan: number; }

interface Summary { revenue: number; trx: number; }

function StatCard({ title, value, sub, icon: Icon, color }: {
  title: string; value: string; sub: string; icon: React.ElementType; color: string;
}) {
  return (
    <div className="bg-white rounded-lg border p-4 flex items-start justify-between">
      <div>
        <p className="text-xs text-gray-500 mb-1">{title}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
        <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
      </div>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon size={18} className="text-white" />
      </div>
    </div>
  );
}

export default function LaporanPage() {
  const [from, setFrom] = useState(firstOfMonth());
  const [to, setTo] = useState(today());
  const [today14, setToday14] = useState<PenjualanRow[]>([]);
  const [monthly, setMonthly] = useState<PenjualanRow[]>([]);
  const [todaySummary, setTodaySummary] = useState<Summary>({ revenue: 0, trx: 0 });
  const [top, setTop] = useState<TopRow[]>([]);
  const [custom, setCustom] = useState<PenjualanRow[]>([]);

  async function loadDashboard() {
    try {
      const [t14, mon, tod, topProd] = await Promise.all([
        api.get<PenjualanRow[]>("/laporan/penjualan", { tgl_mulai: daysAgo(14), tgl_selesai: today() }),
        api.get<PenjualanRow[]>("/laporan/penjualan", { tgl_mulai: firstOfMonth(), tgl_selesai: today() }),
        api.get<PenjualanRow[]>("/laporan/penjualan", { tgl_mulai: today(), tgl_selesai: today() }),
        api.get<TopRow[]>("/laporan/produk-terlaris", { tgl_mulai: firstOfMonth(), tgl_selesai: today(), limit: 7 }),
      ]);
      setToday14(t14);
      setMonthly(mon);
      setTodaySummary({
        revenue: tod.reduce((s, r) => s + Number(r.total_penjualan), 0),
        trx: tod.reduce((s, r) => s + Number(r.jumlah_transaksi), 0),
      });
      setTop(topProd);
    } catch (err) { toast((err as Error).message, "error"); }
  }

  async function loadCustom() {
    try {
      const res = await api.get<PenjualanRow[]>("/laporan/penjualan", { tgl_mulai: from, tgl_selesai: to });
      setCustom(res);
    } catch (err) { toast((err as Error).message, "error"); }
  }

  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { loadCustom(); }, []);

  const monthlyRevenue = monthly.reduce((s, r) => s + Number(r.total_penjualan), 0);
  const monthlyTrx = monthly.reduce((s, r) => s + Number(r.jumlah_transaksi), 0);
  const customRevenue = custom.reduce((s, r) => s + Number(r.total_penjualan), 0);
  const customTrx = custom.reduce((s, r) => s + Number(r.jumlah_transaksi), 0);

  const chart14 = today14.map((r) => ({ ...r, total_penjualan: Number(r.total_penjualan), label: fmtDate(r.tanggal) }));
  return (
    <div className="p-5 space-y-5">
      <div>
        <h1 className="text-lg font-bold text-gray-800">Laporan Penjualan</h1>
        <p className="text-xs text-gray-500 mt-0.5">Ringkasan pendapatan dan performa toko.</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Pendapatan Hari Ini" value={`Rp ${fmt(todaySummary.revenue)}`} sub={`${todaySummary.trx} transaksi`} icon={TrendingUp} color="bg-green-500" />
        <StatCard title="Pendapatan Bulan Ini" value={`Rp ${fmt(monthlyRevenue)}`} sub={`${monthlyTrx} transaksi`} icon={BarChart2} color="bg-blue-500" />
        <StatCard title="Produk Terlaris" value={top[0]?.nama_barang?.split(" ").slice(0,2).join(" ") ?? "-"} sub={top[0] ? `Rp ${fmt(top[0].total_penjualan)}` : "belum ada data"} icon={Package} color="bg-orange-500" />
        <StatCard title="Total Transaksi Bulan Ini" value={String(monthlyTrx)} sub={`Rata-rata Rp ${monthlyTrx > 0 ? fmt(Math.round(monthlyRevenue / monthlyTrx)) : 0}`} icon={ShoppingCart} color="bg-purple-500" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Line chart — 14 days */}
        <div className="bg-white rounded-lg border p-4">
          <p className="text-sm font-semibold text-gray-700 mb-3">Revenue — 14 Hari Terakhir</p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chart14}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={fmtShort} />
              <Tooltip formatter={(v) => [`Rp ${fmt(Number(v))}`, "Penjualan"]} labelFormatter={(l) => `Tgl ${l}`} />
              <Line type="monotone" dataKey="total_penjualan" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top products table */}
        <div className="bg-white rounded-lg border p-4">
          <p className="text-sm font-semibold text-gray-700 mb-3">Produk Terlaris Bulan Ini</p>
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

      {/* Custom date range */}
      <div className="bg-white rounded-lg border p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">Penjualan Harian (Kustom)</p>
        <div className="flex items-center gap-3 flex-wrap mb-4">
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="border rounded px-2 py-1 text-sm" />
          <span className="text-gray-400">s/d</span>
          <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="border rounded px-2 py-1 text-sm" />
          <button onClick={loadCustom} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-1.5 rounded text-sm">Tampilkan</button>
          <span className="ml-auto text-sm text-gray-500">
            {customTrx} transaksi &nbsp;|&nbsp; <span className="font-bold text-gray-800">Rp {fmt(customRevenue)}</span>
          </span>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={custom.map((r) => ({ ...r, total_penjualan: Number(r.total_penjualan), label: fmtDate(r.tanggal) }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={fmtShort} />
            <Tooltip formatter={(v) => [`Rp ${fmt(Number(v))}`, "Penjualan"]} />
            <Bar dataKey="total_penjualan" fill="#1f2937" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
