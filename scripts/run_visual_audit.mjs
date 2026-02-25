import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const outputDir = path.join(root, ".artifacts", "verification");
fs.mkdirSync(outputDir, { recursive: true });

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  const playwrightUrl = pathToFileURL(
    path.join(root, "apps", "web", "node_modules", "playwright", "index.mjs")
  ).href;
  ({ chromium } = await import(playwrightUrl));
}

const viewports = [
  { name: "desktop", width: 1440, height: 940 },
  { name: "tablet", width: 1024, height: 768 },
  { name: "mobile", width: 390, height: 844 },
];

const report = [];
const browser = await chromium.launch({ headless: true });

for (const vp of viewports) {
  const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
  await page.goto("http://127.0.0.1:5173/", { waitUntil: "networkidle" });
  await page.locator(".react-flow__node").first().click({ force: true });
  await page.locator(".react-flow__node").nth(1).click({ force: true });
  await page.locator(".toolbar button", { hasText: "Validate" }).click();
  await page.locator(".toolbar button", { hasText: "Run Preview" }).click();
  await page.waitForTimeout(600);

  const metrics = await page.evaluate(() => {
    const previewCards = document.querySelectorAll(".previewCard").length;
    const imageCards = document.querySelectorAll(".previewCard img").length;
    const traceCount = document.querySelectorAll(".traceList li").length;
      const statusText = document.querySelector(".statusCard")?.textContent ?? "";
    const canvasRect = document.querySelector(".canvas")?.getBoundingClientRect();
    const panelTexts = Array.from(document.querySelectorAll(".sidePanelRight .previewCard"))
      .map((el) => (el.textContent || "").slice(0, 120));
    return {
      previewCards,
      imageCards,
      traceCount,
        statusText,
      canvasHeight: canvasRect ? Math.round(canvasRect.height) : 0,
      canvasWidth: canvasRect ? Math.round(canvasRect.width) : 0,
      sampleTexts: panelTexts.slice(0, 3),
    };
  });

  const screenshotPath = path.join(outputDir, `visual-${vp.name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  report.push({ viewport: vp, ...metrics, screenshot: screenshotPath });
  await page.close();
}

await browser.close();
const reportPath = path.join(outputDir, "visual-audit-report.json");
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf-8");
console.log(reportPath);

// Assert correctness and gate on failures
let failures = 0;
for (const r of report) {
  const vp = r.viewport.name;
  if (r.previewCards === 0) { console.error(`FAIL [${vp}]: no preview cards rendered`); failures++; }
  if (r.traceCount === 0) { console.error(`FAIL [${vp}]: no trace entries`); failures++; }
  if (r.canvasWidth === 0 || r.canvasHeight === 0) { console.error(`FAIL [${vp}]: canvas not rendered (${r.canvasWidth}x${r.canvasHeight})`); failures++; }
}

if (failures > 0) {
  console.error(`\n${failures} assertion(s) failed across ${report.length} viewports`);
  process.exit(1);
}
console.log(`All ${report.length} viewports passed assertions.`);
