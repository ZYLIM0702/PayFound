// Writes apps/api/app/assistant/openui_prompt.txt from the PayFound OpenUI library spec.
// Bundles only our spec module (no React/CSS) with esbuild; packages stay external.
import { build } from 'esbuild';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = resolve(root, '../api/app/assistant/openui_prompt.txt');
const tmp = resolve(root, 'node_modules/.cache/agent-prompt.mjs');
const entry = `
import { buildLibrary, promptOptions, specs } from ${JSON.stringify(resolve(root, 'src/pages/agent/library.spec.ts'))};
const stub = () => null;
const library = buildLibrary(Object.fromEntries(Object.keys(specs).map(k => [k, stub])));
export const prompt = library.prompt(promptOptions);
`;
await mkdir(dirname(tmp), { recursive: true });
await build({ stdin: { contents: entry, resolveDir: root, loader: 'ts' }, bundle: true, platform: 'node', format: 'esm', packages: 'external', outfile: tmp, logLevel: 'warning' });
const { prompt } = await import(pathToFileURL(tmp).href + `?t=${Date.now()}`);
await mkdir(dirname(out), { recursive: true });
await writeFile(out, prompt.trimEnd() + '\n');
await rm(tmp, { force: true });
console.log(`Wrote ${out} (${prompt.length} chars)`);
