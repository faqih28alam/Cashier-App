"use client";
import { useState, useEffect } from "react";
import { FileDown, TrendingUp, ShoppingCart, Package, BarChart2 } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "@/components/shared/Toast";
import { DataTable } from "@/components/shared/DataTable";

function today() { return new Date().toISOString().slice(0, 10); }
function firstOfMonth() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-01`; }
function fmt(n: number) { return Number(n).toLocaleString("id-ID"); }

interface Row {
  id: number;
  tanggal: string;
  no_transaksi: string;
  nama_barang: string;
  sat: string;
  qty: number;
  hpp: number;
  harga: number;
  diskon: number;
  total: number;
  laba_kotor: number;
}

interface StoreSetting { nama_toko: string; alamat: string; telepon: string; }

function StatCard({ title, value, sub, icon: Icon, color }: {
  title: string; value: string; sub?: string; icon: React.ElementType; color: string;
}) {
  return (
    <div className="bg-white rounded-lg border p-4 flex items-start justify-between">
      <div>
        <p className="text-xs text-gray-500 mb-1">{title}</p>
        <p className="text-xl font-bold text-gray-800">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon size={18} className="text-white" />
      </div>
    </div>
  );
}

export default function PenjualanPage() {
  const [from, setFrom] = useState(firstOfMonth());
  const [to, setTo] = useState(today());
  const [data, setData] = useState<Row[]>([]);
  const [setting, setSetting] = useState<StoreSetting>({ nama_toko: "", alamat: "", telepon: "" });
  const [exporting, setExporting] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api.get<StoreSetting>("/setting/").then(setSetting).catch(() => {});
    load();
  }, []);

  async function load() {
    try {
      const res = await api.get<Row[]>("/laporan/penjualan-detail", { tgl_mulai: from, tgl_selesai: to });
      setData(res);
      setLoaded(true);
    } catch (err) { toast((err as Error).message, "error"); }
  }

  const totalOmzet   = data.reduce((s, r) => s + Number(r.total), 0);
  const totalLaba    = data.reduce((s, r) => s + Number(r.laba_kotor), 0);
  const totalQty     = data.reduce((s, r) => s + Number(r.qty), 0);
  const totalDiskon  = data.reduce((s, r) => s + Number(r.diskon), 0);
  const trxSet       = new Set(data.map((r) => r.no_transaksi));
  const margin       = totalOmzet > 0 ? ((totalLaba / totalOmzet) * 100).toFixed(1) : "0";

  async function handleExportPDF() {
    setExporting(true);
    try {
      const { default: jsPDF } = await import("jspdf");
      const { default: autoTable } = await import("jspdf-autotable");

      const doc = new jsPDF({ orientation: "landscape" });
      const pageW = doc.internal.pageSize.getWidth();
      let y = 15;

      doc.setFontSize(16);
      doc.setFont("helvetica", "bold");
      doc.text(setting.nama_toko || "Laporan Penjualan", pageW / 2, y, { align: "center" });
      y += 7;
      doc.setFontSize(9);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100);
      if (setting.alamat) { doc.text(setting.alamat, pageW / 2, y, { align: "center" }); y += 5; }
      if (setting.telepon) { doc.text(`Telp: ${setting.telepon}`, pageW / 2, y, { align: "center" }); y += 5; }
      doc.text(`Periode: ${from} s/d ${to}`, pageW / 2, y, { align: "center" }); y += 5;
      doc.text(`Dicetak: ${new Date().toLocaleString("id-ID")}`, pageW / 2, y, { align: "center" }); y += 8;

      doc.setDrawColor(200);
      doc.line(14, y, pageW - 14, y);
      y += 8;

      doc.setFontSize(11);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(0);
      doc.text("Ringkasan", 14, y); y += 6;

      autoTable(doc, {
        startY: y,
        head: [["Keterangan", "Nilai"]],
        body: [
          ["Total Omzet",       `Rp ${fmt(totalOmzet)}`],
          ["Total Laba Kotor",  `Rp ${fmt(totalLaba)}`],
          ["Margin Laba",       `${margin}%`],
          ["Total Diskon",      `Rp ${fmt(totalDiskon)}`],
          ["Jumlah Transaksi",  String(trxSet.size)],
          ["Total Item Terjual",fmt(totalQty)],
        ],
        styles: { fontSize: 9 },
        headStyles: { fillColor: [31, 41, 55] },
        columnStyles: { 1: { halign: "right" } },
        margin: { left: 14, right: 14 },
        tableWidth: 100,
      });
      y = (doc as any).lastAutoTable.finalY + 10;

      doc.setFontSize(11);
      doc.setFont("helvetica", "bold");
      doc.text("Detail Penjualan", 14, y); y += 6;

      autoTable(doc, {
        startY: y,
        head: [["Tanggal", "No. Transaksi", "Nama Barang", "SAT", "QTY", "HPP", "Harga", "Diskon", "Total", "Laba Kotor"]],
        body: data.map((r) => [
          r.tanggal,
          r.no_transaksi,
          r.nama_barang,
          r.sat,
          Number(r.qty) % 1 === 0 ? String(r.qty) : Number(r.qty).toFixed(3).replace(/\.?0+$/, ""),
          `Rp ${fmt(Number(r.hpp))}`,
          `Rp ${fmt(Number(r.harga))}`,
          Number(r.diskon) > 0 ? `Rp ${fmt(Number(r.diskon))}` : "-",
          `Rp ${fmt(Number(r.total))}`,
          `Rp ${fmt(Number(r.laba_kotor))}`,
        ]),
        foot: [["", "", "", "", fmt(totalQty), "", "", `Rp ${fmt(totalDiskon)}`, `Rp ${fmt(totalOmzet)}`, `Rp ${fmt(totalLaba)}`]],
        styles: { fontSize: 8 },
        headStyles: { fillColor: [31, 41, 55] },
        footStyles: { fillColor: [243, 244, 246], textColor: [0, 0, 0], fontStyle: "bold" },
        columnStyles: {
          4: { halign: "center" },
          5: { halign: "right" },
          6: { halign: "right" },
          7: { halign: "right" },
          8: { halign: "right" },
          9: { halign: "right" },
        },
        margin: { left: 14, right: 14 },
      });

      doc.save(`Penjualan_${from}_${to}.pdf`);
      toast("PDF berhasil diekspor", "success");
    } catch {
      toast("Gagal ekspor PDF", "error");
    } finally {
      setExporting(false);
    }
  }

  const columns = [
    { key: "tanggal",      label: "Tanggal",        render: (r: Row) => r.tanggal },
    { key: "no_transaksi", label: "No. Transaksi",   className: "font-mono text-xs" },
    { key: "nama_barang",  label: "Nama Barang",     className: "font-medium" },
    { key: "sat",          label: "SAT",             className: "text-gray-500" },
    { key: "qty",          label: "QTY",             render: (r: Row) => (
      <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold text-xs">
        {Number(r.qty) % 1 === 0 ? r.qty : Number(r.qty).toFixed(3).replace(/\.?0+$/, "")}
      </span>
    )},
    { key: "hpp",          label: "HPP",             render: (r: Row) => <span className="text-gray-500">{fmt(Number(r.hpp))}</span> },
    { key: "harga",        label: "Harga Jual",      render: (r: Row) => fmt(Number(r.harga)) },
    { key: "diskon",       label: "Diskon",          render: (r: Row) => Number(r.diskon) > 0 ? <span className="text-orange-600">-{fmt(Number(r.diskon))}</span> : <span className="text-gray-300">-</span> },
    { key: "total",        label: "Total Omzet",     render: (r: Row) => <span className="font-semibold">{fmt(Number(r.total))}</span> },
    { key: "laba_kotor",   label: "Laba Kotor",      render: (r: Row) => <span className="text-emerald-700 font-semibold">{fmt(Number(r.laba_kotor))}</span> },
  ];

  return (
    <div className="p-5 space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-lg font-bold text-gray-800">Penjualan</h1>
          <p className="text-xs text-gray-500 mt-0.5">Detail produk terjual per transaksi — qty, HPP, omzet, dan laba kotor.</p>
        </div>
        <button
          onClick={handleExportPDF}
          disabled={exporting || data.length === 0}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-white px-4 py-2 rounded text-sm font-medium"
        >
          <FileDown size={15} />
          {exporting ? "Mengekspor..." : "Export PDF"}
        </button>
      </div>

      {/* Date filter */}
      <div className="bg-white rounded-lg border p-4 flex items-center gap-3 flex-wrap">
        <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="border rounded px-2 py-1 text-sm" />
        <span className="text-gray-400">s/d</span>
        <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="border rounded px-2 py-1 text-sm" />
        <button onClick={load} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-1.5 rounded text-sm">Tampilkan</button>
        {loaded && <span className="text-xs text-gray-400 ml-2">{data.length} baris ditemukan</span>}
      </div>

      {/* Summary cards */}
      {data.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Omzet" value={`Rp ${fmt(totalOmzet)}`} sub={`${trxSet.size} transaksi`} icon={TrendingUp} color="bg-orange-500" />
          <StatCard title="Total Laba Kotor" value={`Rp ${fmt(totalLaba)}`} sub={`Margin ${margin}%`} icon={BarChart2} color="bg-emerald-600" />
          <StatCard title="Total Item Terjual" value={fmt(totalQty)} sub={`${data.length} baris`} icon={Package} color="bg-blue-500" />
          <StatCard title="Total Diskon" value={`Rp ${fmt(totalDiskon)}`} icon={ShoppingCart} color="bg-purple-500" />
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg border">
        <div className="px-4 pt-4 pb-2 flex items-center justify-between">
          <p className="text-sm font-semibold text-gray-700">Detail Per Item</p>
          {data.length > 0 && (
            <div className="flex gap-4 text-xs text-gray-500">
              <span>Omzet: <span className="font-bold text-gray-800">Rp {fmt(totalOmzet)}</span></span>
              <span>Laba: <span className="font-bold text-emerald-700">Rp {fmt(totalLaba)}</span></span>
            </div>
          )}
        </div>
        <DataTable columns={columns} data={data} keyField="id" />
      </div>
    </div>
  );
}
