// Render real page bodies after Vite has produced the CSS asset.
import { spawnSync } from "node:child_process";
const result = spawnSync(
  process.execPath,
  ["--import", "tsx", "scripts/render-static.tsx"],
  { stdio: "inherit" },
);
process.exit(result.status ?? 1);
