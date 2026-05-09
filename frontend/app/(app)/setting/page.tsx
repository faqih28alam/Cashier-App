"use client";
import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { toast } from "@/components/shared/Toast";

interface Setting {
  id?: number; nama_toko: string; alamat: string; telepon: string;
  printer_port: string; printer_width: number; receipt_footer: string; tax_rate: number;
}

const EMPTY: Setting = { nama_toko: "", alamat: "", telepon: "", printer_port: "", printer_width: 80, receipt_footer: "Terima Kasih!", tax_rate: 0 };

export default function SettingPage() {
  const [form, setForm] = useState<Setting>(EMPTY);
  const [loading, setLoading] = useState(false);
  const [printers, setPrinters] = useState<string[]>([]);
  const [scanning, setScanning] = useState(false);
  const [logoKey, setLogoKey] = useState(Date.now());
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  useEffect(() => {
    api.get<Setting>("/setting/").then(setForm).catch(() => {});
  }, []);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setPrinters([]);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  async function handleSave() {
    setLoading(true);
    try {
      await api.put("/setting/", form);
      toast("Setting disimpan", "success");
    } catch (err) { toast((err as Error).message, "error"); }
    finally { setLoading(false); }
  }

  async function handleLogoUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingLogo(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${apiUrl}/setting/logo`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: fd,
      });
      if (!res.ok) throw new Error("Upload gagal");
      setLogoKey(Date.now());
      toast("Logo berhasil diupload", "success");
    } catch { toast("Gagal upload logo", "error"); }
    finally { setUploadingLogo(false); if (fileRef.current) fileRef.current.value = ""; }
  }

  async function handleLogoDelete() {
    try {
      await api.delete("/setting/logo");
      setLogoKey(Date.now());
      toast("Logo dihapus", "success");
    } catch { toast("Gagal menghapus logo", "error"); }
  }

  async function handleScanPrinters() {
    setScanning(true);
    setPrinters([]);
    try {
      const res = await api.get<{ printers: string[] }>("/setting/printers");
      if (res.printers.length === 0) {
        toast("Tidak ada printer ditemukan", "info");
      } else {
        setPrinters(res.printers);
      }
    } catch { toast("Gagal scan printer", "error"); }
    finally { setScanning(false); }
  }

  const otherFields: [keyof Setting, string, string][] = [
    ["nama_toko","Nama Toko","text"],
    ["alamat","Alamat","text"],
    ["telepon","Telepon","text"],
    ["printer_width","Lebar Kertas (mm)","number"],
    ["receipt_footer","Footer Struk","text"],
    ["tax_rate","Pajak (%)","number"],
  ];

  return (
    <div className="p-5 max-w-lg">
      <h1 className="text-lg font-bold text-gray-800">Setting</h1>
      <p className="text-xs text-gray-500 mt-0.5 mb-5">Konfigurasi nama toko, koneksi printer termal, dan tampilan struk pelanggan.</p>
      <div className="bg-white rounded-lg border p-5 flex flex-col gap-4">

        {/* Logo Upload */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-2">Logo Struk</label>
          <div className="flex items-center gap-3">
            <img
              key={logoKey}
              src={`${apiUrl}/static/logo.png?t=${logoKey}`}
              alt="Logo"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              onLoad={(e) => { (e.target as HTMLImageElement).style.display = "block"; }}
              className="h-16 border rounded p-1 bg-gray-50 object-contain hidden"
            />
            <div className="flex gap-2">
              <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleLogoUpload} />
              <button
                onClick={() => fileRef.current?.click()}
                disabled={uploadingLogo}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 border rounded text-sm text-gray-700"
              >
                {uploadingLogo ? "Mengupload..." : "Upload Logo"}
              </button>
              <button
                onClick={handleLogoDelete}
                className="px-3 py-2 bg-red-50 hover:bg-red-100 border border-red-200 rounded text-sm text-red-600"
              >
                Hapus
              </button>
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-1">Format PNG/JPG. Disarankan hitam-putih, lebar max 384px.</p>
        </div>

        {/* Printer Port with Scan button */}
        <div ref={dropdownRef} className="relative">
          <label className="block text-xs font-medium text-gray-600 mb-1">Printer Port</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={form.printer_port}
              onChange={(e) => setForm({ ...form, printer_port: e.target.value })}
              placeholder="Contoh: XH-58PRO atau COM3"
              className="flex-1 border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
            />
            <button
              onClick={handleScanPrinters}
              disabled={scanning}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 border rounded text-sm font-medium text-gray-700 whitespace-nowrap"
            >
              {scanning ? "Scanning..." : "🔍 Scan"}
            </button>
          </div>
          {printers.length > 0 && (
            <div className="absolute z-10 left-0 right-0 mt-1 bg-white border rounded shadow-md text-sm max-h-48 overflow-y-auto">
              {printers.map((p) => (
                <button
                  key={p}
                  onClick={() => { setForm({ ...form, printer_port: p }); setPrinters([]); }}
                  className="block w-full text-left px-3 py-2 hover:bg-gray-100 border-b last:border-b-0"
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>

        {otherFields.map(([key, label, type]) => (
          <div key={key}>
            <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
            <input type={type} value={String(form[key])}
              onChange={(e) => setForm({ ...form, [key]: type === "number" ? Number(e.target.value) : e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-300" />
          </div>
        ))}

        <button onClick={handleSave} disabled={loading}
          className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-white py-2 rounded text-sm font-medium mt-2">
          {loading ? "Menyimpan..." : "Simpan Setting"}
        </button>
      </div>
    </div>
  );
}
