#!/usr/bin/env node
// Generate the GitHub wiki pages from the book sources.
//
//   node scripts/make-wiki.mjs <wiki-checkout-dir>
//
// Writes five pages (Home, Chapter-Guide, Figures, Tooling, Contributing-and-House-Style)
// plus _Sidebar and _Footer. Hand edits to these
// pages are overwritten; change this script or the book instead.
import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT, BOOK_TITLE, PDF_NAME, listParts, readPart, sections, figureMarkers } from "../lib/book.mjs";

const out = process.argv[2];
if (!out) throw new Error("Usage: node scripts/make-wiki.mjs <wiki-checkout-dir>");
mkdirSync(out, { recursive: true });

const REPO = "https://github.com/The-Studio-of-Sadiq/Electronics-and-Computing";
const BLOB = `${REPO}/blob/main`;
const RAW = "https://raw.githubusercontent.com/The-Studio-of-Sadiq/Electronics-and-Computing/main";
const PDF = `${BLOB}/pdf/${PDF_NAME}.pdf`;
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"];

const all = listParts();
const openers = all.filter((p) => p.kind === "part");
const chapters = all.filter((p) => p.kind === "chapter");
const wordCount = (s) => s.split(/\s+/).filter(Boolean).length;
const totalWords = chapters.reduce((n, c) => n + wordCount(readPart(c)), 0);
const totalFigs = chapters.reduce((n, c) => n + figureMarkers(c).length, 0);
const pdfPages = (() => {
  try {
    return (readFileSync(join(ROOT, "pdf", `${PDF_NAME}.pdf`), "latin1").match(/\/Type\s*\/Page[^s]/g) ?? []).length;
  } catch {
    return 0;
  }
})();

const partTitle = (p) => p.title.replace(/^Part [IVX]+ — /, "");
const partPage = (p) => `Part ${ROMAN[p.partNo]} — ${partTitle(p)}`;
const pageFile = (name) => name.replace(/ /g, "-").replace(/[^\w\-—,&]/g, "") + ".md";
const wikiLink = (name, label) => (label ? `[[${label}|${name}]]` : `[[${name}]]`);
const chTitle = (c) => c.title.replace(/^Chapter \d+ — /, "");

