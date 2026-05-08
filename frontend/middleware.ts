import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login"];

// Routes that require admin or owner role
const RESTRICTED_PATHS = ["/keuangan", "/laporan", "/master", "/setting"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("cashier_token")?.value;
  const userRaw = request.cookies.get("cashier_user")?.value;

  if (PUBLIC_PATHS.includes(pathname)) {
    if (token) return NextResponse.redirect(new URL("/kasir", request.url));
    return NextResponse.next();
  }

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (RESTRICTED_PATHS.some((p) => pathname.startsWith(p))) {
    try {
      const user = JSON.parse(userRaw ?? "{}");
      if (user.role === "kasir") {
        return NextResponse.redirect(new URL("/kasir", request.url));
      }
    } catch {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
