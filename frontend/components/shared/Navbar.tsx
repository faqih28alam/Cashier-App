"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getUser, clearAuth, AuthUser } from "@/lib/auth";

const NAV = [
  { href: "/kasir",    label: "KASIR",    roles: ["kasir", "admin", "owner"] },
  { href: "/purchas",  label: "PURCHAS",  roles: ["admin", "owner"] },
  { href: "/keuangan", label: "KEUANGAN", roles: ["admin", "owner"] },
  { href: "/laporan",  label: "LAPORAN",  roles: ["admin", "owner"] },
  { href: "/master",   label: "MASTER",   roles: ["admin", "owner"] },
  { href: "/setting",  label: "SETTING",  roles: ["admin", "owner"] },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    setUser(getUser());
  }, []);

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

  return (
    <nav className="bg-gray-900 text-white px-4 flex items-center h-11 gap-1 flex-shrink-0">
      <span className="text-red-500 font-bold text-sm mr-3 tracking-wide">KASIR APP</span>
      {NAV.filter((n) => user && n.roles.includes(user.role)).map((n) => (
        <Link
          key={n.href}
          href={n.href}
          className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
            pathname.startsWith(n.href)
              ? "bg-white text-gray-900"
              : "text-gray-300 hover:bg-gray-700"
          }`}
        >
          {n.label}
        </Link>
      ))}
      <div className="ml-auto flex items-center gap-3 text-xs text-gray-400">
        <span>{user?.nama}</span>
        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-medium"
        >
          LOGOFF
        </button>
      </div>
    </nav>
  );
}
