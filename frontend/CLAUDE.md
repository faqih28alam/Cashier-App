# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # dev server → http://localhost:3000
npm run build    # type check + production build (run before committing)
npm run start    # serve production build
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

**DataTable:** generic — pass `columns` with optional `render` function for custom cells, `data` array, and `keyField`. Used in master, purchas, keuangan, laporan.

**Modal:** wraps content with a title bar and Escape key handler. Pass `width` to override `max-w-lg` (e.g. `"max-w-3xl"` for wide forms).

## POS Screen (`/kasir`)

- Barcode input stays auto-focused via `ref` — do not add anything that steals focus
- Item rows are clickable → opens `NumpadPopup` for qty edit
- Tiered pricing resolved client-side in `resolvePrice()` — mirrors `services/pricing.py` logic
- Payment flow: `PaymentScreen` → `POST /kasir/transaksi` → `ReceiptPreview`
- After payment: items cleared, barcode input re-focused

## Environment

`NEXT_PUBLIC_API_URL` in `.env.local` — defaults to `http://localhost:8000`. All `api.ts` calls use this base URL.

## Styling

Tailwind CSS only — no CSS modules or styled-components. Dark theme is disabled (removed from globals.css). Background is `bg-gray-100`, cards use `bg-white` with `border`.
