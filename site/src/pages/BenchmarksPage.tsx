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

const validationData = [
  {
    lib: "zodify",
    ops: 615000,
    opsLabel: "615K",
    latency: "1.62µs",
    highlight: true,
  },
  {
    lib: "pydantic v2",
    ops: 1300000,
    opsLabel: "1.3M",
    latency: "0.75µs",
    highlight: false,
    note: "Rust core",
  },
  {
    lib: "voluptuous",
    ops: 289000,
    opsLabel: "289K",
    latency: "3.46µs",
    highlight: false,
  },
  {
    lib: "schema",
    ops: 43000,
    opsLabel: "43K",
    latency: "23.04µs",
    highlight: false,
  },
  {
    lib: "cerberus",
    ops: 10000,
    opsLabel: "10K",
    latency: "100.50µs",
    highlight: false,
  },
];

const importData = [
  { lib: "zodify", time: 4.2, highlight: true },
  { lib: "schema", time: 8.8, highlight: false },
  { lib: "voluptuous", time: 15.0, highlight: false },
  { lib: "cerberus", time: 33.5, highlight: false },
  { lib: "pydantic v2", time: 44.1, highlight: false },
];

const sizeData = [
  { lib: "zodify", size: "48KB", sizeBytes: 48000, deps: 0, highlight: true },
  { lib: "schema", size: "64KB", sizeBytes: 64000, deps: 0, highlight: false },
  {
    lib: "voluptuous",
    size: "212KB",
    sizeBytes: 212000,
    deps: 0,
    highlight: false,
  },
  {
    lib: "cerberus",
    size: "228KB",
    sizeBytes: 228000,
    deps: 0,
    highlight: false,
  },
  {
    lib: "pydantic v2",
    size: "7.8MB",
    sizeBytes: 7800000,
    deps: 4,
    highlight: false,
  },
];

const maxOps = 1300000;
const maxImport = 50;

export function BenchmarksPage() {
  return (
    <div className='max-w-5xl mx-auto px-6 pt-12 pb-20'>
      <Helmet>
        <title>Benchmarks - zodify</title>
        <meta
          name='description'
          content='Performance benchmarks comparing zodify against pydantic, voluptuous, schema, and cerberus. 615K ops/sec, 48KB installed, 4ms import time.'
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
                  text: "No. Pydantic v2 uses a Rust-compiled core and achieves 1.3M ops/sec vs zodify's 615K ops/sec. However, zodify is the fastest pure-Python validation library - 2.1x faster than voluptuous, 14x faster than schema, and 61x faster than cerberus. zodify is also 162x smaller (48KB vs 7.8MB) and imports 10x faster (4ms vs 44ms).",
                },
              },
              {
                "@type": "Question",
                name: "How were these benchmarks measured?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "All benchmarks use Python 3.10 on Apple Silicon (ARM64). Validation speed is measured with timeit.repeat (best of 5 runs, 100,000+ iterations per measurement) using a 3-key flat dict (str, int, bool). Import time uses subprocess isolation per library.",
                },
              },
              {
                "@type": "Question",
                name: "Can I reproduce these benchmarks?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "Yes. Clone the repo (git clone https://github.com/junyoung2015/zodify), install dev dependencies (pip install -e .[dev]), and run python benchmarks/bench_validate.py and python benchmarks/bench_import.py.",
                },
              },
              {
                "@type": "Question",
                name: "Why is zodify's import time so much faster?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: "zodify has zero dependencies and a single-file architecture (402 lines, 48KB). There is no Rust compilation, no framework initialization, and no transitive dependency loading. This gives a 4.2ms import time vs Pydantic's 44.1ms.",
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
            Head-to-head performance comparison across five Python validation
            libraries. All numbers are reproducible from the source repo.
          </p>
        </div>

        {/* Stats Summary */}
        <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-12'>
          {[
            { label: "ZODIFY OPS/SEC", value: "615K" },
            { label: "IMPORT TIME", value: "4.2ms" },
            { label: "INSTALL SIZE", value: "48KB" },
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
              Pydantic v2 uses a Rust-compiled core, making it ~2.1x faster than
              zodify. Among <strong className='text-white'>pure-Python</strong>{" "}
              libraries, zodify is the fastest - 2.1x faster than voluptuous,
              14x faster than schema, and 61x faster than cerberus.
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
                  <th className='px-3 md:px-6 py-3 font-medium'>Install Size</th>
                  <th className='px-6 py-3 font-medium'>Dependencies</th>
                </tr>
              </thead>
              <tbody className='divide-y divide-white/5'>
                {[
                  {
                    lib: "zodify",
                    ops: "615K ops/sec (1.62µs)",
                    imp: "4.2ms",
                    size: "48KB",
                    deps: "0",
                    highlight: true,
                  },
                  {
                    lib: "pydantic v2",
                    ops: "1.3M ops/sec (0.75µs)",
                    imp: "44.1ms",
                    size: "7.8MB",
                    deps: "4",
                    highlight: false,
                  },
                  {
                    lib: "voluptuous",
                    ops: "289K ops/sec (3.46µs)",
                    imp: "15.0ms",
                    size: "212KB",
                    deps: "0",
                    highlight: false,
                  },
                  {
                    lib: "schema",
                    ops: "43K ops/sec (23.04µs)",
                    imp: "8.8ms",
                    size: "64KB",
                    deps: "0",
                    highlight: false,
                  },
                  {
                    lib: "cerberus",
                    ops: "10K ops/sec (100.50µs)",
                    imp: "33.5ms",
                    size: "228KB",
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
                { label: "Python Version", value: "3.10" },
                { label: "Hardware", value: "Apple Silicon (ARM64)" },
                {
                  label: "Validation Payload",
                  value: "3-key flat dict (str, int, bool)",
                },
                { label: "Iterations", value: "100,000+ per measurement" },
                { label: "Timing", value: "timeit.repeat, best of 5 runs" },
                {
                  label: "Import Timing",
                  value: "Subprocess isolation per library",
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
$ pip install -e ".[dev]"
$ python benchmarks/bench_validate.py
$ python benchmarks/bench_import.py`}
              </pre>
            </div>
          </div>

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
                a: "No. Pydantic v2 uses a Rust-compiled core and achieves 1.3M ops/sec vs zodify's 615K ops/sec. However, zodify is the fastest pure-Python validation library \u2014 2.1x faster than voluptuous, 14x faster than schema, and 61x faster than cerberus. zodify is also 162x smaller (48KB vs 7.8MB) and imports 10x faster (4ms vs 44ms).",
              },
              {
                q: "How were these benchmarks measured?",
                a: "All benchmarks use Python 3.10 on Apple Silicon (ARM64). Validation speed is measured with timeit.repeat (best of 5 runs, 100,000+ iterations per measurement) using a 3-key flat dict (str, int, bool). Import time uses subprocess isolation per library to avoid cross-contamination.",
              },
              {
                q: "Can I reproduce these benchmarks?",
                a: "Yes. Clone the repo (git clone https://github.com/junyoung2015/zodify), install dev dependencies (pip install -e .[dev]), and run python benchmarks/bench_validate.py and python benchmarks/bench_import.py. All source code is in the benchmarks/ directory.",
              },
              {
                q: "Why is zodify's import time so much faster?",
                a: "zodify has zero dependencies and a single-file architecture (402 lines, 48KB). There is no Rust compilation, no framework initialization, and no transitive dependency loading. This gives a 4.2ms import time vs Pydantic's 44.1ms \u2014 a 10x difference.",
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
          Last updated: March 5, 2026
        </div>
      </motion.div>
    </div>
  );
}
