# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # dev server → http://localhost:3000
npm run build    # type check + production build (run before committing)
npm run start    # serve production build

# LAN access (phone/tablet on same Wi-Fi)
npm run dev -- --hostname 0.0.0.0   # exposes dev server on all interfaces
# Then set NEXT_PUBLIC_API_URL=http://<pc-ip>:8000 in .env.local and restart
```

## Architecture

Next.js 15 App Router. Two route groups:
- `(auth)/` — login page, no navbar, no auth guard
- `(app)/` — all protected pages, shares `layout.tsx` with `<Navbar />`

`middleware.ts` runs on every request: redirects unauthenticated users to `/login`, redirects `kasir` role away from admin-only routes.

## Key Patterns

**API calls:** always use `lib/api.ts` — `api.get()`, `api.post()`, `api.put()`, `api.delete()`. It attaches the JWT token automatically and redirects to `/login` on 401. Never use raw `fetch` in components.

**Auth state:** read with `getUser()` and `getToken()` from `lib/auth.ts`. These read from cookies (set on login, cleared on logout). Server components cannot read these — keep auth reads in client components.

**Toast notifications:** import `toast` from `components/shared/Toast.tsx`. Call `toast("message", "success" | "error" | "info")`. The `<ToastContainer />` is mounted in the root layout.

**DataTable:** generic — pass `columns` with optional `render` function for custom cells, `data` array, and `keyField`. To hide a column on small screens add `className: "hidden sm:table-cell"` (or `md:` / `lg:`). Used across all data pages.

**Modal:** wraps content with a title bar and Escape key handler. Pass `width` to override `max-w-lg` (e.g. `"max-w-3xl"` for wide forms). Has `max-h-[90vh] overflow-y-auto` so tall forms scroll on mobile.

**PDF export:** `jspdf` + `jspdf-autotable`, imported dynamically (`await import()`). Used in laporan, penjualan, and purchas pages. Pattern: header → summary autoTable → detail autoTable → `doc.save()`.

## POS Screen (`/kasir`)

- Barcode input stays auto-focused via `ref` — do not add anything that steals focus
- Item rows are clickable → opens `NumpadPopup` for qty edit
- Tiered pricing resolved client-side in `resolvePrice()` — mirrors `services/pricing.py` logic
- Payment flow: `PaymentScreen` → `POST /kasir/transaksi` → `ReceiptPreview`
- After payment: items cleared, barcode input re-focused

## Environment

`NEXT_PUBLIC_API_URL` in `.env.local` — defaults to `http://localhost:8000`. All `api.ts` calls use this base URL. For LAN access (phone/tablet), set this to `http://<pc-ip>:8000` and rebuild. This value is baked in at build time — changing it requires a restart (dev) or full rebuild (production).

## LAN / Phone Access

- `next.config.ts` uses `os.networkInterfaces()` to auto-detect LAN IPs and populate `allowedDevOrigins` — this allows phones to access the HMR websocket in dev mode without the "blocked cross-origin" error.
- Backend CORS uses `allow_origin_regex` matching all private subnets — no hardcoded IPs needed.
- `NEXT_PUBLIC_API_URL` must point to the PC's LAN IP, not `localhost`, so the phone's browser can reach the backend.

## Responsive Design

All pages (`laporan`, `penjualan`, `purchas`, `keuangan`, `master`) are mobile-responsive:
- Navbar has a hamburger menu on mobile (`md:` breakpoint)
- DataTable columns use `hidden sm:table-cell` / `hidden md:table-cell` to hide lower-priority columns on small screens
- Stat card grids use `grid-cols-2` on mobile, `lg:grid-cols-4` on desktop
- Header rows use `flex-wrap gap-2` so buttons don't overflow on small screens

## Styling

Tailwind CSS only — no CSS modules or styled-components. Dark theme is disabled (removed from globals.css). Background is `bg-gray-100`, cards use `bg-white` with `border`.
