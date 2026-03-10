import { Helmet } from "react-helmet-async";
import { motion } from "framer-motion";
import {
  Activity,
  Clock,
  HardDrive,
  Package,
  FlaskConical,
  ExternalLink,
} from "lucide-react";

import { SITE_LAST_UPDATED, SITE_NUMBERS } from "../siteMeta";

const validationData = [
  {
    lib: "zodify",
    ops: 533333,
    opsLabel: "533K",
    latency: "1.87µs",
    highlight: true,
  },
  {
    lib: "pydantic v2",
    ops: 1499251,
    opsLabel: "1.50M",
    latency: "0.67µs",
    highlight: false,
    note: "Rust core",
  },
  {
    lib: "voluptuous",
    ops: 218198,
    opsLabel: "218K",
    latency: "4.58µs",
    highlight: false,
  },
  {
    lib: "schema",
    ops: 38772,
    opsLabel: "38.8K",
    latency: "25.79µs",
    highlight: false,
  },
  {
    lib: "cerberus",
    ops: 8466,
    opsLabel: "8.5K",
    latency: "118.12µs",
    highlight: false,
  },
];

const importData = [
  { lib: "zodify", time: 2.3, highlight: true },
  { lib: "schema", time: 5.4, highlight: false },
  { lib: "voluptuous", time: 10.8, highlight: false },
  { lib: "cerberus", time: 28.4, highlight: false },
  { lib: "pydantic v2", time: 39.4, highlight: false },
];

const sizeData = [
  { lib: "zodify", size: "78KB", sizeBytes: 77962, deps: 0, highlight: true },
  { lib: "schema", size: "101KB", sizeBytes: 100801, deps: 0, highlight: false },
  {
    lib: "voluptuous",
    size: "213KB",
    sizeBytes: 213121,
    deps: 0,
    highlight: false,
  },
  {
    lib: "cerberus",
    size: "215KB",
    sizeBytes: 215457,
    deps: 0,
    highlight: false,
  },
  {
    lib: "pydantic v2",
    size: "8.1MB",
    sizeBytes: 8099203,
    deps: 4,
    highlight: false,
  },
];

const maxOps = 1500000;
const maxImport = 50;

