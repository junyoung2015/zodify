import { type ReactNode } from "react";
import { Helmet } from "react-helmet-async";
import { Rocket, Layers, Zap, AlertTriangle, Code } from "lucide-react";

function CodeBlock({
  filename,
  children,
}: {
  filename: string;
  children: ReactNode;
}) {
  return (
    <div className='relative group mb-8'>
      <div className='relative rounded-xl bg-[#0d0b16] border border-white/10 overflow-hidden'>
        <div className='flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5'>
          <div className='flex gap-1.5'>
            <div className='w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50'></div>
            <div className='w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50'></div>
            <div className='w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50'></div>
          </div>
          <span className='text-xs font-mono text-cyber-text/30'>
            {filename}
          </span>
        </div>
        <div className='p-6 overflow-x-auto'>
          <pre className='font-mono text-sm leading-relaxed'>
            <code>{children}</code>
          </pre>
        </div>
      </div>
    </div>
  );
}

export function DocsPage() {
  return (
    <div className='flex gap-12 pt-8 pb-20 max-w-7xl mx-auto px-6'>
      <Helmet>
        <title>Docs - zodify</title>
        <meta
          name='description'
          content='Documentation for zodify: installation, schemas, validation, type coercion, union types, custom validators, environment variables, and structured errors.'
        />
        <link rel='canonical' href='https://zodify.dev/docs' />
      </Helmet>
      {/* Sidebar */}
      <aside className='hidden md:block w-64 flex-shrink-0 sticky top-24 h-[calc(100vh-8rem)] overflow-y-auto pr-4'>
        <nav className='space-y-8 font-display text-sm'>
          <div>
            <h5 className='text-white font-bold mb-4 flex items-center gap-2'>
              <Rocket className='w-4 h-4 text-cyber-purple' />
              Getting Started
            </h5>
            <ul className='space-y-2 border-l border-white/10 ml-2 pl-4'>
              <li>
                <a
                  href='#install'
                  className='block text-cyber-purple border-l-2 border-cyber-purple -ml-[18px] pl-[14px] font-medium'
                >
                  Installation
                </a>
              </li>
              <li>
                <a
                  href='#basic-validation'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Basic Validation
                </a>
              </li>
              <li>
                <a
                  href='#type-support'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Type Support
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h5 className='text-white font-bold mb-4 flex items-center gap-2'>
              <Layers className='w-4 h-4 text-cyber-purple' />
              Schemas
            </h5>
            <ul className='space-y-2 border-l border-white/10 ml-2 pl-4'>
              <li>
                <a
                  href='#optional-keys'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Optional Keys
                </a>
              </li>
              <li>
                <a
                  href='#union-types'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Union Types
                </a>
              </li>
              <li>
                <a
                  href='#nested-schemas'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Nested Schemas
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h5 className='text-white font-bold mb-4 flex items-center gap-2'>
              <Zap className='w-4 h-4 text-cyber-purple' />
              Advanced
            </h5>
            <ul className='space-y-2 border-l border-white/10 ml-2 pl-4'>
              <li>
                <a
                  href='#custom-validators'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Custom Validators
                </a>
              </li>
              <li>
                <a
                  href='#env-helper'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Env Helper
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h5 className='text-white font-bold mb-4 flex items-center gap-2'>
              <AlertTriangle className='w-4 h-4 text-cyber-purple' />
              Errors
            </h5>
            <ul className='space-y-2 border-l border-white/10 ml-2 pl-4'>
              <li>
                <a
                  href='#error-handling'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Error Handling
                </a>
              </li>
              <li>
                <a
                  href='#structured-errors'
                  className='block text-cyber-text/60 hover:text-white transition-colors'
                >
                  Structured Errors
                </a>
              </li>
            </ul>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className='flex-grow min-w-0 max-w-3xl'>
        <div className='mb-12 border-b border-white/10 pb-8'>
          <div className='flex items-center gap-3 text-xs font-mono text-cyber-purple mb-4'>
            <span className='opacity-70'>DOCS</span>
            <span className='opacity-50'>/</span>
            <span className='opacity-70'>GETTING STARTED</span>
          </div>
          <h1 className='font-display font-extrabold text-4xl md:text-5xl text-white mb-4 tracking-tight'>
            Getting Started
          </h1>
          <p className='text-lg text-cyber-text/70 leading-relaxed font-light'>
            Get from zero to validating dicts in 60 seconds. zodify uses plain
            Python types as schemas - no DSL, no decorators, no magic.
          </p>
        </div>

        {/* Installation */}
        <section id='install' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Installation
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            zodify is a single file with zero dependencies. Install from PyPI:
          </p>
          <CodeBlock filename='terminal'>
            <span className='text-cyber-purple'>$</span> pip install zodify
          </CodeBlock>
          <p className='text-cyber-text/60 text-sm'>
            Requires Python 3.10+ (for{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              str | int
            </code>{" "}
            union syntax).
          </p>
        </section>

        {/* Basic Validation */}
        <section id='basic-validation' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Basic Validation
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Define a schema as a plain Python dict mapping keys to types. Call{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              validate(schema, data)
            </code>{" "}
            - schema first, data second.
          </p>
          <CodeBlock filename='basic_validation.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> validate{"\n"}
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
            result = <span className='text-cyber-purple'>validate</span>(schema,
            data){"\n"}
            <span className='text-slate-500 italic'>
              # → {"{"}&#39;name&#39;: &#39;Alice&#39;, &#39;age&#39;: 30{"}"}
            </span>
          </CodeBlock>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            If validation fails, a{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              ValueError
            </code>{" "}
            is raised with a clear message:
          </p>
          <CodeBlock filename='error_example.py'>
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-green-400'>"Alice"</span>,{" "}
            <span className='text-green-400'>"age"</span>:{" "}
            <span className='text-green-400'>"thirty"</span>
            {"}"}){"\n"}
            <span className='text-slate-500 italic'>
              # → ValueError: age: expected int, got str
            </span>
            {"\n"}
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-green-400'>"Alice"</span>
            {"}"}){"\n"}
            <span className='text-slate-500 italic'>
              # → ValueError: age: missing required key
            </span>
          </CodeBlock>
        </section>

        {/* Type Support */}
        <section id='type-support' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Type Support
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Schema values can be any Python type. zodify checks{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              isinstance()
            </code>{" "}
            under the hood.
          </p>
          <div className='w-full overflow-hidden rounded-lg border border-white/10 mb-6'>
            <table className='w-full text-sm text-left'>
              <thead className='bg-white/5 text-cyber-text/60 font-mono text-xs uppercase'>
                <tr>
                  <th className='px-6 py-3 font-medium'>Schema Type</th>
                  <th className='px-6 py-3 font-medium'>Accepts</th>
                  <th className='px-6 py-3 font-medium'>Example</th>
                </tr>
              </thead>
              <tbody className='divide-y divide-white/5'>
                {[
                  { type: "str", accepts: "Strings", example: '"hello"' },
                  {
                    type: "int",
                    accepts: "Integers (not bool)",
                    example: "42",
                  },
                  { type: "float", accepts: "Floats", example: "3.14" },
                  { type: "bool", accepts: "Booleans", example: "True" },
                  { type: "list", accepts: "Lists", example: "[1, 2, 3]" },
                  {
                    type: "dict",
                    accepts: "Nested schemas",
                    example: '{"key": str}',
                  },
                ].map((row) => (
                  <tr
                    key={row.type}
                    className='bg-cyber-glass hover:bg-white/5 transition-colors'
                  >
                    <td className='px-6 py-4 font-mono text-cyber-purple'>
                      {row.type}
                    </td>
                    <td className='px-6 py-4 text-cyber-text/70'>
                      {row.accepts}
                    </td>
                    <td className='px-6 py-4 font-mono text-cyber-text/60'>
                      {row.example}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Optional Keys */}
        <section id='optional-keys' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Optional Keys
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Use{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              Optional(type)
            </code>{" "}
            or{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              Optional(type, default)
            </code>{" "}
            for keys that may be absent.
          </p>
          <CodeBlock filename='optional_keys.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> Optional, validate
            {"\n"}
            {"\n"}
            schema = {"{"}
            {"\n"}
            {"    "}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-cyber-blue'>str</span>,{"\n"}
            {"    "}
            <span className='text-green-400'>"debug"</span>: Optional(
            <span className='text-cyber-blue'>bool</span>,{" "}
            <span className='text-orange-400'>False</span>),{"\n"}
            {"    "}
            <span className='text-green-400'>"region"</span>: Optional(
            <span className='text-cyber-blue'>str</span>),{"\n"}
            {"}"}
            {"\n"}
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-green-400'>"api"</span>
            {"}"}){"\n"}
            <span className='text-slate-500 italic'>
              # → {"{"}&#39;name&#39;: &#39;api&#39;, &#39;debug&#39;: False
              {"}"}
            </span>
          </CodeBlock>
        </section>

        {/* Union Types */}
        <section id='union-types' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Union Types
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Use Python 3.10+{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              str | int
            </code>{" "}
            syntax for union types. The value must match at least one type in
            the union.
          </p>
          <CodeBlock filename='union_types.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> validate{"\n"}
            {"\n"}
            schema = {"{"}
            <span className='text-green-400'>"value"</span>:{" "}
            <span className='text-cyber-blue'>str</span> |{" "}
            <span className='text-cyber-blue'>int</span>
            {"}"}
            {"\n"}
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"value"</span>:{" "}
            <span className='text-green-400'>"hello"</span>
            {"}"}) <span className='text-slate-500 italic'># ✓ str</span>
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"value"</span>:{" "}
            <span className='text-orange-400'>7</span>
            {"}"}) <span className='text-slate-500 italic'># ✓ int</span>
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"value"</span>:{" "}
            <span className='text-orange-400'>True</span>
            {"}"}){" "}
            <span className='text-slate-500 italic'># ✗ bool ≠ str | int</span>
            {"\n"}
            <span className='text-slate-500 italic'>
              # → ValueError: value: expected str | int, got bool
            </span>
          </CodeBlock>
        </section>

        {/* Nested Schemas */}
        <section id='nested-schemas' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Nested Schemas
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Compose schemas by nesting dicts. Errors report the full path.
          </p>
          <CodeBlock filename='nested_schemas.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> Optional, validate
            {"\n"}
            {"\n"}
            config_schema = {"{"}
            {"\n"}
            {"    "}
            <span className='text-green-400'>"db"</span>: {"{"}
            <span className='text-green-400'>"host"</span>:{" "}
            <span className='text-cyber-blue'>str</span>,{" "}
            <span className='text-green-400'>"port"</span>:{" "}
            <span className='text-cyber-blue'>int</span>
            {"}"}, {"\n"}
            {"    "}
            <span className='text-green-400'>"service"</span>: {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-cyber-blue'>str</span>,{" "}
            <span className='text-green-400'>"mode"</span>:{" "}
            <span className='text-cyber-blue'>str</span> |{" "}
            <span className='text-cyber-blue'>int</span>
            {"}"}, {"\n"}
            {"    "}
            <span className='text-green-400'>"debug"</span>: Optional(
            <span className='text-cyber-blue'>bool</span>,{" "}
            <span className='text-orange-400'>False</span>),{"\n"}
            {"}"}
            {"\n"}
            {"\n"}
            <span className='text-cyber-purple'>
              validate
            </span>(config_schema, {"{"}
            {"\n"}
            {"    "}
            <span className='text-green-400'>"db"</span>: {"{"}
            <span className='text-green-400'>"host"</span>:{" "}
            <span className='text-green-400'>"localhost"</span>,{" "}
            <span className='text-green-400'>"port"</span>:{" "}
            <span className='text-orange-400'>5432</span>
            {"}"}, {"\n"}
            {"    "}
            <span className='text-green-400'>"service"</span>: {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-green-400'>"api"</span>,{" "}
            <span className='text-green-400'>"mode"</span>:{" "}
            <span className='text-orange-400'>1</span>
            {"}"}, {"\n"}
            {"}"})
          </CodeBlock>
        </section>

        {/* Custom Validators */}
        <section id='custom-validators' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Custom Validators
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Use a lambda or function as a schema value. It receives the value
            and must return{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              True
            </code>{" "}
            to pass.
          </p>
          <CodeBlock filename='custom_validators.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> validate{"\n"}
            {"\n"}
            <span className='text-slate-500 italic'># Lambda validator</span>
            {"\n"}
            schema = {"{"}
            <span className='text-green-400'>"nick"</span>:{" "}
            <span className='text-cyber-purple'>lambda</span> v:{" "}
            <span className='text-cyber-purple'>isinstance</span>(v,{" "}
            <span className='text-cyber-blue'>str</span>){" "}
            <span className='text-cyber-purple'>and</span>{" "}
            <span className='text-cyber-purple'>len</span>(v) {">"}
            <span className='text-orange-400'>= 3</span>
            {"}"}
            {"\n"}
            <span className='text-cyber-purple'>validate</span>(schema, {"{"}
            <span className='text-green-400'>"nick"</span>:{" "}
            <span className='text-green-400'>"ally"</span>
            {"}"}) <span className='text-slate-500 italic'># ✓</span>
            {"\n"}
            {"\n"}
            <span className='text-slate-500 italic'>
              # Named function validator
            </span>
            {"\n"}
            <span className='text-cyber-purple'>def</span>{" "}
            <span className='text-cyber-neon'>even_number</span>(v):{"\n"}
            {"    "}
            <span className='text-cyber-purple'>return</span>{" "}
            <span className='text-cyber-purple'>isinstance</span>(v,{" "}
            <span className='text-cyber-blue'>int</span>){" "}
            <span className='text-cyber-purple'>and</span> v %{" "}
            <span className='text-orange-400'>2</span> =={" "}
            <span className='text-orange-400'>0</span>
            {"\n"}
            {"\n"}
            <span className='text-cyber-purple'>validate</span>({"{"}
            <span className='text-green-400'>"count"</span>: even_number{"}"},{" "}
            {"{"}
            <span className='text-green-400'>"count"</span>:{" "}
            <span className='text-orange-400'>4</span>
            {"}"}) <span className='text-slate-500 italic'># ✓</span>
            {"\n"}
            <span className='text-cyber-purple'>validate</span>({"{"}
            <span className='text-green-400'>"count"</span>: even_number{"}"},{" "}
            {"{"}
            <span className='text-green-400'>"count"</span>:{" "}
            <span className='text-orange-400'>3</span>
            {"}"}) <span className='text-slate-500 italic'># ✗</span>
            {"\n"}
            <span className='text-slate-500 italic'>
              # → ValueError: count: custom validator &#39;even_number&#39;
              failed
            </span>
          </CodeBlock>
        </section>

        {/* Env Helper */}
        <section id='env-helper' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Env Helper
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Use{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              env(name, type, default?)
            </code>{" "}
            to load and type-cast environment variables.
          </p>
          <CodeBlock filename='env_config.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> env{"\n"}
            {"\n"}
            port = <span className='text-cyber-purple'>env</span>(
            <span className='text-green-400'>"PORT"</span>,{" "}
            <span className='text-cyber-blue'>int</span>){" "}
            <span className='text-slate-500 italic'># → 8080 (int)</span>
            {"\n"}
            debug = <span className='text-cyber-purple'>env</span>(
            <span className='text-green-400'>"DEBUG"</span>,{" "}
            <span className='text-cyber-blue'>bool</span>){" "}
            <span className='text-slate-500 italic'># → True (bool)</span>
            {"\n"}
            timeout = <span className='text-cyber-purple'>env</span>(
            <span className='text-green-400'>"TIMEOUT"</span>,{" "}
            <span className='text-cyber-blue'>int</span>,{" "}
            <span className='text-orange-400'>30</span>){" "}
            <span className='text-slate-500 italic'># → 30 (default)</span>
            {"\n"}
            {"\n"}
            <span className='text-slate-500 italic'>
              # Missing required var raises ValueError
            </span>
            {"\n"}
            <span className='text-cyber-purple'>env</span>(
            <span className='text-green-400'>"SECRET_KEY"</span>,{" "}
            <span className='text-cyber-blue'>str</span>){"\n"}
            <span className='text-slate-500 italic'>
              # → ValueError: SECRET_KEY: missing required env var
            </span>
          </CodeBlock>
        </section>

        {/* Error Handling */}
        <section id='error-handling' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Error Handling
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            By default,{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              validate()
            </code>{" "}
            raises a standard{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              ValueError
            </code>{" "}
            with a human-readable message including the key path, expected type,
            and actual type.
          </p>
          <CodeBlock filename='errors.py'>
            <span className='text-cyber-purple'>try</span>:{"\n"}
            {"    "}
            <span className='text-cyber-purple'>validate</span>({"{"}
            <span className='text-green-400'>"age"</span>:{" "}
            <span className='text-cyber-blue'>int</span>
            {"}"}, {"{"}
            <span className='text-green-400'>"age"</span>:{" "}
            <span className='text-green-400'>"thirty"</span>
            {"}"}){"\n"}
            <span className='text-cyber-purple'>except</span>{" "}
            <span className='text-cyber-blue'>ValueError</span>{" "}
            <span className='text-cyber-purple'>as</span> e:{"\n"}
            {"    "}
            <span className='text-cyber-purple'>print</span>(e){" "}
            <span className='text-slate-500 italic'>
              # → age: expected int, got str
            </span>
          </CodeBlock>
        </section>

        {/* Structured Errors */}
        <section id='structured-errors' className='mb-16 scroll-mt-24'>
          <h2 className='font-display font-bold text-3xl text-white mb-6 group cursor-pointer flex items-center'>
            <span className='text-cyber-purple/60 mr-2 opacity-50 text-2xl font-mono group-hover:opacity-100 transition-opacity'>
              #
            </span>
            Structured Errors
          </h2>
          <p className='text-cyber-text/80 mb-6 leading-relaxed'>
            Pass{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              error_mode="structured"
            </code>{" "}
            to get a{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              ValidationError
            </code>{" "}
            with programmatic access to each issue.
          </p>
          <CodeBlock filename='structured_errors.py'>
            <span className='text-cyber-purple'>from</span>{" "}
            <span className='text-cyber-neon'>zodify</span>{" "}
            <span className='text-cyber-purple'>import</span> ValidationError,
            validate{"\n"}
            {"\n"}
            <span className='text-cyber-purple'>try</span>:{"\n"}
            {"    "}
            <span className='text-cyber-purple'>validate</span>({"\n"}
            {"        "}
            {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-cyber-blue'>str</span>,{" "}
            <span className='text-green-400'>"age"</span>:{" "}
            <span className='text-cyber-blue'>int</span>
            {"}"}, {"\n"}
            {"        "}
            {"{"}
            <span className='text-green-400'>"name"</span>:{" "}
            <span className='text-orange-400'>123</span>,{" "}
            <span className='text-green-400'>"age"</span>:{" "}
            <span className='text-green-400'>"bad"</span>
            {"}"}, {"\n"}
            {"        "}error_mode=
            <span className='text-green-400'>"structured"</span>,{"\n"}
            {"    "}){"\n"}
            <span className='text-cyber-purple'>except</span>{" "}
            <span className='text-cyber-blue'>ValidationError</span>{" "}
            <span className='text-cyber-purple'>as</span> e:{"\n"}
            {"    "}
            <span className='text-cyber-purple'>for</span> issue{" "}
            <span className='text-cyber-purple'>in</span> e.issues:{"\n"}
            {"        "}
            <span className='text-cyber-purple'>print</span>(issue[
            <span className='text-green-400'>"path"</span>], issue[
            <span className='text-green-400'>"message"</span>]){"\n"}
            {"        "}
            <span className='text-slate-500 italic'>
              # → name expected str, got int
            </span>
            {"\n"}
            {"        "}
            <span className='text-slate-500 italic'>
              # → age expected int, got str
            </span>
          </CodeBlock>
          <p className='text-cyber-text/80 leading-relaxed'>
            Each issue dict contains:{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              path
            </code>
            ,{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              message
            </code>
            ,{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              expected
            </code>
            , and{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              got
            </code>
            .{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              ValidationError
            </code>{" "}
            is a subclass of{" "}
            <code className='bg-white/5 px-1.5 py-0.5 rounded text-sm font-mono text-cyber-purple'>
              ValueError
            </code>
            , so existing except blocks still work.
          </p>
        </section>
      </main>

      {/* Right Sidebar (Table of Contents) */}
      <aside className='hidden xl:block w-64 flex-shrink-0 sticky top-24 h-[calc(100vh-8rem)]'>
        <div className='border-l border-white/10 pl-4'>
          <h5 className='text-xs font-mono font-bold text-cyber-text/40 uppercase tracking-widest mb-4'>
            On this page
          </h5>
          <ul className='space-y-3 text-sm font-display'>
            <li>
              <a
                href='#install'
                className='block text-cyber-purple font-medium hover:text-cyber-neon transition-colors'
              >
                Installation
              </a>
            </li>
            <li>
              <a
                href='#basic-validation'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Basic Validation
              </a>
            </li>
            <li>
              <a
                href='#type-support'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Type Support
              </a>
            </li>
            <li>
              <a
                href='#optional-keys'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Optional Keys
              </a>
            </li>
            <li>
              <a
                href='#union-types'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Union Types
              </a>
            </li>
            <li>
              <a
                href='#nested-schemas'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Nested Schemas
              </a>
            </li>
            <li>
              <a
                href='#custom-validators'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Custom Validators
              </a>
            </li>
            <li>
              <a
                href='#env-helper'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Env Helper
              </a>
            </li>
            <li>
              <a
                href='#error-handling'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Error Handling
              </a>
            </li>
            <li>
              <a
                href='#structured-errors'
                className='block text-cyber-text/60 hover:text-cyber-purple transition-colors'
              >
                Structured Errors
              </a>
            </li>
          </ul>
          <div className='mt-8 pt-8 border-t border-white/5'>
            <a
              href='https://github.com/junyoung2015/zodify'
              target='_blank'
              rel='noopener noreferrer'
              className='flex items-center gap-2 text-xs font-mono text-cyber-text/50 hover:text-white transition-colors'
            >
              <Code className='w-3 h-3' />
              View source on GitHub
            </a>
          </div>
        </div>
      </aside>
    </div>
  );
}
