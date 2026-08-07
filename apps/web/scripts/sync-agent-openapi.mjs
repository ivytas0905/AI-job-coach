import { execFileSync } from "node:child_process";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import openapiTS, { astToString } from "openapi-typescript";

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const agentRoot = resolve(webRoot, "../../agent");
const outputPath = resolve(webRoot, "src/types/generated/agent-openapi.ts");
const python = process.env.PYTHON ?? "python";
const source = execFileSync(
  python,
  ["-c", "import json; from agent_service.main import create_app; print(json.dumps(create_app().openapi()))"],
  { cwd: agentRoot, env: { ...process.env, PYTHONPATH: "src" }, encoding: "utf8", maxBuffer: 50 * 1024 * 1024 },
);
const schema = JSON.parse(source);
const generated = [
  "// Generated from agent_service FastAPI OpenAPI. Do not edit by hand.\n",
  astToString(await openapiTS(schema)),
].join("");

if (process.argv.includes("--check")) {
  let checked = "";
  try { checked = readFileSync(outputPath, "utf8"); } catch {}
  if (checked !== generated) {
    console.error("Agent OpenAPI types are stale. Run npm run api:sync and review the diff.");
    process.exitCode = 1;
  }
} else {
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, generated);
  console.log(`Updated ${outputPath}`);
}
