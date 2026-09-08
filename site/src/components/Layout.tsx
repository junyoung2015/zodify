import type { ReactNode } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="site-shell">
      <Navbar />
      <main>{children}</main>
      <Footer />
    </div>
  );
}
