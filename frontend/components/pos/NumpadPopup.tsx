"use client";
import { useState, useEffect } from "react";

interface Props {
  productName: string;
  unit: string;
  initialQty: number;
  onConfirm: (qty: number) => void;
  onCancel: () => void;
}

export function NumpadPopup({ productName, unit, initialQty, onConfirm, onCancel }: Props) {
  const [value, setValue] = useState(String(initialQty));

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key >= "0" && e.key <= "9") setValue((v) => (v === "0" ? e.key : v + e.key));
      else if (e.key === "Backspace") setValue((v) => v.length > 1 ? v.slice(0, -1) : "0");
      else if (e.key === "Enter") handleConfirm();
      else if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  });

  function press(key: string) {
    if (key === "←") setValue((v) => v.length > 1 ? v.slice(0, -1) : "0");
    else if (key === "00") setValue((v) => v === "0" ? "0" : v + "00");
    else setValue((v) => v === "0" ? key : v + key);
  }

  function handleConfirm() {
    const qty = parseInt(value, 10);
    if (qty > 0) onConfirm(qty);
  }

  const keys = ["1","2","3","4","5","6","7","8","9","0","00","←"];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl w-72">
        <div className="bg-gray-800 text-white px-4 py-3 rounded-t-lg">
          <p className="text-xs text-gray-400 truncate">{productName}</p>
          <p className="text-3xl font-bold tracking-widest text-right">{value} <span className="text-lg font-normal">{unit}</span></p>
        </div>
        <div className="grid grid-cols-3 gap-1 p-3">
          {keys.map((k) => (
            <button
              key={k}
              onClick={() => press(k)}
              className="bg-gray-100 hover:bg-gray-200 active:bg-gray-300 rounded py-3 text-lg font-semibold"
            >
              {k}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-2 px-3 pb-3">
          <button onClick={onCancel} className="bg-red-500 hover:bg-red-600 text-white py-2 rounded font-medium">✗ Batal</button>
          <button onClick={handleConfirm} className="bg-green-600 hover:bg-green-700 text-white py-2 rounded font-medium">✓ OK</button>
        </div>
      </div>
    </div>
  );
}
