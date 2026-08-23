import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

async function main() {
  const [svgPath, pngPath, sharpModulePath] = process.argv.slice(2);
  if (!svgPath || !pngPath || !sharpModulePath) {
    throw new Error("usage: node render_status_png.mjs <input.svg> <output.png> <sharp-module-path>");
  }
  const sharpModule = await import(pathToFileURL(path.resolve(sharpModulePath)).href);
  const sharp = sharpModule.default ?? sharpModule;
  const svg = await fs.readFile(svgPath);
  await sharp(svg).png().toFile(pngPath);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
