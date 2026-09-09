import type examples from "./examples.json";

export type Section = {
  id: string;
  title: string;
  paragraphs: string[];
  example?: keyof typeof examples;
  links?: [string, string][];
};
export type Page = {
  path: string;
  title: string;
  description: string;
  updated: string;
  nav?: string;
  sections: Section[];
};
const page = (
  path: string,
  title: string,
  description: string,
  sections: Section[],
  nav?: string,
): Page => ({ path, title, description, sections, nav, updated: "2026-09-09" });
const section = (
  id: string,
  title: string,
  paragraphs: string[],
  example?: keyof typeof examples,
  links?: [string, string][],
): Section => ({ id, title, paragraphs, example, links });
export const routes: Page[] = [
  page(
    "/",
    "Validate Python dictionaries. Keep them dictionaries.",
    "Describe the data you expect with ordinary Python types. Validate configuration and script inputs with zero required runtime dependencies.",
    [
      section(
        "start",
        "Two dicts. One useful boundary.",
        [
          "Describe the shape with ordinary Python types, then validate the data you receive. A model framework or builder API is not required. Zodify is Zod-inspired, with its own Python semantics and deliberately limited scope.",
        ],
        "first-validation",
        [
          ["Read the getting-started guide", "/docs/getting-started/"],
          ["Choose the right validator", "/compare/"],
        ],
      ),
      section(
        "fit",
        "A small tool for small data boundaries",
        [
          "Use zodify for configuration dicts, automation scripts, and straightforward Python object validation. Required keys, exact types, nested shapes, and explicit coercion keep decisions visible.",
          "Choose a broader tool when you need extensive typing support, framework integrations, serialization, recursive models, or a JSON Schema implementation. See the selection guide for the appropriate Pydantic TypeAdapter API.",
        ],
        undefined,
        [
          ["Validate configuration", "/guides/config-validation/"],
          ["Validate CLI input", "/guides/cli-input-validation/"],
          ["Validate a JSON object", "/guides/json-object-validation/"],
        ],
      ),
      section(
        "boundaries",
        "Know the semantics before you rely on them",
        [
          "By default, unknown keys fail validation and bool is not accepted as int. Optional keys and nullable values mean different things. Released defaults are inserted without independent validation or copying.",
          "Canonical error details, strict JSON object input, conservative exact JSON Schema export, and .env file loading are available in 0.8.0. Compilation and reports remain unavailable.",
        ],
        undefined,
        [
          ["Types and coercion", "/docs/types-and-coercion/"],
          ["Defaults and ownership", "/docs/optional-and-defaults/"],
          ["Released versus planned", "/roadmap/"],
        ],
      ),
    ],
    "Home",
  ),
  page(
    "/docs/",
    "Documentation",
    "Released API documentation and task guides, with stable links for existing zodify documentation.",
    [
      section(
        "install",
        "Installation",
        [
          "Install the released package with pip install zodify==0.8.0. Python 3.10 or later is required.",
        ],
        undefined,
        [["Getting started", "/docs/getting-started/"]],
      ),
      section(
        "basic-validation",
        "Basic validation",
        [
          "Pass a schema dict and a data dict to validate(). Exact types and unknown-key rejection are the defaults.",
        ],
        "quickstart",
        [["First validation", "/docs/getting-started/"]],
      ),
      section(
        "type-support",
        "Supported types",
        [
          "Use exact Python types, nested dict schemas, one-element list schemas, unions, and predicates.",
        ],
        undefined,
        [
          ["Schema grammar", "/docs/schemas/"],
          ["Types and coercion", "/docs/types-and-coercion/"],
        ],
      ),
      section(
        "optional-keys",
        "Optional keys and defaults",
        [
          "Optional controls missing keys; a union with None controls nullable values. Released defaults are not copied or validated.",
        ],
        undefined,
        [["Optional and defaults", "/docs/optional-and-defaults/"]],
      ),
      section(
        "union-types",
        "Unions",
        [
          "With coercion enabled, string input follows declared union order; non-string exact matches take precedence.",
        ],
        undefined,
        [["Conversion rules", "/docs/types-and-coercion/"]],
      ),
      section(
        "nested-schemas",
        "Nested schemas",
        [
          "Dict shapes and one-element list schemas validate nested containers. The default maximum depth is 32.",
        ],
        undefined,
        [["Schemas", "/docs/schemas/"]],
      ),
      section(
        "class-schemas",
        "Optional class syntax",
        [
          "Schema declarations offer attribute access using the same validation engine.",
        ],
        undefined,
        [["Class schemas and limitations", "/docs/class-schemas/"]],
      ),
      section(
        "custom-validators",
        "Custom validators",
        [
          "Predicates return truthy for acceptance; they receive and preserve the original value. Callback errors may expose their own messages.",
        ],
        undefined,
        [
          ["Predicates", "/docs/schemas/"],
          ["Error privacy", "/docs/errors/"],
        ],
      ),
      section(
        "environment-apis",
        "Environment variables",
        [
          "The env(name, cast, default) helper reads process environment variables. The load_env(path, schema=...) helper parses a .env file without mutating os.environ; with a schema it defaults to coercion and stripping unknown keys. Raw mode returns parsed strings.",
        ],
        undefined,
        [
          ["Configuration recipe", "/guides/config-validation/"],
          ["Feature availability", "/roadmap/"],
        ],
      ),
      section(
        "error-handling",
        "Error handling",
        [
          'Text mode raises ValueError. Choose error_mode="structured" for ValidationError. Do not log untrusted messages without reviewing their contents.',
        ],
        undefined,
        [["Errors", "/docs/errors/"]],
      ),
      section(
        "structured-errors",
        "Structured errors",
        [
          "ValidationError.issues retains path, message, expected, and got fields. Engine structured errors also expose immutable canonical details with machine codes and typed locations; manually constructed legacy errors can have details=None.",
        ],
        undefined,
        [["Structured error example", "/docs/errors/"]],
      ),
      section(
        "faq",
        "Which guide should I read?",
        [
          "Start from the boundary you need to validate. Every downloadable Python example is checked against the recorded PyPI release.",
        ],
        undefined,
        [
          ["Configuration", "/guides/config-validation/"],
          ["Command-line input", "/guides/cli-input-validation/"],
          ["JSON objects", "/guides/json-object-validation/"],
          ["Choosing a validator", "/compare/"],
        ],
      ),
    ],
    "Docs",
  ),
  page(
    "/docs/getting-started/",
    "Getting started",
    "Install zodify and validate your first Python dict, including a useful failure.",
    [
      section(
        "install",
        "Install the recorded release",
        [
          "Run python -m pip install zodify==0.8.0 in a virtual environment. Examples on this site require Python 3.10 or later and no optional packages.",
          "Pass the schema first and data second. Returned dicts contain validated values. Invalid input raises ValueError by default.",
        ],
        "quickstart",
        [
          ["Schema grammar", "/docs/schemas/"],
          ["Structured errors", "/docs/errors/"],
        ],
      ),
    ],
  ),
  page(
    "/docs/schemas/",
    "Schemas and predicates",
    "The released dict, list, union, and callable schema grammar.",
    [
      section(
        "grammar",
        "Describe a shape with Python values",
        [
          "A dict maps field names to schemas. A one-element list describes each item in a list. A Python type requires that exact type. PEP 604 unions combine types. Optional wraps an optional field.",
          "Predicates receive the original value and accept it when they return a truthy result. They do not transform values. A predicate should check its own input type before comparing or indexing it.",
        ],
        "schemas",
      ),
      section(
        "limits",
        "Keep schema boundaries explicit",
        [
          "Top-level data must be a dict (or a supported Schema declaration at the schema boundary). Lists with zero or multiple schema items are invalid. Malformed schemas may raise TypeError. Validation has a max_depth option, defaulting to 32; cyclic models and arbitrary typing expressions are not promised.",
          "Dict-shaped and list-shaped validation creates result containers, but leaf objects and defaults can remain shared. Validation is not a universal deep copy.",
        ],
        undefined,
        [["Ownership and defaults", "/docs/optional-and-defaults/"]],
      ),
    ],
  ),
  page(
    "/docs/types-and-coercion/",
    "Exact types, coercion, and unions",
    "Understand bool versus int, string conversion, and union order in zodify 0.8.0.",
    [
      section(
        "types",
        "Exact Python types by default",
        [
          "The int schema accepts an actual int. It rejects bool, float, and string values, even when they look numerically equivalent. Coercion is an explicit option.",
          "With coerce=True, string input can convert to int or float. Boolean strings are case-insensitive true/1/yes and false/0/no. Strings are not trimmed by the boolean rule. Conversion to str uses str(value); numeric schemas do not accept arbitrary constructor casting from non-string input.",
        ],
        "exact-types",
      ),
      section(
        "unions",
        "Union order can change string results",
        [
          "In coercing unions, exact non-string matches win first. String input then tries union members in their declared order: int | str can turn '1' into 1, while str | int preserves '1'. Without coercion, exact membership determines acceptance. Do not reorder a union casually.",
        ],
        undefined,
        [
          [
            "JSON integer semantics explained",
            "/articles/python-integers-and-json/",
          ],
          ["CLI recipe", "/guides/cli-input-validation/"],
        ],
      ),
    ],
  ),
  page(
    "/docs/optional-and-defaults/",
    "Missing keys, None, and defaults",
    "Distinguish optional keys from nullable values and understand released default ownership.",
    [
      section(
        "missing",
        "Missing and None are different inputs",
        [
          "Optional(str) permits an absent key, which is omitted from the result. str | None accepts a present null value but still requires the key. Optional(str, 'Ada') inserts a default only when the key is absent.",
        ],
        "optional-defaults",
      ),
      section(
        "ownership",
        "Defaults in the released version",
        [
          "In 0.8.0, a default is inserted as supplied. It is not independently validated or copied. Mutable defaults may be shared between calls. The executable example deliberately demonstrates an invalid default being inserted; this documents behavior, not a recommended configuration.",
          "Prefer immutable, type-correct defaults and construct fresh mutable values in application code. A future default policy belongs to a separately released migration; do not assume unreleased source changes apply to an installed package.",
        ],
        undefined,
        [
          ["Roadmap", "/roadmap/"],
          ["Schema containers", "/docs/schemas/"],
        ],
      ),
    ],
  ),
  page(
    "/docs/errors/",
    "Errors and privacy",
    "Catch released text and structured validation errors without assuming input redaction.",
    [
      section(
        "structured",
        "Choose structured errors explicitly",
        [
          "The default text mode raises ValueError. error_mode='structured' raises ValidationError, a ValueError subclass with an issues list. Each issue carries a string path, message, expected, and got. These legacy fields are preserved. Engine errors also expose a separate immutable details tuple of ValidationIssue records with machine codes and typed locations; manual legacy errors and unsupported key locations may have details=None. Mutating issues does not change the canonical snapshot.",
        ],
        "errors",
        [["Measured diagnostics cost", "/benchmarks/#diagnostics-cost"]],
      ),
      section(
        "privacy",
        "Treat error text as potentially sensitive",
        [
          "Coercion failures can include the original string, and custom callback exceptions can include callback messages. An issues list is not a promise of redaction. Avoid logging entire errors for credentials or user secrets; prefer an application-controlled message and a reviewed field identifier.",
          "Legacy paths use dots and brackets. Literal field names containing punctuation can be ambiguous. Do not parse these strings into an authoritative structural path.",
        ],
        undefined,
        [
          ["Schema predicates", "/docs/schemas/"],
          ["Roadmap", "/roadmap/"],
        ],
      ),
    ],
  ),
  page(
    "/docs/class-schemas/",
    "Optional class schemas",
    "Use Schema for attribute access while keeping the released syntax limits visible.",
    [
      section(
        "syntax",
        "One engine, optional declarations",
        [
          "Subclass Schema with concrete field annotations, then call validate(User, data) to get an instance with attributes. Dict schemas remain a first-class entry point; classes are an optional syntax choice.",
        ],
        "class-schemas",
      ),
      section(
        "limits",
        "Use the supported subset",
        [
          "Do not assume arbitrary postponed annotations, forward references, recursive models, general inheritance, generics, or every typing construct are supported. The example uses concrete annotations without 'from __future__ import annotations'.",
          "Validator is reusable validation configuration. In this release it is not a compiled schema cache.",
        ],
        undefined,
        [
          ["Dict schema reference", "/docs/schemas/"],
          ["Choosing a broader model tool", "/compare/"],
        ],
      ),
    ],
  ),
  page(
    "/guides/config-validation/",
    "Validate a configuration dict",
    "Catch missing keys and misspelled configuration, with an explicit strip alternative.",
    [
      section(
        "recipe",
        "Validate once at the configuration boundary",
        [
          "Keep strict validation for configuration that already has Python values. Reject unknown keys to catch misspellings. Insert a simple immutable default only for an intentionally optional setting.",
        ],
        "config-validation",
      ),
      section(
        "limits",
        "Make data loss an explicit choice",
        [
          "unknown_keys='strip' removes unknown fields from the returned shape; it does not fix misspellings. A type-only port check does not enforce the valid network-port range. Add a reviewed predicate if your application needs that constraint.",
          "This recipe validates a dict you already have. It does not load .env files, manage secrets, or infer configuration precedence.",
        ],
        undefined,
        [
          ["Schema predicates", "/docs/schemas/"],
          ["Defaults", "/docs/optional-and-defaults/"],
        ],
      ),
    ],
  ),
  page(
    "/guides/cli-input-validation/",
    "Validate command-line inputs",
    "Convert argparse strings deliberately and handle invalid command-line values.",
    [
      section(
        "recipe",
        "Convert at the input boundary",
        [
          "argparse can produce strings; coerce=True lets the validation step explicitly convert supported values. The example supplies an argument list so it runs reproducibly; use parser.parse_args() for real command-line arguments.",
        ],
        "cli-input-validation",
      ),
      section(
        "limits",
        "Keep the command-line contract small",
        [
          "The integer conversion checks a type, not a valid port range. Boolean conversion recognizes a small vocabulary. Handle errors with an application-controlled message if arguments may contain secrets.",
          "For a single argument, argparse's built-in type or choices may be enough. Use a shared validation schema when the same shape also comes from another boundary.",
        ],
        undefined,
        [
          ["Conversion and union rules", "/docs/types-and-coercion/"],
          ["Error privacy", "/docs/errors/"],
        ],
      ),
    ],
  ),
  page(
    "/guides/json-object-validation/",
    "Validate a JSON object",
    "Parse JSON with the standard library, enforce an object root, then validate Python fields.",
    [
      section(
        "recipe",
        "Parsing and validation are separate steps",
        [
          "Use json.loads() to parse the text, check for an object root, then validate its fields. Invalid JSON and a valid JSON object with incorrect fields fail at different boundaries.",
        ],
        "json-object-validation",
      ),
      section(
        "limits",
        "This is a Python object contract",
        [
          "The standard parser keeps the last duplicate object key and accepts non-finite numeric constants by default. This recipe does not promise duplicate-key rejection, strict JSON-number policy, or JSON Schema equivalence. Set input-size limits before parsing untrusted payloads.",
          "The int schema rejects a parsed 1.0 because it is a Python float. For a general JSON Schema contract, use a JSON Schema validator. The released zodify.json_io.validate_json helper provides a stricter parsing boundary than this standard-library recipe: it rejects duplicate keys, BOMs, nonfinite values and non-object roots before ordinary validation. zodify.json_schema.export_json_schema exports only the exact supported subset; numeric types, defaults, arbitrary predicates and bare containers are refused. The root to_json_schema facade returns only the document.",
        ],
        undefined,
        [
          [
            "Exact integers and JSON Schema",
            "/articles/python-integers-and-json/",
          ],
          ["Selection guide", "/compare/"],
        ],
      ),
    ],
  ),
  page(
    "/compare/",
    "Choosing a Python validator",
    "A task-based choice between small dict validation and broader validation tools.",
    [
      section(
        "choice",
        "Choose by the boundary you need",
        [
          "Zodify 0.8.0 is a fit for small plain-Python dict shapes, zero required runtime dependencies, and an explicit exact-type default. Its limited typing and interoperability surface is a tradeoff.",
          "Pydantic v2 TypeAdapter validates types without requiring a BaseModel subclass and provides serialization and JSON Schema generation. Consider it when those capabilities or Pydantic-compatible types matter. A model class is not required for every Pydantic task.",
          "For standards-based JSON Schema validation, choose an implementation of the required draft. For a tiny CLI, argparse alone may be enough. Compare your own accepted and rejected inputs before comparing timing.",
        ],
        undefined,
        [
          [
            "Pydantic TypeAdapter documentation (checked 2026-09-09)",
            "https://pydantic.dev/docs/validation/latest/concepts/type_adapter/",
          ],
          [
            "JSON Schema implementations",
            "https://json-schema.org/tools?query=&tooling_type=validator",
          ],
          ["Benchmark methodology", "/benchmarks/"],
        ],
      ),
      section(
        "evidence",
        "No universal speed ranking",
        [
          "This is a capability selection guide, not a timed library comparison. Zodify examples are checked against the installed 0.8.0 wheel. Pydantic capability statements refer to its current v2 documentation, checked September 9, 2026; no competitor timing is claimed.",
          "There are no invented adoption figures, maintenance rankings, or framework affiliations here.",
        ],
        undefined,
        [["Try a complete example", "/docs/getting-started/"]],
      ),
    ],
    "Compare",
  ),
  page(
    "/benchmarks/",
    "Benchmarks and measurement",
    "Reproducible measurement requirements and the limits of current performance claims.",
    [
      section(
        "status",
        "Measure a workload, not a slogan",
        [
          "We have withdrawn the earlier universal speed rankings and multiplier claims from this site. A scalar throughput figure cannot establish a fair cross-library ranking without equivalent semantics and setup accounting.",
          "No replacement cross-library ranking is published here. Repository experiments are development evidence and must identify their exact commit and environment before supporting a released-product claim.",
        ],
        undefined,
        [
          [
            "Benchmark source and artifacts",
            "https://github.com/junyoung2015/zodify/tree/main/benchmarks",
          ],
          ["Choose by capability", "/compare/"],
        ],
      ),
      section(
        "diagnostics-cost",
        "The cost of canonical diagnostics in 0.8.0",
        [
          "Versioned Python 3.12 flat and nested synthetic fixtures compared complete 0.8.0 and 0.6.0 versions on one machine. Structured-mode successful calls increased 36–43% and failed calls 61–64%. Default text-mode successes were approximately unchanged; text-mode failures increased 9–11%. Import median rose from about 2.3 ms to 4.3 ms.",
          "Typed locations require traversal work and failures retain both canonical records and legacy issues. These measurements describe a diagnostic capability cost, not application-level predictions or a cross-library ranking. No compiler is included.",
        ],
        undefined,
        [["0.8.0 release notes", "https://github.com/junyoung2015/zodify/blob/main/release-notes/v0.8.0.md"]],
      ),
      section(
        "protocol",
        "A reproducible comparison must include",
        [
          "Record the commit, installed-wheel version and hash, interpreter, platform, dependency versions, repeated raw samples, and the exact success/failure fixtures. Check output equivalence before timing. Include TypeAdapter for the appropriate Pydantic task.",
          "Measure setup separately from repeated validation. Report invalid input, strictness, unknown-key policy, nested shapes, import time, and installed footprint with named metric definitions. Avoid attributing a single scenario's result to every validation workload.",
          "Compilation experiments must report preparation cost, ordinary and prepared call costs, and a measured break-even point. A source experiment is not a released feature.",
        ],
        undefined,
        [
          ["Released feature availability", "/roadmap/"],
          [
            "An executable semantic comparison",
            "/articles/python-integers-and-json/",
          ],
        ],
      ),
    ],
    "Benchmarks",
  ),
  page(
    "/about/",
    "Why zodify exists",
    "The project's origin, author, design choices, and honest boundaries.",
    [
      section(
        "origin",
        "A validator for a small script",
        [
          "Jun Young Sohn (jusohn) created zodify while working on a small automation script involving environment variables and API keys. The original project account describes a roughly 20-line script and the wish for validation that fit its scale.",
          "That led to a dict-first interface: describe expected values with Python types and validate the dict at the boundary. Optional Schema declarations later added attribute access over the same engine.",
        ],
        undefined,
        [
          ["Project repository", "https://github.com/junyoung2015/zodify"],
          ["Try it", "/docs/getting-started/"],
        ],
      ),
      section(
        "choices",
        "Small, predictable scope",
        [
          "Zero required runtime dependencies, explicit coercion, and ordinary data shapes are deliberate choices. Zod-inspired describes an origin, not a full port or affiliation. The project uses the MIT license.",
          "Other tools solve broader problems. The selection guide explains where TypeAdapter or a JSON Schema implementation may serve your application better.",
        ],
        undefined,
        [
          ["Selection guide", "/compare/"],
          ["Roadmap", "/roadmap/"],
        ],
      ),
    ],
    "About",
  ),
  page(
    "/roadmap/",
    "Released, planned, and experimental",
    "Feature availability separated from unreleased source work and proposed designs.",
    [
      section(
        "released",
        "Released: 0.8.0",
        [
          "The verified 0.8.0 release provides validate, Optional, Validator, Schema, env, load_env, ValidationError and ValidationIssue. It preserves legacy structured issues and adds canonical details, strict JSON object input via zodify.json_io.validate_json, and conservative exact export via zodify.json_schema.export_json_schema and the root to_json_schema facade.",
        ],
        undefined,
        [
          ["PyPI release", "https://pypi.org/project/zodify/0.8.0/"],
          ["Current reference", "/docs/"],
        ],
      ),
      section(
        "future",
        "Not released in 0.8.0",
        [
          "Compilation and rich reports remain unavailable. Approximate export, native execution and source generation remain outside the current scope; future work requires separate semantic, evidence and release gates.",
          "Compilation requires an actual repeated-use workload and measured preparation economics before any public API is admitted. Version 0.8.0 remains alpha; publication does not establish a stable 1.0 contract.",
        ],
        undefined,
        [
          ["Development repository", "https://github.com/junyoung2015/zodify"],
          ["Changelog", "/changelog/"],
        ],
      ),
      section("limits", "Directions outside the initial scope", [
        "No hosted AI assistant, account system, paid documentation service, browser Python runtime, or recursive model framework is part of this website. Static search can be considered when navigation becomes insufficient.",
      ]),
    ],
  ),
  page(
    "/changelog/",
    "Release history",
    "Verified released package identity and the development changelog.",
    [
      section(
        "release",
        "0.8.0 — September 9, 2026",
        [
          "PyPI records the 0.8.0 wheel and source distribution on September 9, 2026. This site's release manifest was checked on September 9, 2026. It records the wheel SHA-256 and Python requirement independently from the working tree version.",
          "The repository changelog includes development changes; its presence does not mean those changes are available from PyPI.",
        ],
        undefined,
        [
          ["Verified 0.8.0 release", "https://pypi.org/project/zodify/0.8.0/"],
          [
            "Repository changelog",
            "https://github.com/junyoung2015/zodify/blob/main/CHANGELOG.md",
          ],
          ["Feature availability", "/roadmap/"],
        ],
      ),
    ],
  ),
  page(
    "/articles/python-integers-and-json/",
    "Why a Python int check is not JSON Schema integer",
    "An executable explanation of exact Python types and JSON numeric semantics.",
    [
      section(
        "question",
        "The same-looking number can have a different contract",
        [
          "In zodify 0.8.0, int means exact Python int. After standard-library JSON parsing, 1 becomes int and 1.0 becomes float. Python bool is also rejected by the int schema. The following example tests all four cases and the opt-in conversion alternative.",
        ],
        "exact-types",
      ),
      section(
        "standard",
        "JSON Schema answers a different question",
        [
          "JSON Schema considers a number with zero fractional part an integer, including 1.0. Python runtime type identity and mathematical integrality are distinct contracts. Translating int directly to a JSON Schema integer constraint does not preserve every acceptance decision.",
          "This is a semantic limitation, not a performance result. The 0.8.0 exact exporter refuses numeric declarations because of this mismatch; it does not imply complete equivalence. Use a JSON Schema validator when that standard is the authority for your payload.",
        ],
        undefined,
        [
          [
            "JSON Schema numeric reference (checked 2026-09-09)",
            "https://json-schema.org/understanding-json-schema/reference/numeric",
          ],
          [
            "Download and run the JSON recipe",
            "/guides/json-object-validation/",
          ],
          ["Exact-type reference", "/docs/types-and-coercion/"],
        ],
      ),
    ],
  ),
];
export const notFound = page(
  "/404.html",
  "Page not found",
  "This page does not exist. Find the released documentation or return to the homepage.",
  [
    section(
      "find",
      "Find what you need",
      [
        "The requested address is not a published page. Start with the docs index or one of the practical guides.",
      ],
      undefined,
      [
        ["Documentation", "/docs/"],
        ["Home", "/"],
      ],
    ),
  ],
);
