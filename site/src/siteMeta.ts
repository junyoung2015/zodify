export const SITE_VERSION = "v0.6.0";
export const SITE_VERSION_NUMBER = "0.6.0";
export const SITE_LAST_UPDATED = "March 10, 2026";

export const SITE_STATS = [
  { label: "VERSION", value: SITE_VERSION },
  { label: "OPS/SEC", value: "533K" },
  { label: "SIZE", value: "78KB" },
  { label: "DEPS", value: "0" },
  { label: "TESTS", value: "345" },
  { label: "SRC LOC", value: "808" },
] as const;

export const SITE_NUMBERS = {
  ops: "533K",
  importMs: "2.3ms",
  size: "78KB",
  deps: "0",
  tests: "345",
  sourceLoc: "808",
  latencyUs: "1.87µs",
} as const;
