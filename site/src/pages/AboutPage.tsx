import { Helmet } from "react-helmet-async";
import { motion } from "framer-motion";

export function AboutPage() {
  return (
    <div className='max-w-3xl mx-auto px-6 pt-12 pb-20'>
      <Helmet>
        <title>About - zodify</title>
        <meta
          name='description'
          content='How a 20-line automation script turned into a published Python validation library - the story behind zodify and why it exists.'
        />
        <link rel='canonical' href='https://zodify.dev/about' />
      </Helmet>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className='mb-12 border-b border-white/10 pb-8'>
          <div className='flex items-center gap-3 text-xs font-mono text-cyber-purple mb-4'>
            <span className='opacity-70'>ABOUT</span>
            <span className='opacity-50'>/</span>
            <span className='opacity-70'>WHY ZODIFY?</span>
          </div>
          <h1 className='font-display font-extrabold text-4xl md:text-5xl text-white mb-4 tracking-tight'>
            Why zodify?
          </h1>
          <p className='text-lg text-cyber-text/50 font-light italic'>
            How a 20-line automation script turned into a Python validation
            library - and why I now understand open source.
          </p>
        </div>

        <div className='prose-cyber space-y-12'>
          {/* Intro */}
          <p className='text-cyber-text/80 leading-relaxed text-lg'>
            This is the story of how zodify went from a throwaway helper
            function to a published PyPI library with 263 tests, 7 releases, and
            615,000 validations per second. It covers the friction that started
            it, the constraints that shaped it, and what building open source
            taught me.
          </p>

          {/* Section 1 */}
          <section>
            <h2 className='font-display font-bold text-2xl md:text-3xl text-white mb-6'>
              It started with an{" "}
              <code className='bg-white/5 px-2 py-0.5 rounded text-cyber-purple font-mono text-xl'>
                .env
              </code>{" "}
              file
            </h2>
            <p className='text-cyber-text/70 leading-relaxed mb-4 font-semibold text-lg'>
              The validation tool I needed was heavier than the script I was
              writing.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              I was writing a Python script to automate some work for our team -
              read API keys from a{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                .env
              </code>{" "}
              file or{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                os
              </code>{" "}
              environment variables, validate them, make some API calls. Twenty
              lines of real logic, maybe thirty.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              I needed to validate the input data. The obvious answer was
              Pydantic.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              But I hesitated. Pydantic felt way too <em>serious</em> for this.
              In my head, Pydantic belonged in the backend - FastAPI route
              validators, Django serializers, production data pipelines. It's a
              7.8MB install with four transitive dependencies. Import time: 44
              milliseconds. My entire script was lighter than the validator I
              was about to install.
            </p>
            <p className='text-cyber-text/70 leading-relaxed'>
              I looked for alternatives. And I found... not much. There are
              lightweight validation libraries in Python - cerberus, voluptuous,
              schema - but they were either barely maintained, hadn't adopted
              modern Python features like{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                str | int
              </code>{" "}
              union syntax, or had APIs that required learning yet another DSL.
              I wasn't looking for another framework. I just wanted to check
              that a{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                port
              </code>{" "}
              value was an{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                int
              </code>{" "}
              and an{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                api_key
              </code>{" "}
              was a non-empty{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                str
              </code>
              .
            </p>
          </section>

          <div className='w-full h-px bg-gradient-to-r from-transparent via-cyber-border to-transparent opacity-50'></div>

          {/* Section 2 */}
          <section>
            <h2 className='font-display font-bold text-2xl md:text-3xl text-white mb-6'>
              What if validation was just... Python dicts?
            </h2>
            <p className='text-cyber-text/70 leading-relaxed mb-4 font-semibold text-lg'>
              A throwaway helper function turned into a design question - and
              then a real library.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-6'>
              The thought started as a throwaway. I wrote a helper function - it
              didn't even have a name yet - that took two dicts: one describing
              the expected types, one containing the actual data. Match them up,
              raise an error if something's wrong.
            </p>
            <div className='relative rounded-xl bg-[#0d0b16] border border-white/10 overflow-hidden mb-6'>
              <div className='p-6 overflow-x-auto'>
                <pre className='font-mono text-sm leading-relaxed'>
                  <code>
                    <span className='text-cyber-purple'>validate</span>({"{"}
                    <span className='text-green-400'>"port"</span>:{" "}
                    <span className='text-cyber-blue'>int</span>,{" "}
                    <span className='text-green-400'>"debug"</span>:{" "}
                    <span className='text-cyber-blue'>bool</span>
                    {"}"}, {"{"}
                    <span className='text-green-400'>"port"</span>:{" "}
                    <span className='text-orange-400'>8080</span>,{" "}
                    <span className='text-green-400'>"debug"</span>:{" "}
                    <span className='text-orange-400'>True</span>
                    {"}"})
                  </code>
                </pre>
              </div>
            </div>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              No classes. No{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                BaseModel
              </code>
              . No{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                {"Field(ge=0, le=65535)"}
              </code>
              . Just the shape of the data, described in the types you already
              think in.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              But then a question crept in:{" "}
              <em>What if I actually built this properly?</em>
            </p>
            <p className='text-cyber-text/70 leading-relaxed'>
              Not a throwaway helper. A real library. Semver releases. Tests.
              Published on PyPI. Something other people could{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                pip install
              </code>
              . I'd never done that before - never created my own library, never
              published a package. The idea excited me more than the script that
              started it all.
            </p>
          </section>

          <div className='w-full h-px bg-gradient-to-r from-transparent via-cyber-border to-transparent opacity-50'></div>

          {/* Section 3 */}
          <section>
            <h2 className='font-display font-bold text-2xl md:text-3xl text-white mb-6'>
              From helper function to open-source library
            </h2>
            <p className='text-cyber-text/70 leading-relaxed mb-4 font-semibold text-lg'>
              Deliberate constraints - one file, zero dependencies, 500 LOC cap
              - shaped every decision.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              I set myself constraints from the start. One source file. Zero
              dependencies. Cap the implementation at 500 lines of code. Every
              line had to earn its place. These weren't arbitrary limitations -
              they were design decisions. A single file means trivial auditing.
              Zero dependencies means zero supply-chain risk. The LOC cap forces
              API discipline: if adding a feature pushes you past the budget,
              you have to find a better abstraction.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-6'>
              The first release, v0.0.1, landed on PyPI on February 25, 2026.
              Core{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                validate()
              </code>{" "}
              function, type coercion,{" "}
              <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
                env()
              </code>{" "}
              helper for environment variables. Functional, but minimal.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-6'>
              Then the iterations started:
            </p>
            <ul className='space-y-2 mb-6'>
              {[
                [
                  "v0.1.0",
                  "Nested schema validation, optional keys, typed lists",
                ],
                [
                  "v0.2.0",
                  "Custom validator functions, unknown key handling, recursion depth protection, benchmark infrastructure",
                ],
                [
                  "v0.2.1",
                  "PEP 561 type marker, mypy strict + pyright CI gates, overloaded signatures for IDE inference",
                ],
                ["v0.3.0", "Union types using Python 3.10+ str | int syntax"],
                [
                  "v0.4.0",
                  "Structured error reporting: machine-readable ValidationError with path, message, expected, and got",
                ],
                ["v0.4.1", "Example scripts, schema composition documentation"],
              ].map(([version, desc]) => (
                <li key={version} className='flex gap-3 text-cyber-text/70'>
                  <span className='font-mono text-cyber-purple text-sm font-bold shrink-0'>
                    {version}
                  </span>
                  <span className='text-sm leading-relaxed'>- {desc}</span>
                </li>
              ))}
            </ul>
            <p className='text-cyber-text/70 leading-relaxed mb-6'>
              Seven releases in eight days. 263 tests. 402 lines of code. Strict
              type checking with mypy and pyright as merge-blocking CI gates.
              Automated PyPI publishing on every version tag.
            </p>

            {/* Benchmark Table */}
            <div className='w-full overflow-hidden rounded-lg border border-white/10 mb-6'>
              <table className='w-full text-sm text-left'>
                <thead className='bg-white/5 text-cyber-text/60 font-mono text-xs uppercase'>
                  <tr>
                    <th className='px-6 py-3 font-medium'>Library</th>
                    <th className='px-6 py-3 font-medium'>Ops/sec</th>
                    <th className='px-6 py-3 font-medium'>Import</th>
                    <th className='px-6 py-3 font-medium'>Install Size</th>
                    <th className='px-6 py-3 font-medium'>Deps</th>
                  </tr>
                </thead>
                <tbody className='divide-y divide-white/5'>
                  {[
                    {
                      lib: "zodify",
                      ops: "615K",
                      imp: "4ms",
                      size: "48KB",
                      deps: "0",
                      highlight: true,
                    },
                    {
                      lib: "pydantic v2 (Rust)",
                      ops: "1.3M",
                      imp: "44ms",
                      size: "7.8MB",
                      deps: "4",
                      highlight: false,
                    },
                    {
                      lib: "voluptuous",
                      ops: "289K",
                      imp: "15ms",
                      size: "212KB",
                      deps: "0",
                      highlight: false,
                    },
                    {
                      lib: "schema",
                      ops: "43K",
                      imp: "9ms",
                      size: "64KB",
                      deps: "0",
                      highlight: false,
                    },
                    {
                      lib: "cerberus",
                      ops: "10K",
                      imp: "34ms",
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
                        className={`px-6 py-4 font-mono ${row.highlight ? "text-white font-bold" : "text-cyber-text/60"}`}
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
            <p className='text-cyber-text/70 leading-relaxed'>
              zodify is the fastest pure-Python validation library I could find.
              Only Pydantic v2's Rust-compiled core validates faster - but at
              the cost of a 7.8MB install and a 44ms import time. zodify does it
              in 48KB and 4 milliseconds.
            </p>
          </section>

          <div className='w-full h-px bg-gradient-to-r from-transparent via-cyber-border to-transparent opacity-50'></div>

          {/* Section 4 */}
          <section>
            <h2 className='font-display font-bold text-2xl md:text-3xl text-white mb-6'>
              What I didn't expect
            </h2>
            <p className='text-cyber-text/70 leading-relaxed mb-4 font-semibold text-lg'>
              Building zodify taught me why people contribute to open source for
              free.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              I'd always wondered about open-source maintainers. People pouring
              hours into npm packages, PyPI libraries, Cargo crates - without
              getting paid. Before zodify, it genuinely puzzled me. Why would
              you spend evenings and weekends building something for strangers?
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              Now I know.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              Every moment of building zodify has been <em>happy</em>.
              Discussing architecture decisions, debating API design, watching
              test counts climb from 10 to 263 - it never felt like work. It
              felt like building something that mattered, even if the audience
              was small.
            </p>
            <p className='text-cyber-text/70 leading-relaxed mb-4'>
              I understand now that open-source contributors aren't doing
              charity. They're doing what they genuinely want to do. They're
              passionate about it, and they enjoy the process of creating and
              sharing something with the world.
            </p>
            <p className='text-cyber-text/70 leading-relaxed'>
              zodify is my first contribution to that world. It won't be my
              last.
            </p>
          </section>

          <div className='w-full h-px bg-gradient-to-r from-transparent via-cyber-border to-transparent opacity-50'></div>

          {/* Attribution */}
          <p className='text-cyber-text/50 italic text-sm'>
            - Jun Young Sohn (jusohn)
          </p>
        </div>
      </motion.div>
    </div>
  );
}
