/**
 * sweep_all.js —— 在单个浏览器会话内批量校验多个封面文件。
 * 用法：node tools/sweep_all.js <文件列表.txt>
 * 输出：每个文件的溢出/安全区/主次关系结果汇总。
 */
const fs = require('fs'); const path = require('path');
(async () => {
  const listFile = process.argv[2];
  if (!listFile || !fs.existsSync(listFile)) { console.log('[]'); return; }
  const files = fs.readFileSync(listFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch (e) { console.log(JSON.stringify({ skip: 'no-playwright' })); return; }
  let browser;
  try { browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}); }
  catch (e) { console.log(JSON.stringify({ skip: String(e.message).slice(0, 80) })); return; }
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const bad = []; const fitted = [];
  for (const f of files) {
    try {
      await page.goto('file:///' + path.resolve(f).replace(/\\/g, '/'));
      await page.waitForTimeout(120);
      const m = await page.evaluate(() => {
        const c = document.querySelector('.cover'); if (!c) return null;
        const fr = c.querySelector('.cv-frame'); const cr = c.getBoundingClientRect();
        const h1 = c.querySelector('.cv-title h1');
        // 先做与 fit_cover 一致的自适应缩放
        const cs0 = getComputedStyle(c);
        const baseTitle = parseFloat(cs0.getPropertyValue('--fs-title')) || 10;
        const wm0 = getComputedStyle(h1).writingMode || '';
        const vert0 = wm0.indexOf('vertical') === 0;
        function fits(sc) {
          c.style.setProperty('--fs-title', (baseTitle * sc).toFixed(2) + 'cqw');
          c.style.setProperty('--fs-sub', Math.max(1.6, baseTitle * sc * 0.30).toFixed(2) + 'cqw');
          const over = fr.scrollHeight > fr.clientHeight + 3 || fr.scrollWidth > fr.clientWidth + 3;
          const hOver = vert0 ? h1.scrollHeight > h1.clientHeight + 3 : h1.scrollWidth > h1.clientWidth + 3;
          return !over && !hOver;
        }
        let fitScale = 1;
        if (!fits(1)) {
          let lo = 0.5, hi = 1.0, best = 0.5;
          for (let i = 0; i < 24; i++) { const mid = (lo + hi) / 2; if (fits(mid)) { best = mid; lo = mid; } else { hi = mid; } }
          fitScale = best; fits(best);
        }
        const wm = getComputedStyle(h1).writingMode || '';
        const vert = wm.indexOf('vertical') === 0;
        const hOver = vert ? h1.scrollHeight > h1.clientHeight + 3 : h1.scrollWidth > h1.clientWidth + 3;
        function textRect(el) {
          const rg = document.createRange(); rg.selectNodeContents(el);
          const rs = Array.from(rg.getClientRects()).filter(x => x.width > 0.5 && x.height > 0.5);
          if (!rs.length) return null;
          let l = Infinity, t = Infinity, rr = -Infinity, b = -Infinity;
          rs.forEach(x => { l = Math.min(l, x.left); t = Math.min(t, x.top); rr = Math.max(rr, x.right); b = Math.max(b, x.bottom); });
          return { left: l, top: t, right: rr, bottom: b };
        }
        const mgn = Math.min(cr.width, cr.height) * 0.055; const viol = [];
        ['.cv-title', '.cv-meta', '.cv-kicker'].forEach(sel => {
          const e = c.querySelector(sel); if (!e || !e.textContent.trim()) return;
          const b = textRect(e); if (!b) return;
          if (b.left < cr.left + mgn - 2 || b.right > cr.right - mgn + 2 || b.top < cr.top + mgn - 2 || b.bottom > cr.bottom - mgn + 2) viol.push(sel.replace('.cv-', ''));
        });
        const tb = c.querySelector('.cv-title').getBoundingClientRect();
        const fg = c.querySelector('.cv-figure').getBoundingClientRect();
        return { over: fr.scrollHeight > fr.clientHeight + 3 || fr.scrollWidth > fr.clientWidth + 3, hOver,
                 viol, fitScale, titleArea: (tb.width*tb.height)/(cr.width*cr.height), figArea: (fg.width*fg.height)/(cr.width*cr.height) };
      });
      if (!m) { bad.push(f + ' :: 无 .cover'); continue; }
      const issues = [];
      if (m.over) issues.push('容器溢出');
      if (m.hOver) issues.push('标题溢出');
      if (m.viol.length) issues.push('安全区:' + m.viol.join('/'));
      if (m.titleArea < 0.03 && m.figArea > 0.3) issues.push('主次偏弱');
      if (issues.length) bad.push(path.basename(f) + ' :: ' + issues.join(' | '));
      else if (m.fitScale < 0.999) fitted.push(path.basename(f) + ' 缩放 ' + m.fitScale.toFixed(3));
    } catch (e) { bad.push(f + ' :: ' + String(e.message).slice(0, 60)); }
  }
  await browser.close();
  console.log(JSON.stringify({ total: files.length, bad: bad.length, details: bad, fitted: fitted }, null, 1));
})();
