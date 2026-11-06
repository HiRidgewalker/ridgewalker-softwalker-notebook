#!/usr/bin/env node
/**
 * 将 Obsidian wikilink 语法转换为标准 Markdown 链接。
 *
 *   [[Go笔记]]            -> [Go笔记](./Go笔记.md)
 *   [[Go笔记#1.2 基础]]   -> [Go笔记 > 1.2 基础](./Go笔记.md#1.2 基础)
 *
 * 代码块与行内代码内的 [[...]] 保持原样（它们是文档示例的一部分）。
 *
 * 用法：
 *   node scripts/convert-wikilinks.mjs --dry-run   仅报告，不改文件
 *   node scripts/convert-wikilinks.mjs              实际写入
 */
import fs from 'node:fs';
import path from 'node:path';

const HUB = path.resolve('hub');
const DRY_RUN = process.argv.includes('--dry-run');

const files = fs.readdirSync(HUB).filter((f) => f.endsWith('.md'));
const basenames = new Set(files.map((f) => f.replace(/\.md$/, '')));

const stats = {
  filesScanned: files.length,
  filesChanged: 0,
  linksConverted: 0,
  linksWithAnchor: 0,
  linksInCode: 0,
  missingTargets: 0,
};
const missing = new Set();
const anchors = [];
const samples = [];

const CODE_TOKEN = '\u0000CODE';

function protectCode(text) {
  const stash = [];
  const push = (m) => {
    stash.push(m);
    return `${CODE_TOKEN}${stash.length - 1}\u0000`;
  };
  // 围栏代码块（含 ~~~），非贪婪；先于行内代码处理
  let out = text.replace(/(`{3,}|~{3,})[\s\S]*?\1/g, push);
  // 行内代码
  out = out.replace(/`[^`\n]+`/g, push);
  return {out, stash};
}

function restoreCode(text, stash) {
  return text.replace(/\u0000CODE(\d+)\u0000/g, (_, i) => stash[Number(i)]);
}

function encodeHref(fileName) {
  // 只编码空格，中文保持原样（浏览器与 Docusaurus 均支持）
  return `./${fileName.replace(/ /g, '%20')}`;
}

function convertFile(file) {
  const full = path.join(HUB, file);
  const original = fs.readFileSync(full, 'utf8');
  const rawCount = (original.match(/\[\[[^\]]+\]\]/g) || []).length;

  const {out: protectedText, stash} = protectCode(original);
  let convertedInBody = 0;

  const transformed = protectedText.replace(/\[\[([^\]]+)\]\]/g, (match, inner) => {
    const hashIdx = inner.indexOf('#');
    const target = (hashIdx === -1 ? inner : inner.slice(0, hashIdx)).trim();
    const anchor = hashIdx === -1 ? '' : inner.slice(hashIdx + 1).trim();

    if (!basenames.has(target)) {
      stats.missingTargets++;
      missing.add(`${file}: [[${inner}]]`);
      return match;
    }

    convertedInBody++;
    stats.linksConverted++;
    if (anchor) {
      stats.linksWithAnchor++;
      anchors.push(`${file}  ->  ${target}#${anchor}`);
    }

    const targetFile = `${target}.md`;
    const label = anchor ? `${target} > ${anchor}` : target;
    const href = anchor
      ? `${encodeHref(targetFile)}#${anchor.replace(/ /g, '%20')}`
      : encodeHref(targetFile);

    const replacement = `[${label}](${href})`;
    if (samples.length < 12) {
      samples.push(`  ${file}\n    ${match}\n    -> ${replacement}`);
    }
    return replacement;
  });

  // 代码块 / 行内代码内保留的 wikilink 数量（仅统计，不转换）
  const inCode = (stash.join('\n').match(/\[\[[^\]]+\]\]/g) || []).length;
  stats.linksInCode += inCode;

  const finalText = restoreCode(transformed, stash);
  if (finalText !== original) {
    stats.filesChanged++;
    if (!DRY_RUN) {
      fs.writeFileSync(full, finalText, 'utf8');
    }
  }

}

for (const file of files) convertFile(file);

console.log(`\n${'='.repeat(56)}`);
console.log(`wikilink 转换${DRY_RUN ? '（DRY RUN，未写入）' : ''}`);
console.log('='.repeat(56));
console.log(`扫描文件        ${stats.filesScanned}`);
console.log(`涉及变更文件    ${stats.filesChanged}`);
console.log(`成功转换        ${stats.linksConverted}`);
console.log(`  其中带锚点    ${stats.linksWithAnchor}`);
console.log(`代码块内跳过    ${stats.linksInCode}`);
console.log(`目标不存在      ${stats.missingTargets}`);

if (samples.length) {
  console.log('\n--- 转换样例 ---');
  console.log(samples.join('\n'));
}

if (anchors.length) {
  console.log('\n--- 带锚点的链接（构建后需校验跳转） ---');
  console.log(anchors.map((a) => `  ${a}`).join('\n'));
}

if (missing.size) {
  console.log('\n--- 目标不存在的 wikilink ---');
  console.log([...missing].map((m) => `  ${m}`).join('\n'));
}

if (DRY_RUN) {
  console.log('\n加 --write 参数才会实际写入。');
}
