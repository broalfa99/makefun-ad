// bring-the-humans-03 entry: the video is the entry. This program only hands the house the
// address of the TikTok video, by copying VIDEO.json from the repository root to the output dir.
// Local run: mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const raw = readFileSync(join(botDir, 'VIDEO.json'), 'utf8');
const video = JSON.parse(raw) as { url?: unknown };
if (typeof video.url !== 'string') {
  console.error('VIDEO.json has no url string');
  process.exit(1);
}
if (!/^https:\/\/(www\.|m\.)?tiktok\.com\/@[^/]+\/video\/\d+/.test(video.url)) {
  console.warn(`warning: ${video.url} is not a full TikTok video address yet`);
}
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'VIDEO.json'), raw);
console.log(`handed in ${video.url}`);
