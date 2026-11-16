/**
 * fit_cover.js —— 测量封面标题溢出，二分求出最大可容纳的标题缩放。
 * 输出 JSON：{ scale, needed, ok }
 */
const fs = require('fs'); const path = require('path');
(async () => {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) { console.log(JSON.stringify({ ok:false, reason:'file-missing' })); return; }
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch (e) { console.log(JSON.stringify({ ok:false, reason:'no-playwright' })); return; }
  let browser;
  try { browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}); }
  catch (e) { console.log(JSON.stringify({ ok:false, reason:'no-chromium' })); return; }
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  await page.goto('file:///' + path.resolve(file).replace(/\\/g, '/'));
  await page.waitForTimeout(200);
  const res = await page.evaluate(() => {
    const c = document.querySelector('.cover'); if (!c) return { ok:false };
    const fr = c.querySelector('.cv-frame');
    const h1 = c.querySelector('.cv-title h1');
    const cs = getComputedStyle(c);
    const baseTitle = parseFloat(cs.getPropertyValue('--fs-title')) || 10;
    const baseSub = parseFloat(cs.getPropertyValue('--fs-sub')) || 3;
    const wm = getComputedStyle(h1).writingMode || '';
    const vert = wm.indexOf('vertical') === 0;
    function fits(scale) {
      c.style.setProperty('--fs-title', (baseTitle * scale).toFixed(2) + 'cqw');
      c.style.setProperty('--fs-sub', Math.max(1.6, baseTitle * scale * 0.30).toFixed(2) + 'cqw');
      const over = fr.scrollHeight > fr.clientHeight + 3 || fr.scrollWidth > fr.clientWidth + 3;
      const hOver = vert ? h1.scrollHeight > h1.clientHeight + 3 : h1.scrollWidth > h1.clientWidth + 3;
      return !over && !hOver;
    }
    if (fits(1)) return { ok:true, scale:1, needed:1 };
    let lo = 0.5, hi = 1.0, best = 0.5;
    for (let i = 0; i < 24; i++) {
      const mid = (lo + hi) / 2;
      if (fits(mid)) { best = mid; lo = mid; } else { hi = mid; }
    }
    fits(best);
    return { ok:true, scale: Math.round(best * 1000) / 1000, needed: baseTitle, baseSub: baseSub };
  });
  await browser.close();
  console.log(JSON.stringify(res));
})();