/** The opening questions of a chapter: the bold lines of its first blockquote. */
function questions(text) {
  const qs = [];
  for (const line of text.split(/\r?\n/)) {
    const m = /^>\s*\*\*(.+\?)\*\*\s*$/.exec(line);
    if (m) qs.push(m[1]);
    else if (qs.length && !line.startsWith(">")) break;
  }
  return qs;
}
const firstParagraph = (text) =>
  text.split(/\r?\n\s*\r?\n/).map((b) => b.trim()).find((b) => b && !/^[#*>|<!-]/.test(b)) ?? "";

const write = (name, body) => writeFileSync(join(out, pageFile(name)), body.trimEnd() + "\n");
const files = (p) => `[\`${p.relPath}\`](${BLOB}/${encodeURI(p.relPath)})`;

const toc = readFileSync(join(ROOT, "TOC.md"), "utf8");
const relation = /## Relation to the other books\s+([\s\S]*?)$/m.exec(toc)?.[1].trim() ?? "";

// ---------------------------------------------------------------- Home
write(
  "Home",
  `![${BOOK_TITLE}](${RAW}/docs/social-preview.png)

# ${BOOK_TITLE}

**Book 4 — The Electronics & Computing Core.** Electronic devices, analog and digital hardware, computer architecture, programming, embedded computation and hardware–software interaction: diodes and transistors, amplifiers and op-amps, logic and sequential design, processors, memory and FPGAs, HDLs, C/C++ and Python for engineers, embedded and real-time systems, power electronics, CMOS and VLSI, and co-design. It extends *Engineering Physics* and *Circuits, Signals and Communications* into devices, circuits and computing hardware.

## At a glance

| | |
|---|---|
| **Parts** | ${openers.length}: ${openers.map((p) => partTitle(p)).join(" → ")} |
| **Chapters** | ${chapters.length}, about ${Math.round(totalWords / 1000)}k words, each starting from an engineering problem |
| **Figures** | ${totalFigs}, each computed from the chapter's own numbers by a reproducible Python script |
| **Formats** | Markdown with LaTeX math (reads on GitHub and in Obsidian) and a typeset [PDF](${PDF})${pdfPages ? ` (${pdfPages} pages)` : ""} |
| **Tooling** | One-command PDF build, book checks in CI, and an MCP server for reading and searching the book with an AI client |
| **License** | MIT |

## Where to start

- **New reader:** read on, then open the ${wikiLink("Chapter Guide")} and begin at Chapter 1.
- **Looking for a topic:** the ${wikiLink("Chapter Guide")} lists every chapter's opening questions and sections.
- **Want the PDF:** download it [here](${PDF}) or from the [latest release](${REPO}/releases/latest), or build your own (${wikiLink("Tooling")}).
- **Using Claude or another AI client:** the book ships an MCP server (${wikiLink("Tooling")}).
- **Found an error or want to help:** see ${wikiLink("Contributing and House Style")}.

## The backbone

**devices → analog circuits → digital logic → computer hardware → software → embedded and real-time systems → power electronics → integrated circuits and co-design.**

One idea runs through all of it: a nonlinear device, biased and switched, is turned into a reliable abstraction (an amplifier, a logic gate, an instruction, a task, a converter), and every abstraction holds only inside the limits of voltage, current, time, power and temperature that the device beneath it sets. The diode law of Part I becomes the bias network of Part II, the noise margin of Part III, the memory cell of Part IV, the number format of Part V, the interrupt latency of Part VI, the switching loss of Part VII and the timing slack of Part VIII.

## The method

Each chapter starts from an **engineering problem** (a MOSFET that browns a board on a warm afternoon, an amplifier that oscillates when a cable is plugged in, a state machine that locks up after reset, an I²C bus that hangs after a brown-out, a buck converter that runs hot at light load, a chip that misses timing at the slow corner), builds a **model with stated assumptions**, solves it, and takes it to a **measurable consequence**. Real numbers come in tables with units and in worked examples recomputed in full; each chapter closes with a *What remains open* table. There are no exercises.

After every important law, theorem or rule a box states what kind of truth it is:

| Label | Meaning | Examples |
|---|---|---|
| **Fundamental** | Follows from physical law or the system's definition | Charge conservation behind KCL, the Boltzmann factor in the diode law, Boolean algebra as two-valued logic |
| **Derived** | A mathematical consequence of more basic results | The hybrid-π model, the closed-loop gain formula, two's-complement arithmetic, Amdahl's law, buck volt-second balance, CMOS dynamic power |
| **Approximate** | Valid under stated assumptions | The ideal op-amp, the constant-drop diode, square-law MOSFET, the Miller approximation, linear-ripple converter formulas |
| **Empirical** | Fitted to observation | Moore's law, the 10 °C capacitor-life rule, Arrhenius reliability, Rent's rule, cache miss-rate curves |

## Boundaries with the other books

${relation}

## FAQ

**What do I need to know first?** Calculus, complex numbers, linear algebra and differential equations; semiconductor physics as in *Engineering Physics*; circuit analysis, frequency response and Laplace methods as in *Circuits, Signals and Communications*. Results from those books are cited with links where they are used.

**Can I read it in Obsidian?** Yes: open the repository folder as a vault; math and links work.

**Can I reuse it?** Yes, under the MIT License. Please credit the book; [\`CITATION.cff\`](${BLOB}/CITATION.cff) gives a citation.
`,
);

// ---------------------------------------------------------------- Chapter guide
let guide = `# Chapter Guide

Every chapter with the questions it opens with and its sections. Click a chapter to read it on GitHub.

`;
for (const op of openers) {
  guide += `## ${partPage(op)}\n\n${firstParagraph(readPart(op))}\n\n*Part opener:* ${files(op)}\n\n`;
  for (const c of chapters.filter((x) => x.partNo === op.partNo)) {
    const t = readPart(c);
    guide += `### ${c.id}. [${chTitle(c)}](${BLOB}/${encodeURI(c.relPath)})\n\n`;
    guide += questions(t).map((q) => `> ${q}`).join("\n>\n") + "\n\n";
    const secs = sections(t).slice(1).filter((s) => s.number);
    guide += `<details><summary>${secs.length} sections · ${figureMarkers(c).length} figures</summary>\n\n`;
    guide += secs.map((s) => `- **${s.number}** ${s.title}`).join("\n") + "\n\n</details>\n\n";
  }
}
write("Chapter Guide", guide);

// ---------------------------------------------------------------- Figures
const kinds = {};
for (const c of chapters) for (const f of figureMarkers(c)) kinds[f.kind] = (kinds[f.kind] ?? 0) + 1;
const gallery = ["1.5", "3.2", "7.4", "10.4", "14.5", "16.4", "27.4", "30.6", "33.1"];
const figByNo = new Map(chapters.flatMap((c) => figureMarkers(c).map((f) => [f.number, f])));
write(
  "Figures",
  `# Figures

The book has **${totalFigs} figures**. Every one is specified by a \`<!-- FIGURE ... -->\` marker at the point it belongs in its chapter and drawn by a Python script, \`figures/scripts/chNN.py\`, from the same numbers the text uses (numpy, scipy, matplotlib; circuits, logic and timing diagrams with schemdraw). The full plan, with what each figure shows, is [\`FIGURES.md\`](${BLOB}/FIGURES.md).

## Regenerating

\`\`\`bash
pip install -r requirements.txt
python scripts/build-figures.py          # all chapters
python scripts/build-figures.py ch07     # one chapter
node scripts/insert-figures.mjs          # place newly drawn figures below their markers
npm run figures:plan                     # rebuild FIGURES.md
\`\`\`

CI runs every figure script on each push.

## By kind

| Kind | Count |
|---|---|
${Object.entries(kinds)
  .sort((a, b) => b[1] - a[1])
  .map(([k, n]) => `| ${k} | ${n} |`)
  .join("\n")}

## By chapter

| Ch. | Title | Figures |
|---|---|---|
${chapters.map((c) => `| ${c.id} | ${chTitle(c)} | ${figureMarkers(c).length} |`).join("\n")}

## Gallery

${gallery
  .map((n) => figByNo.get(n))
  .filter(Boolean)
  .map((f) => `### Figure ${f.number}\n\n![Figure ${f.number}](${RAW}/${f.path})\n\n*${f.caption}*`)
  .join("\n\n")}
`,
);

// ---------------------------------------------------------------- Tooling
const mcpReadme = readFileSync(join(ROOT, "mcp", "README.md"), "utf8")
  .replace(/^# .*\n/, "")
  .replace(/^## /gm, "### ");
write(
  "Tooling",
  `# Tooling

Everything that turns the Markdown into a PDF, checks it, and serves it to AI clients.

## Building the PDF

The PDF is built from the Markdown sources: [markdown-it](https://github.com/markdown-it/markdown-it) renders the text, [KaTeX](https://katex.org) typesets the math on the server side, and a local headless Chrome, Edge or Chromium prints the result through [puppeteer-core](https://pptr.dev), with clickable contents and PDF bookmarks.

### Requirements

- Node.js ≥ 18
- Google Chrome, Microsoft Edge or Chromium (set \`CHROME_PATH\` if it is not found automatically)

### Build

\`\`\`bash
npm install
npm run pdf
\`\`\`

This writes \`dist/${PDF_NAME}.pdf\` and reports any math expression that failed to render or any missing image. To build an excerpt (part openers are \`P1\`…\`P8\`, chapters \`1\`…\`35\`):

\`\`\`bash
node scripts/build-pdf.mjs --parts P3,11,12 --out dist/excerpt.pdf
\`\`\`

Add \`--html\` to keep the intermediate HTML for debugging.

### Releases

The **Build PDF and release** workflow (\`.github/workflows/release.yml\`) builds the PDF on GitHub's Ubuntu runners. Pushing a version tag publishes a release with the PDF attached and the matching section of [\`CHANGELOG.md\`](${BLOB}/CHANGELOG.md) as notes:

\`\`\`bash
git tag v1.0.1
git push origin v1.0.1
\`\`\`

Running the workflow by hand (**Actions → Build PDF and release → Run workflow**) uploads the PDF as a build artifact instead.

## Book checks and CI

The **Check book** workflow runs on every push and pull request: \`npm run check\` (TOC coverage, chapter layout, math delimiters, figure markers, links; the figure plan is up to date; the MCP smoke test) and every figure script.

## MCP server
${mcpReadme.replace(/\(\.\.\/scripts\/build-pdf\.mjs\)/g, `(${BLOB}/scripts/build-pdf.mjs)`)}
### Example questions to ask

- "Using the electronics-computing book, explain why the IRF540N in the opening of Chapter 4 overheats at 3.3 V gate drive."
- "Search the book for every place it uses volt-second balance and summarise the method."
- "Show me Figure 14.5 and explain why a two-flip-flop synchronizer's MTBF grows so fast with resolution time."
- "Build a PDF of Part VI only."

### Testing

\`node scripts/mcp-smoke.mjs\` starts the server and exercises every read-only tool; CI runs it on each push.
`,
);

// ---------------------------------------------------------------- Contributing
const contributing = readFileSync(join(ROOT, "CONTRIBUTING.md"), "utf8")
  .replace(/^# .*\n/, "")
  .replace(/\]\(\.\.\/\.\.\/issues/g, `](${REPO}/issues`)
  .replace(/\]\((CODE_OF_CONDUCT|LICENSE|TOC|FIGURES)(\.md)?\)/g, `](${BLOB}/$1$2)`)
  .replace(/\]\(`?(TOC\.md|FIGURES\.md)`?\)/g, `](${BLOB}/$1)`);
write(
  "Contributing and House Style",
  `# Contributing and House Style

*Mirrored from [\`CONTRIBUTING.md\`](${BLOB}/CONTRIBUTING.md); edit that file, not this page.*
${contributing}`,
);

// ---------------------------------------------------------------- Sidebar and footer
write(
  "_Sidebar",
  `**${BOOK_TITLE}**

- ${wikiLink("Home")}
- ${wikiLink("Chapter Guide")}
- ${wikiLink("Figures")}
- ${wikiLink("Tooling")}
- ${wikiLink("Contributing and House Style")}

**Links**

- [Read the PDF](${PDF})
- [Latest release](${REPO}/releases/latest)
- [Syllabus (TOC.md)](${BLOB}/TOC.md)
- [Report an error](${REPO}/issues/new?template=erratum.yml)
`,
);
write(
  "_Footer",
  `*${BOOK_TITLE}* · Book 4 of the EEE series · [Repository](${REPO}) · [PDF](${PDF}) · MIT License · These pages are generated by [\`scripts/make-wiki.mjs\`](${BLOB}/scripts/make-wiki.mjs).`,
);

console.error(`Wrote 5 wiki pages plus sidebar and footer to ${out}`);