export function BenchmarksPage() {
  return (
    <div className='max-w-5xl mx-auto px-6 pt-12 pb-20'>
      <Helmet>
        <title>Benchmarks - zodify</title>
        <meta
          name='description'
          content='Performance benchmarks comparing zodify against pydantic, voluptuous, schema, and cerberus. 533K ops/sec, 78KB installed, 2.3ms import time.'
        />
        <link rel='canonical' href='https://zodify.dev/benchmarks' />
        <script type='application/ld+json'>
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: "Is zodify faster than Pydantic?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "No. Pydantic v2 uses a Rust-compiled core and achieves about 1.50M ops/sec vs zodify's 533K ops/sec in the latest local comparison run. However, zodify is the fastest pure-Python validation library - 2.4x faster than voluptuous, 13.8x faster than schema, and 63x faster than cerberus. zodify is also about 104x smaller and imports about 17x faster than Pydantic in the latest local run.",
                },
              },
              {
                "@type": "Question",
                name: "How were these benchmarks measured?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "Validation comparisons use benchmarks/comparison_bench.py on Python 3.10.19 / Apple Silicon (ARM64): 500 warmups plus 10,000 measured single-call runs on a 3-key flat dict. Import time uses 30 fresh subprocess imports per library. Install size reflects a clean wheel-based virtual environment footprint including dependencies.",
                },
              },
              {
                "@type": "Question",
                name: "Can I reproduce these benchmarks?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "Yes. Clone the repo, create a fresh virtual environment, install zodify plus the comparison libraries, then run python benchmarks/comparison_bench.py for the head-to-head validation results and python benchmarks/bench_import.py for import timings.",
                },
              },
              {
                "@type": "Question",
                name: "Why is zodify's import time so much faster?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: `zodify has zero dependencies and a compact Python runtime (${SITE_NUMBERS.sourceLoc} source LOC, ${SITE_NUMBERS.size} installed). There is no Rust compilation, no framework initialization, and no transitive dependency loading. This gives a ${SITE_NUMBERS.importMs} import time vs Pydantic's 39.4ms in the latest local run.`,
                },
              },
            ],
          })}
        </script>
      </Helmet>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className='mb-12 border-b border-white/10 pb-8'>
          <div className='flex items-center gap-3 text-xs font-mono text-cyber-purple mb-4'>
            <span className='opacity-70'>BENCHMARKS</span>
            <span className='opacity-50'>/</span>
            <span className='opacity-70'>COMPARISONS</span>
          </div>
          <h1 className='font-display font-extrabold text-4xl md:text-5xl text-white mb-4 tracking-tight'>
            Benchmarks
          </h1>
          <p className='text-lg text-cyber-text/70 leading-relaxed font-light'>
            Head-to-head performance comparison from the latest local run
            across five Python validation libraries. All numbers are
            reproducible from the source repo.
          </p>
        </div>

        {/* Stats Summary */}
        <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-12'>
          {[
            { label: "ZODIFY OPS/SEC", value: "533K" },
            { label: "IMPORT TIME", value: "2.3ms" },
            { label: "INSTALL SIZE", value: "78KB" },
            { label: "DEPENDENCIES", value: "0" },
          ].map((stat) => (
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
        </div>

        {/* Validation Speed */}
        <section className='mb-16'>
          <div className='flex items-center gap-3 mb-8'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <Activity className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                Validation Speed
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                Operations per second (3-key dict)
              </p>
            </div>
          </div>

          <div className='glass-panel rounded-xl p-6 md:p-8 mb-6'>
            <div className='space-y-4'>
              {validationData.map((item, i) => (
                <motion.div
                  key={item.lib}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className='flex items-center gap-4'
                >
                  <div
                    className={`w-28 shrink-0 text-right font-mono text-sm ${item.highlight ? "text-cyber-purple font-bold" : "text-cyber-text/60"}`}
                  >
                    {item.lib}
                    {item.note && (
                      <span className='text-[10px] text-cyber-text/30 block'>
                        {item.note}
                      </span>
                    )}
                  </div>
                  <div className='flex-grow h-8 bg-white/5 rounded overflow-hidden relative'>
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(item.ops / maxOps) * 100}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: i * 0.1 }}
                      className={`h-full rounded ${item.highlight ? "bg-gradient-to-r from-cyber-purple to-cyber-neon" : "bg-white/10"}`}
                    />
                  </div>
                  <div
                    className={`w-24 shrink-0 font-mono text-sm ${item.highlight ? "text-white font-bold" : "text-cyber-text/50"}`}
                  >
                    {item.opsLabel}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <div className='glass-panel rounded-lg p-4 border border-cyber-purple/20 bg-cyber-purple/5'>
            <p className='text-sm text-cyber-text/70'>
              <span className='text-cyber-purple font-bold'>Note:</span>{" "}
              Pydantic v2 uses a Rust-compiled core, making it ~2.8x faster than
              zodify. Among <strong className='text-white'>pure-Python</strong>{" "}
              libraries, zodify is the fastest - 2.4x faster than voluptuous,
              13.8x faster than schema, and 63x faster than cerberus.
            </p>
          </div>
        </section>

        {/* Import Time */}
        <section className='mb-16'>
          <div className='flex items-center gap-3 mb-8'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <Clock className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                Import Time
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                Time to import the library (ms)
              </p>
            </div>
          </div>

          <div className='glass-panel rounded-xl p-6 md:p-8'>
            <div className='space-y-4'>
              {importData.map((item, i) => (
                <motion.div
                  key={item.lib}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className='flex items-center gap-4'
                >
                  <div
                    className={`w-28 shrink-0 text-right font-mono text-sm ${item.highlight ? "text-cyber-purple font-bold" : "text-cyber-text/60"}`}
                  >
                    {item.lib}
                  </div>
                  <div className='flex-grow h-8 bg-white/5 rounded overflow-hidden relative'>
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{
                        width: `${(item.time / maxImport) * 100}%`,
                      }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: i * 0.1 }}
                      className={`h-full rounded ${item.highlight ? "bg-gradient-to-r from-cyber-purple to-cyber-neon" : "bg-white/10"}`}
                    />
                  </div>
                  <div
                    className={`w-20 shrink-0 font-mono text-sm ${item.highlight ? "text-white font-bold" : "text-cyber-text/50"}`}
                  >
                    {item.time}ms
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Install Size */}
        <section className='mb-16'>
          <div className='flex items-center gap-3 mb-8'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <HardDrive className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                Install Size & Dependencies
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                Total package size and dependency count
              </p>
            </div>
          </div>

          <div className='w-full rounded-xl border border-white/10 overflow-x-auto'>
            <table className='w-full text-sm text-left min-w-[560px]'>
              <thead className='bg-white/5 text-cyber-text/60 font-mono text-xs uppercase'>
                <tr>
                  <th className='px-3 md:px-6 py-3 font-medium'>Library</th>
                  <th className='px-3 md:px-6 py-3 font-medium'>Validation</th>
                  <th className='px-3 md:px-6 py-3 font-medium'>Import</th>
                  <th className='px-3 md:px-6 py-3 font-medium'>
                    Install Size
                  </th>
                  <th className='px-6 py-3 font-medium'>Dependencies</th>
                </tr>
              </thead>
              <tbody className='divide-y divide-white/5'>
                {[
                  {
                    lib: "zodify",
                    ops: "533K ops/sec (1.87µs)",
                    imp: "2.3ms",
                    size: "78KB",
                    deps: "0",
                    highlight: true,
                  },
                  {
                    lib: "pydantic v2",
                    ops: "1.50M ops/sec (0.67µs)",
                    imp: "39.4ms",
                    size: "8.1MB",
                    deps: "4",
                    highlight: false,
                  },
                  {
                    lib: "voluptuous",
                    ops: "218K ops/sec (4.58µs)",
                    imp: "10.8ms",
                    size: "213KB",
                    deps: "0",
                    highlight: false,
                  },
                  {
                    lib: "schema",
                    ops: "38.8K ops/sec (25.79µs)",
                    imp: "5.4ms",
                    size: "101KB",
                    deps: "0",
                    highlight: false,
                  },
                  {
                    lib: "cerberus",
                    ops: "8.5K ops/sec (118.12µs)",
                    imp: "28.4ms",
                    size: "215KB",
                    deps: "0",
                    highlight: false,
                  },
                ].map((row) => (
                  <tr
                    key={row.lib}
                    className={`${row.highlight ? "bg-cyber-purple/5" : "bg-cyber-glass"} hover:bg-white/5 transition-colors`}
                  >
                    <td
                      className={`px-6 py-4 font-mono ${row.highlight ? "text-cyber-purple font-bold" : "text-cyber-text/70"}`}
                    >
                      {row.lib}
                    </td>
                    <td
                      className={`px-6 py-4 font-mono ${row.highlight ? "text-white font-bold" : "text-cyber-text/60"} text-xs`}
                    >
                      {row.ops}
                    </td>
                    <td
                      className={`px-6 py-4 font-mono ${row.highlight ? "text-white font-bold" : "text-cyber-text/60"}`}
                    >
                      {row.imp}
                    </td>
                    <td
                      className={`px-6 py-4 font-mono ${row.highlight ? "text-white font-bold" : "text-cyber-text/60"}`}
                    >
                      {row.size}
                    </td>
                    <td
                      className={`px-6 py-4 font-mono ${row.highlight ? "text-white font-bold" : "text-cyber-text/60"}`}
                    >
                      {row.deps}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Methodology */}
        <section className='mb-16'>
          <div className='flex items-center gap-3 mb-8'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <FlaskConical className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                Methodology
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                How these benchmarks were measured
              </p>
            </div>
          </div>

          <div className='glass-panel rounded-xl p-6 md:p-8 space-y-4'>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              {[
                { label: "Python Version", value: "3.10.19" },
                { label: "Hardware", value: "Apple Silicon (ARM64)" },
                {
                  label: "Validation Payload",
                  value: "3-key flat dict (str, int, bool)",
                },
                { label: "Validation Runs", value: "500 warmups + 10,000 measured single-call runs" },
                { label: "Timing", value: "statistics.median over per-call timings" },
                {
                  label: "Import Timing",
                  value: "30 fresh subprocess imports per library",
                },
              ].map((item) => (
                <div key={item.label} className='flex flex-col gap-1'>
                  <span className='text-xs font-mono text-cyber-text/40 uppercase tracking-widest'>
                    {item.label}
                  </span>
                  <span className='text-sm text-cyber-text/80'>
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Reproduce */}
        <section className='mb-16'>
          <div className='flex items-center gap-3 mb-6'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <Package className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                Reproduce
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                Run the benchmarks yourself
              </p>
            </div>
          </div>

          <div className='relative rounded-xl bg-[#0d0b16] border border-white/10 overflow-hidden mb-6'>
            <div className='flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5'>
              <div className='flex gap-1.5'>
                <div className='w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50'></div>
                <div className='w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50'></div>
                <div className='w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50'></div>
              </div>
              <span className='text-xs font-mono text-cyber-text/30'>
                terminal
              </span>
            </div>
            <div className='p-6 overflow-x-auto'>
              <pre className='font-mono text-sm leading-relaxed text-cyber-text/80'>
                {`$ git clone https://github.com/junyoung2015/zodify
$ cd zodify
$ python -m venv .venv
$ .venv/bin/pip install -e ".[dev]" pydantic cerberus voluptuous schema
$ .venv/bin/python benchmarks/comparison_bench.py
$ .venv/bin/python benchmarks/bench_import.py`}
              </pre>
            </div>
          </div>
          <p className='text-cyber-text/60 text-sm leading-relaxed mb-6'>
            Install-size totals come from a clean wheel-based virtual
            environment and may vary slightly by platform or dependency version.
          </p>

          <a
            href='https://github.com/junyoung2015/zodify/tree/main/benchmarks'
            target='_blank'
            rel='noopener noreferrer'
            className='inline-flex items-center gap-2 text-sm font-mono text-cyber-purple hover:text-cyber-neon transition-colors'
          >
            View benchmark source code
            <ExternalLink className='w-3.5 h-3.5' />
          </a>
        </section>

        {/* FAQ */}
        <section className='mb-12'>
          <div className='flex items-center gap-3 mb-8'>
            <div className='w-10 h-10 rounded-lg bg-cyber-purple/10 flex items-center justify-center'>
              <FlaskConical className='w-5 h-5 text-cyber-purple' />
            </div>
            <div>
              <h2 className='font-display font-bold text-2xl text-white'>
                FAQ
              </h2>
              <p className='text-xs font-mono text-cyber-text/50'>
                Common questions about these benchmarks
              </p>
            </div>
          </div>
          <div className='space-y-4'>
            {[
              {
                q: "Is zodify faster than Pydantic?",
                a: "No. Pydantic v2 uses a Rust-compiled core and achieves about 1.50M ops/sec vs zodify's 533K ops/sec in the latest local comparison run. However, zodify is the fastest pure-Python validation library \u2014 2.4x faster than voluptuous, 13.8x faster than schema, and 63x faster than cerberus. zodify is also about 104x smaller and imports about 17x faster than Pydantic in the latest local run.",
              },
              {
                q: "How were these benchmarks measured?",
                a: "Validation comparisons use benchmarks/comparison_bench.py on Python 3.10.19 / Apple Silicon (ARM64): 500 warmups plus 10,000 measured single-call runs on a 3-key flat dict. Import time uses 30 fresh subprocess imports per library. Install size reflects a clean wheel-based virtual environment footprint including dependencies.",
              },
              {
                q: "Can I reproduce these benchmarks?",
                a: "Yes. Clone the repo, create a fresh virtual environment, install zodify plus the comparison libraries, then run python benchmarks/comparison_bench.py for the head-to-head validation results and python benchmarks/bench_import.py for import timings. All source code is in the benchmarks/ directory.",
              },
              {
                q: "Why is zodify's import time so much faster?",
                a: `zodify has zero dependencies and a compact Python runtime (${SITE_NUMBERS.sourceLoc} source LOC, ${SITE_NUMBERS.size} installed). There is no Rust compilation, no framework initialization, and no transitive dependency loading. This gives a ${SITE_NUMBERS.importMs} import time vs Pydantic's 39.4ms \u2014 about a 17x difference.`,
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

        {/* Last Updated */}
        <div className='text-center text-xs font-mono text-cyber-text/30'>
          Last updated: {SITE_LAST_UPDATED}
        </div>
      </motion.div>
    </div>
  );
}
