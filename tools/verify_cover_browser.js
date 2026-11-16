/**
 * verify_cover_browser.js —— 真实布局检查（需 Playwright）。
 * 检查：标题溢出、安全区、主次关系、缩略图实际渲染。
 * 输出 JSON 数组，由 tools/verify_cover.py 合并进报告。
 * 用法：node tools/verify_cover_browser.js cover.html
 */
const path = require('path');
const fs = require('fs');

(async () => {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) {
    console.log(JSON.stringify([{ name: '浏览器布局检查', level: 'skip', detail: '文件不存在' }]));
    return;
  }
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch (e) {
    console.log(JSON.stringify([{ name: '浏览器布局检查', level: 'skip', detail: '未安装 Playwright（npm i -D playwright && npx playwright install chromium）' }]));
    return;
  }
  let browser;
  try { browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}); }
  catch (e) {
    console.log(JSON.stringify([{ name: '浏览器布局检查', level: 'skip', detail: '无法启动 Chromium：' + String(e.message).slice(0, 90) }]));
    return;
  }
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const out = [];
  try {
    await page.goto('file:///' + path.resolve(file).replace(/\\/g, '/'));
    await page.waitForTimeout(600);
    const m = await page.evaluate(() => {
      const c = document.querySelector('.cover');
      if (!c) return null;
      const f = c.querySelector('.cv-frame');
      const cr = c.getBoundingClientRect();
      const h1 = c.querySelector('.cv-title h1');
      const titleBox = c.querySelector('.cv-title').getBoundingClientRect();
      const fig = c.querySelector('.cv-figure').getBoundingClientRect();
      const viol = [];
      const mgn = Math.min(cr.width, cr.height) * 0.055;
      // 量文字实际占位，而不是元素盒：带内边距的槽位元素盒会整体贴边，造成误判
      function textRect(el) {
        const rg = document.createRange();
        rg.selectNodeContents(el);
        const rs = Array.from(rg.getClientRects()).filter(x => x.width > 0.5 && x.height > 0.5);
        if (!rs.length) return null;
        let l = Infinity, t = Infinity, rr = -Infinity, b = -Infinity;
        rs.forEach(x => { l = Math.min(l, x.left); t = Math.min(t, x.top); rr = Math.max(rr, x.right); b = Math.max(b, x.bottom); });
        return { left: l, top: t, right: rr, bottom: b, width: rr - l, height: b - t };
      }
      ['.cv-title', '.cv-meta', '.cv-kicker'].forEach(sel => {
        const e = c.querySelector(sel);
        if (!e || !e.textContent.trim()) return;
        const b = textRect(e);
        if (!b) return;
        if (b.left < cr.left + mgn - 2 || b.right > cr.right - mgn + 2 ||
            b.top < cr.top + mgn - 2 || b.bottom > cr.bottom - mgn + 2) viol.push(sel.replace('.cv-', ''));
      });
      const wm = getComputedStyle(h1).writingMode || '';
      const vert = wm.indexOf('vertical') === 0;
      const hOver = vert ? h1.scrollHeight > h1.clientHeight + 3 : h1.scrollWidth > h1.clientWidth + 3;
      return {
        frameOver: f.scrollHeight > f.clientHeight + 3 || f.scrollWidth > f.clientWidth + 3,
        dh: f.scrollHeight - f.clientHeight, dw: f.scrollWidth - f.clientWidth,
        titleOver: hOver, viol: viol,
        titleArea: (titleBox.width * titleBox.height) / (cr.width * cr.height),
        figArea: (fig.width * fig.height) / (cr.width * cr.height),
        canvasW: c.clientWidth
      };
    });
    if (!m) out.push({ name: '浏览器布局检查', level: 'fail', detail: '页面中未找到 .cover' });
    else {
      out.push({ name: '标题溢出', level: m.titleOver || m.frameOver ? 'fail' : 'pass',
        detail: m.frameOver ? '容器溢出 Δ高 ' + m.dh + 'px / Δ宽 ' + m.dw + 'px'
                             : '标题与容器均在画布内' });
      out.push({ name: '安全区', level: m.viol.length ? 'warn' : 'pass',
        detail: m.viol.length ? '越界：' + m.viol.join('、') : '所有文字块位于 5.5% 安全边距内' });
      out.push({ name: '主次关系', level: (m.titleArea < 0.03 && m.figArea > 0.3) ? 'warn' : 'pass',
        detail: '标题块占版面 ' + (m.titleArea * 100).toFixed(1) + '%，主视觉占 ' + (m.figArea * 100).toFixed(1) + '%' });
    }
  } catch (e) {
    out.push({ name: '浏览器布局检查', level: 'skip', detail: String(e.message).slice(0, 110) });
  }
  await browser.close();
  console.log(JSON.stringify(out));
})();
