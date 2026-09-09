import type { ReactNode } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
export function Layout({ children, path }: { children: ReactNode; path: string }) {
  return (
    <div className="site-shell">
      <Navbar path={path} />
      <main>{children}</main>
      <Footer />
    </div>
  );
}
