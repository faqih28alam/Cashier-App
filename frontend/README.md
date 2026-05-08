# Frontend — Cashier App

Next.js frontend for the Cashier App POS system. Runs on `http://localhost:3000`.

## Stack

| | |
|---|---|
| Framework | Next.js 15 (App Router) + TypeScript |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Icons | Lucide React |
| Auth | JWT stored in cookies (`js-cookie`) |

## Setup

```bash
npm install
cp .env.local.example .env.local   # or create manually (see below)
npm run dev                         # starts on http://localhost:3000
```

**.env.local**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> Backend must be running on port 8000 before using the app.

## Commands

```bash
npm run dev      # development server with hot reload
npm run build    # production build + type check
npm run start    # serve production build
```

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/login/      # Login page (no navbar)
│   ├── (app)/             # Protected pages (with navbar)
│   │   ├── layout.tsx     # Shared layout with Navbar
│   │   ├── kasir/         # POS — main cashier screen
│   │   ├── master/        # Product CRUD
│   │   ├── purchas/       # Purchase management
│   │   ├── keuangan/      # Finance ledger
│   │   ├── laporan/       # Reports + analytics
│   │   └── setting/       # App configuration
│   ├── layout.tsx         # Root layout (ToastContainer)
│   └── page.tsx           # Redirects to /kasir
├── components/
│   ├── pos/               # POS-specific components
│   │   ├── NumpadPopup    # Quantity input overlay
│   │   ├── PaymentScreen  # Payment modal with numpad
│   │   └── ReceiptPreview # Receipt popup after payment
│   └── shared/
│       ├── Navbar         # Top navigation bar
│       ├── DataTable      # Reusable table component
│       ├── Modal          # Generic modal wrapper
│       └── Toast          # Toast notification system
├── lib/
│   ├── api.ts             # Fetch wrapper → backend API
│   └── auth.ts            # JWT cookie helpers
└── middleware.ts           # Route protection by role
```

## Pages & Access

| Route | Role Access | Description |
|---|---|---|
| `/login` | Public | Login form |
| `/kasir` | All | POS cashier screen |
| `/master` | Admin, Owner | Product CRUD |
| `/purchas` | Admin, Owner | Purchase management |
| `/keuangan` | Admin, Owner | Cash flow ledger |
| `/laporan` | Admin, Owner | Sales reports + charts |
| `/setting` | Admin, Owner | Store & printer config |

## Barcode Scanner

The scanner works in USB HID mode — it sends keystrokes directly into the browser. The `/kasir` page keeps the barcode input auto-focused at all times. No driver or extra configuration needed.
