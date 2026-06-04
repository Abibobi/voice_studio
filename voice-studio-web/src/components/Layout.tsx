import type { ReactNode } from "react";
import Navbar from "./Navbar";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      {/* Animated background orbs */}
      <div className="bg-orbs" aria-hidden="true">
        <div className="orb orb--purple" />
        <div className="orb orb--blue" />
        <div className="orb orb--cyan" />
      </div>

      <div className="app">
        <Navbar />
        <main className="page-enter">{children}</main>
      </div>
    </>
  );
}
