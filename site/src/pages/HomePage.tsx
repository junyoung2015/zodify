import { Helmet } from "react-helmet-async";
import { motion } from "framer-motion";
import {
  Zap,
  Activity,
  Cpu,
  Box,
  Download,
  Check,
  FileCode,
  Layers,
  ShieldCheck,
  Settings,
} from "lucide-react";

const benchmarks = [
  { name: "cerberus", value: 10000, ops: "10K", color: "bg-cyber-text/10" },
  { name: "schema", value: 43000, ops: "43K", color: "bg-cyber-text/15" },
  { name: "voluptuous", value: 289000, ops: "289K", color: "bg-cyber-text/20" },
  {
    name: "zodify",
    value: 615000,
    ops: "615K",
    color: "bg-gradient-to-t from-cyber-purple to-cyber-neon",
  },
  {
    name: "pydantic v2",
    value: 1300000,
    ops: "1.3M",
    color: "bg-cyber-text/25",
  },
];

const maxValue = 1300000;

export function HomePage() {
  return (
    <div className='flex flex-col gap-20 pb-20'>
      <Helmet>
        <title>zodify - Fastest Pure-Python Validation Library</title>
        <meta
          name='description'
          content='Zero-dependency Python dict validation with 615K ops/sec, recursive schemas, type coercion, and first-class type-checker support. 402 LOC, 48KB installed.'
        />
        <link rel='canonical' href='https://zodify.dev/' />
        <script type='application/ld+json'>
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: "What is zodify?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "zodify is the fastest pure-Python validation library. It validates Python dicts at 615,000 operations per second with zero dependencies, a single 402-line source file, and a 48KB install size. The API is schema-first: validate(schema, data).",
                },
              },
              {
                "@type": "Question",
                name: "When should I use zodify instead of Pydantic?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "Use zodify when you need lightweight validation without heavy frameworks - scripts, CLI tools, microservices, serverless functions, or any project where a 7.8MB install with 4 transitive dependencies feels excessive. Pydantic v2 is faster (Rust core, 1.3M ops/sec) but zodify is 162x smaller (48KB vs 7.8MB) and imports 10x faster (4ms vs 44ms).",
                },
              },
              {
                "@type": "Question",
                name: "Does zodify have any dependencies?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "No. zodify has zero dependencies - it uses only Python's standard library. The entire library is a single file (402 lines of code, 48KB installed). This means zero supply-chain risk and trivial auditing.",
                },
              },
              {
                "@type": "Question",
                name: "What Python versions does zodify support?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "zodify requires Python 3.10 or higher. This is because it uses the native str | int union type syntax introduced in Python 3.10 (PEP 604).",
                },
              },
              {
                "@type": "Question",
                name: "Is zodify production-ready?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "zodify is in alpha (v0.4.1). The API is stable for current features but may expand. It has 263 tests with strict type checking enforced by mypy and pyright as merge-blocking CI gates. Automated PyPI publishing on every version tag.",
                },
              },
            ],
          })}
        </script>
      </Helmet>
      {/* Hero Section */}
      <section className='pt-20 pb-12 px-6 flex flex-col items-center text-center'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className='inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyber-purple/10 border border-cyber-purple/20 text-cyber-purple text-xs font-mono mb-8 backdrop-blur-sm'
        >
          <Zap className='w-3 h-3' />
          FASTEST PURE-PYTHON VALIDATION
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className='font-display font-extrabold text-5xl md:text-7xl mb-6 leading-[0.9] tracking-tighter text-white drop-shadow-lg'
        >
          Lightweight Python <br />
          <span className='text-transparent bg-clip-text bg-gradient-to-r from-cyber-purple via-cyber-neon to-cyber-blue text-glow'>
            dict validation
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className='text-lg text-cyber-text/70 leading-relaxed font-light mb-8 max-w-xl mx-auto'
        >
          Zero dependencies. Single file. Type-checked schemas. <br />
          Validate dicts in microseconds with pure Python.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className='flex flex-col sm:flex-row gap-4 items-center'
        >
          <div className='relative group'>
            <div className='bg-cyber-dark border border-white/10 rounded-lg px-6 py-3 font-mono text-sm text-cyber-text/80 flex items-center gap-3 group-hover:border-cyber-purple/50 transition-colors'>
              <span className='text-cyber-purple'>$</span>
              <span>pip install zodify</span>
            </div>
          </div>
          <a
            href='https://github.com/junyoung2015/zodify'
            target='_blank'
            rel='noopener noreferrer'
            className='text-sm font-mono text-cyber-text/50 hover:text-cyber-purple transition-colors'
          >
            View on GitHub →
          </a>
        </motion.div>
      </section>

      {/* Stats Bar */}
      <section className='px-6 max-w-4xl mx-auto w-full'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className='grid grid-cols-2 md:grid-cols-6 gap-4'
        >
          {[
            { label: "VERSION", value: "v0.4.1" },
            { label: "OPS/SEC", value: "615K" },
            { label: "SIZE", value: "48KB" },
            { label: "DEPS", value: "0" },
            { label: "TESTS", value: "263" },
            { label: "LOC", value: "402" },
          ].map((stat, i) => (
            <div
              key={stat.label}
              className='glass-panel rounded-lg p-4 text-center'
            >
              <div className='text-[10px] font-mono text-cyber-text/40 uppercase tracking-widest mb-1'>
                {stat.label}
              </div>
              <div className='font-mono font-bold text-white text-lg'>
                {stat.value}
              </div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Code Demo */}
      <section className='px-6 max-w-3xl mx-auto w-full'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className='relative group'
        >
          <div className='absolute -inset-1 bg-gradient-to-r from-cyber-purple to-cyber-blue opacity-20 blur rounded-xl group-hover:opacity-30 transition-opacity duration-500'></div>
          <div className='relative rounded-xl bg-[#0d0b16] border border-white/10 overflow-hidden'>
            <div className='flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5'>
              <div className='flex gap-1.5'>
                <div className='w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50'></div>
                <div className='w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50'></div>
                <div className='w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50'></div>
              </div>
              <span className='text-xs font-mono text-cyber-text/30'>
                example.py
              </span>
            </div>
            <div className='p-6 overflow-x-auto'>
              <pre className='font-mono text-sm leading-relaxed'>
                <code>
                  <span className='text-cyber-purple'>from</span>{" "}
                  <span className='text-cyber-neon'>zodify</span>{" "}
                  <span className='text-cyber-purple'>import</span> validate
                  {"\n"}
                  {"\n"}
                  <span className='text-slate-500 italic'>
                    # Define a schema as a plain dict
                  </span>
                  {"\n"}
                  schema = {"{"}
                  <span className='text-green-400'>"name"</span>:{" "}
                  <span className='text-cyber-blue'>str</span>,{" "}
                  <span className='text-green-400'>"age"</span>:{" "}
                  <span className='text-cyber-blue'>int</span>
                  {"}"}
                  {"\n"}
                  data = {"{"}
                  <span className='text-green-400'>"name"</span>:{" "}
                  <span className='text-green-400'>"Alice"</span>,{" "}
                  <span className='text-green-400'>"age"</span>:{" "}
                  <span className='text-orange-400'>30</span>
                  {"}"}
                  {"\n"}
                  {"\n"}
                  result = <span className='text-cyber-purple'>validate</span>
                  (schema, data){"\n"}
                  <span className='text-slate-500 italic'>
                    # → {"{"}&#39;name&#39;: &#39;Alice&#39;, &#39;age&#39;: 30
                    {"}"}
                  </span>
                  {"\n"}
                  {"\n"}
                  <span className='text-slate-500 italic'>
                    # Type mismatch raises ValueError
                  </span>
                  {"\n"}
                  <span className='text-cyber-purple'>
                    validate
                  </span>(schema, {"{"}
                  <span className='text-green-400'>"name"</span>:{" "}
                  <span className='text-green-400'>"Alice"</span>,{" "}
                  <span className='text-green-400'>"age"</span>:{" "}
                  <span className='text-green-400'>"thirty"</span>
                  {"}"}){"\n"}
                  <span className='text-slate-500 italic'>
                    # → ValueError: age: expected int, got str
                  </span>
                </code>
              </pre>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Benchmark Chart */}
      <section className='px-6 max-w-5xl mx-auto w-full'>
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className='glass-panel p-8 md:p-12 rounded-2xl relative overflow-hidden box-glow'
        >
          <div className='flex justify-between items-end mb-8 border-b border-white/5 pb-4'>
            <div>
              <h3 className='font-mono text-xl text-white font-bold'>
                Validation Speed (ops/sec)
              </h3>
              <p className='text-xs text-cyber-text/50 font-mono mt-1'>
                3-key dict • Python 3.10 • Apple Silicon • Higher is better
              </p>
            </div>
            <div className='hidden md:flex gap-4'>
              <div className='flex items-center gap-2'>
                <span className='w-3 h-3 rounded-sm bg-cyber-purple'></span>
                <span className='text-xs font-mono text-cyber-text/70'>
                  zodify (pure Python)
                </span>
              </div>
              <div className='flex items-center gap-2'>
                <span className='w-3 h-3 rounded-sm bg-cyber-text/30'></span>
                <span className='text-xs font-mono text-cyber-text/70'>
                  Others
                </span>
              </div>
            </div>
          </div>

          <div className='relative h-[400px] w-full flex flex-col justify-end'>
            {/* Grid lines */}
            <div className='absolute inset-0 flex flex-col justify-between pointer-events-none text-cyber-text/20 font-mono text-xs z-0'>
              {["1.3M", "975K", "650K", "325K", "0"].map((val) => (
                <div
                  key={val}
                  className='w-full border-t border-white/5 h-0 flex items-center'
                >
                  <span className='-mt-6'>{val}</span>
                </div>
              ))}
            </div>

            <div className='relative z-10 flex justify-around items-end h-[360px] pl-12 gap-2 md:gap-6'>
              {benchmarks.map((bench, index) => (
                <div
                  key={bench.name}
                  className='flex flex-col items-center w-full max-w-[120px] group relative'
                >
                  {bench.name === "zodify" && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 1, duration: 0.5 }}
                      className='absolute -top-12 bg-cyber-purple text-white text-xs font-bold px-3 py-1 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.5)]'
                    >
                      Fastest pure-Python
                    </motion.div>
                  )}

                  <div
                    className={`text-xs font-mono ${bench.name === "zodify" ? "text-cyber-purple font-bold" : "text-cyber-text/50"} mb-2 opacity-0 group-hover:opacity-100 transition-opacity`}
                  >
                    {bench.ops} ops/sec
                  </div>

                  <motion.div
                    initial={{ height: 0 }}
                    whileInView={{
                      height: `${(bench.value / maxValue) * 100}%`,
                    }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: index * 0.15 }}
                    className={`w-full ${bench.color} rounded-t-lg relative min-h-[4px] group-hover:brightness-110 transition-all shadow-lg`}
                  >
                    {bench.name === "zodify" && (
                      <div className='absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity'></div>
                    )}
                  </motion.div>

                  <div
                    className={`mt-4 font-mono font-bold text-xs tracking-wider uppercase ${bench.name === "zodify" ? "text-white text-glow" : "text-cyber-text/50"}`}
                  >
                    {bench.name}
                  </div>
                  {bench.name === "pydantic v2" && (
                    <div className='text-[9px] font-mono text-cyber-text/30 mt-1'>
                      (Rust core)
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </section>

      <div className='max-w-7xl mx-auto w-full px-6'>
        <div className='w-full h-px bg-gradient-to-r from-transparent via-cyber-border to-transparent opacity-50'></div>
      </div>

      {/* Features Section */}
      <section className='px-6 max-w-7xl mx-auto w-full'>
        <div className='text-center mb-16'>
          <h2 className='font-display font-bold text-3xl md:text-4xl text-white mb-4'>
            Why <span className='text-cyber-purple'>zodify?</span>
          </h2>
          <p className='text-cyber-text/60 max-w-2xl mx-auto'>
            One file. Zero dependencies. Validate Python dicts with type-checked
            schemas.
          </p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          {[
            {
              icon: <Box className='w-6 h-6 text-cyber-purple' />,
              title: "Zero Dependencies",
              desc: "No external packages. No transitive dependency trees. Just Python's standard library.",
              stat: "DEPS: 0",
              status: "OPTIMAL",
            },
            {
              icon: <FileCode className='w-6 h-6 text-cyber-purple' />,
              title: "Single File",
              desc: "The entire library is one Python file - 402 lines of logic. Easy to audit, vendor, or understand.",
              stat: "LOC: 402",
              status: "OPTIMAL",
            },
            {
              icon: <Activity className='w-6 h-6 text-cyber-purple' />,
              title: "615K ops/sec",
              desc: "Fastest pure-Python validation library. 2.1x faster than voluptuous, 14x faster than schema.",
              stat: "LATENCY: 1.62µs",
              status: "OPTIMAL",
            },
            {
              icon: <Cpu className='w-6 h-6 text-cyber-purple' />,
              title: "4.2ms Import",
              desc: "Start validating instantly. No heavy framework initialization - 10x faster import than Pydantic.",
              stat: "IMPORT: 4.2ms",
              status: "OPTIMAL",
            },
            {
              icon: <Layers className='w-6 h-6 text-cyber-purple' />,
              title: "Union Types & Nesting",
              desc: "Support for str | int union types (Python 3.10+), Optional keys, and deeply nested dict schemas.",
              stat: "TYPES: full",
              status: "OPTIMAL",
            },
            {
              icon: <ShieldCheck className='w-6 h-6 text-cyber-purple' />,
              title: "Structured Errors",
              desc: "Detailed error paths, expected vs actual types, and missing key reports. Debug in seconds.",
              stat: "SIZE: 48KB",
              status: "OPTIMAL",
            },
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className='glass-panel p-6 rounded-xl border border-white/5 hover:border-cyber-purple/40 transition-colors group'
            >
              <div className='w-12 h-12 rounded-lg bg-cyber-purple/10 flex items-center justify-center mb-6 group-hover:bg-cyber-purple/20 transition-colors'>
                {feature.icon}
              </div>
              <h3 className='font-display font-bold text-xl text-white mb-3'>
                {feature.title}
              </h3>
              <p className='text-sm text-cyber-text/60 leading-relaxed mb-6'>
                {feature.desc}
              </p>
              <div className='mt-auto pt-6 border-t border-white/5 flex justify-between items-center text-xs font-mono text-cyber-text/40'>
                <span>{feature.stat}</span>
                <span className='text-green-400'>{feature.status}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* FAQ Section */}
      <section className='px-6 max-w-5xl mx-auto w-full'>
        <div className='text-center mb-12'>
          <h2 className='font-display font-bold text-3xl md:text-4xl text-white mb-4'>
            Frequently Asked{" "}
            <span className='text-cyber-purple'>Questions</span>
          </h2>
        </div>
        <div className='space-y-4'>
          {[
            {
              q: "What is zodify?",
              a: "zodify is the fastest pure-Python validation library. It validates Python dicts at 615,000 operations per second with zero dependencies, a single 402-line source file, and a 48KB install size. The API is schema-first: validate(schema, data).",
            },
            {
              q: "When should I use zodify instead of Pydantic?",
              a: "Use zodify when you need lightweight validation without heavy frameworks - scripts, CLI tools, microservices, serverless functions, or any project where a 7.8MB install with 4 transitive dependencies feels excessive. Pydantic v2 is faster (Rust core, 1.3M ops/sec) but zodify is 162x smaller (48KB vs 7.8MB) and imports 10x faster (4ms vs 44ms).",
            },
            {
              q: "Does zodify have any dependencies?",
              a: "No. zodify has zero dependencies - it uses only Python's standard library. The entire library is a single file (402 lines of code, 48KB installed). This means zero supply-chain risk and trivial auditing.",
            },
            {
              q: "What Python versions does zodify support?",
              a: "zodify requires Python 3.10 or higher. This is because it uses the native str | int union type syntax introduced in Python 3.10 (PEP 604).",
            },
            {
              q: "Is zodify production-ready?",
              a: "zodify is in alpha (v0.4.1). The API is stable for current features but may expand. It has 263 tests with strict type checking enforced by mypy and pyright as merge-blocking CI gates. Automated PyPI publishing on every version tag.",
            },
          ].map((item, i) => (
            <details
              key={i}
              className='glass-panel rounded-xl border border-white/5 hover:border-cyber-purple/30 transition-colors group'
            >
              <summary className='px-6 py-5 cursor-pointer font-display font-bold text-white text-lg flex items-center justify-between list-none'>
                <span>{item.q}</span>
                <span className='text-cyber-purple text-xl ml-4 group-open:rotate-45 transition-transform'>
                  +
                </span>
              </summary>
              <div className='px-6 pb-5 text-cyber-text/70 leading-relaxed'>
                {item.a}
              </div>
            </details>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className='py-20 px-6 text-center relative'>
        <div className='absolute inset-0 bg-cyber-purple/5 blur-3xl -z-10 rounded-full transform scale-75'></div>
        <h2 className='font-display font-bold text-3xl mb-4 tracking-tight text-white'>
          Get started in <span className='text-cyber-purple'>seconds</span>
        </h2>
        <p className='text-cyber-text/50 font-mono text-sm mb-8'>
          pip install zodify
        </p>
        <div className='flex justify-center gap-4'>
          <a
            href='https://pypi.org/project/zodify/'
            target='_blank'
            rel='noopener noreferrer'
            className='relative px-8 py-3 bg-cyber-purple/10 text-cyber-purple border border-cyber-purple/50 font-mono text-sm uppercase tracking-widest font-bold hover:bg-cyber-purple hover:text-white transition-all duration-300 group overflow-hidden rounded flex items-center gap-2'
          >
            <span className='relative z-10 flex items-center gap-2'>
              Install from PyPI
              <Download className='w-4 h-4 group-hover:translate-y-0.5 transition-transform' />
            </span>
            <div className='absolute inset-0 bg-cyber-purple/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300'></div>
          </a>
          <a
            href='https://github.com/junyoung2015/zodify'
            target='_blank'
            rel='noopener noreferrer'
            className='px-8 py-3 border border-white/10 text-cyber-text/60 font-mono text-sm uppercase tracking-widest font-bold hover:border-white/30 hover:text-white transition-all duration-300 rounded flex items-center gap-2'
          >
            GitHub
          </a>
        </div>
      </section>

      {/* Last Updated */}
      <div className='text-center text-xs font-mono text-cyber-text/30'>
        Last updated: March 5, 2026
      </div>
    </div>
  );
}
