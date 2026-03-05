import { Link, useLocation } from "react-router-dom";
import { Zap, Menu } from "lucide-react";
import { clsx } from "clsx";

export function Navbar() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className='sticky top-0 z-50 border-b border-white/5 bg-cyber-dark/80 backdrop-blur-xl'>
      <div className='max-w-7xl mx-auto px-6 h-16 flex justify-between items-center'>
        <Link to='/' className='flex items-center gap-2 group'>
          <div className='relative'>
            <div className='absolute inset-0 bg-cyber-purple blur-md opacity-50 group-hover:opacity-100 transition-opacity duration-300'></div>
            <Zap className='w-6 h-6 text-white relative z-10 fill-white' />
          </div>
          <span className='font-display font-bold text-xl tracking-tighter text-white group-hover:text-glow transition-all'>
            zodify
          </span>
          <span className='ml-2 text-[10px] font-mono text-cyber-purple bg-cyber-purple/10 border border-cyber-purple/20 px-1.5 py-0.5 rounded'>
            v0.4.1
          </span>
        </Link>

        <nav className='hidden md:flex gap-8 text-xs font-mono font-bold text-cyber-text/60'>
          {[
            { name: "HOME", path: "/" },
            { name: "BENCHMARKS", path: "/benchmarks" },
            { name: "DOCS", path: "/docs" },
            { name: "ABOUT", path: "/about" },
            { name: "GITHUB", path: "https://github.com/junyoung2015/zodify" },
            { name: "PYPI", path: "https://pypi.org/project/zodify/" },
          ].map((link) =>
            link.path.startsWith("http") ? (
              <a
                key={link.name}
                href={link.path}
                target='_blank'
                rel='noopener noreferrer'
                className='hover:text-cyber-purple hover:shadow-[0_2px_0_0_currentColor] transition-all pb-1'
              >
                {link.name}
              </a>
            ) : (
              <Link
                key={link.name}
                to={link.path}
                className={clsx(
                  "transition-all pb-1",
                  isActive(link.path)
                    ? "text-cyber-purple shadow-[0_2px_0_0_currentColor]"
                    : "hover:text-cyber-purple hover:shadow-[0_2px_0_0_currentColor]",
                )}
              >
                {link.name}
              </Link>
            ),
          )}
        </nav>

        <div className='flex items-center gap-4'>
          <button className='md:hidden text-cyber-text'>
            <Menu className='w-6 h-6' />
          </button>
        </div>
      </div>
    </header>
  );
}
