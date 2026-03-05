import { ReactNode } from 'react';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-cyber-bg text-cyber-text font-sans antialiased selection:bg-cyber-purple selection:text-white relative overflow-x-hidden">
      <div className="fixed inset-0 bg-cyber-grid pointer-events-none z-0"></div>
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-cyber-purple/20 rounded-full blur-[120px] pointer-events-none z-0 opacity-40"></div>
      <div className="fixed bottom-0 right-0 w-[600px] h-[600px] bg-cyber-blue/10 rounded-full blur-[100px] pointer-events-none z-0 opacity-30"></div>
      
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
}
