import { Github, Package } from "lucide-react";

export function Footer() {
  return (
    <footer className='py-12 border-t border-white/5 mt-auto'>
      <div className='max-w-7xl mx-auto px-6 text-center'>
        <div className='flex justify-center items-center gap-6 mb-8 text-cyber-text/40'>
          <a
            href='https://github.com/junyoung2015/zodify'
            target='_blank'
            rel='noopener noreferrer'
            className='hover:text-cyber-purple transition-colors'
          >
            <Github className='w-5 h-5' />
          </a>
          <a
            href='https://pypi.org/project/zodify/'
            target='_blank'
            rel='noopener noreferrer'
            className='hover:text-cyber-purple transition-colors'
          >
            <Package className='w-5 h-5' />
          </a>
        </div>
        <p className='font-mono text-[10px] uppercase tracking-[0.2em] text-cyber-text/30'>
          © 2026 zodify <span className='mx-2 text-cyber-purple'>•</span>{" "}
          Lightweight Python dict validation
        </p>
      </div>
    </footer>
  );
}
