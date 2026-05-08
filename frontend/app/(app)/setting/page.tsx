"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/shared/Toast";

interface Setting {
  id?: number; nama_toko: string; alamat: string; telepon: string;
  printer_port: string; printer_width: number; receipt_footer: string; tax_rate: number;
}

const EMPTY: Setting = { nama_toko: "", alamat: "", telepon: "", printer_port: "", printer_width: 80, receipt_footer: "Terima Kasih!", tax_rate: 0 };

export default function SettingPage() {
  const [form, setForm] = useState<Setting>(EMPTY);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get<Setting>("/setting/").then(setForm).catch(() => {});
  }, []);

  async function handleSave() {
    setLoading(true);
    try {
      await api.put("/setting/", form);
      toast("Setting disimpan", "success");
    } catch (err) { toast((err as Error).message, "error"); }
    finally { setLoading(false); }
  }

  const fields: [keyof Setting, string, string][] = [
    ["nama_toko","Nama Toko","text"],
    ["alamat","Alamat","text"],
    ["telepon","Telepon","text"],
    ["printer_port","Printer Port (misal: COM3 atau /dev/usb/lp0)","text"],
    ["printer_width","Lebar Kertas (mm)","number"],
    ["receipt_footer","Footer Struk","text"],
    ["tax_rate","Pajak (%)","number"],
  ];

  return (
    <div className="p-5 max-w-lg">
      <h1 className="text-lg font-bold text-gray-800 mb-5">Setting</h1>
      <div className="bg-white rounded-lg border p-5 flex flex-col gap-4">
        {fields.map(([key, label, type]) => (
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
