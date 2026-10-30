/* WebKit swipe专项 tests for PAI website (TJPAI/pai-web, QA branch only).
 *
 * Covers what tools/verify_current_ui.cjs does NOT: real left/right page
 * swipes, gesture cancel, rapid consecutive swipes, edge-guard (iOS
 * back-gesture zone), short-swipe settle-back, vertical-scroll guard,
 * outside-click menu dismissal, and Back/Forward scroll restoration.
 *
 * Playwright WebKit exposes touchscreen.tap only (no touch drag API, and
 * WebKit has no CDP Input.dispatchTouchEvent), and this WebKit build
 * rejects `new Touch()` ("Illegal constructor") and rejects createTouch()
 * objects in `new TouchEvent()` ("Type error"), so swipes are driven with
 * synthetic cancelable Events carrying Touch-like touch lists (see
 * dispatchTouch). That exercises the site's real
 * touchstart/touchmove/touchend/touchcancel handlers in the real
 * WebKit JavaScript engine (thresholds, edge guard, preview fetch,
 * commit/settle animation). It does NOT test the iOS system edge-back
 * gesture recognizer or real finger input; see the QA report limitations.
 *
 * Run: PAI_BROWSER=webkit node tools/verify_webkit_swipe.cjs
 * Engine selection mirrors verify_current_ui.cjs.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium, webkit } = require('playwright');

const engine = process.env.PAI_BROWSER === 'webkit' ? webkit : chromium;
const BASE = 'https://tjpai.github.io/pai-web/';
const ROOT = path.resolve(__dirname, '..');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const results = [];
let failures = 0;
async function check(name, fn) {
  try {
    await fn();
    results.push(`PASS ${name}`);
    console.log(`PASS ${name}`);
  } catch (e) {
    failures += 1;
    results.push(`FAIL ${name}: ${e.message}`);
    console.log(`FAIL ${name}: ${e.message}`);
  }
}

// Dispatch one synthetic TouchEvent on a plain <p> inside <main> (never a
// link/button, which the site deliberately excludes from swiping).
// WebKit limitation (verified 2026-10-31 in Playwright 1.56.1 WebKit):
// `new Touch()` throws "Illegal constructor" and `new TouchEvent()`
// rejects createTouch() Touch objects with "Type error", so the event is a
// plain cancelable Event carrying Touch-like touch lists via defineProperty.
// The site's handlers only read touches/changedTouches/target and call
// preventDefault(), all of which this preserves; the handlers under test
// are the real ones running in the real WebKit engine.
async function dispatchTouch(page, type, touches, changedTouches) {
  await page.evaluate(
    ({ type, touches, changedTouches }) => {
      const target = document.querySelector('main p') || document.querySelector('main');
      const mk = (t) => ({ identifier: 1, target, clientX: t.x, clientY: t.y });
      const ev = new Event(type, { bubbles: true, cancelable: true });
      Object.defineProperty(ev, 'touches', { value: touches.map(mk) });
      Object.defineProperty(ev, 'targetTouches', { value: touches.map(mk) });
      Object.defineProperty(ev, 'changedTouches', { value: changedTouches.map(mk) });
      target.dispatchEvent(ev);
    },
    { type, touches, changedTouches },
  );
}

// Full swipe: touchstart -> progressive touchmoves -> optional hold (lets the
// site fetch the preview page) -> touchend. Distance |dx| >= 58 commits.
async function swipe(page, fromX, toX, y = 320, { stepMs = 30, holdMs = 350 } = {}) {
  await dispatchTouch(page, 'touchstart', [{ x: fromX, y }], [{ x: fromX, y }]);
  const steps = 5;
  for (let i = 1; i <= steps; i += 1) {
    const x = fromX + ((toX - fromX) * i) / steps;
    await dispatchTouch(page, 'touchmove', [{ x, y }], [{ x, y }]);
    await sleep(stepMs);
  }
  if (holdMs) await sleep(holdMs);
  await dispatchTouch(page, 'touchend', [], [{ x: toX, y }]);
}

async function swipeAndWaitUrl(page, fromX, toX, url, y = 320, opts) {
  await swipe(page, fromX, toX, y, opts);
  await page.waitForURL(url, { timeout: 8000 });
  await sleep(700); // settle animation (330ms) + preview cleanup
}

async function assertCleanPage(page, label) {
  const state = await page.evaluate(() => ({
    title: document.title,
    mainText: (document.querySelector('main')?.innerText || '').trim().length,
    mainTransform: document.querySelector('main')?.style.transform || '',
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    previewShells: [...document.querySelectorAll('body > div')].filter(
      (d) => d.getAttribute('aria-hidden') === 'true' && d.style.position === 'fixed',
    ).length,
    url: location.href,
  }));
  assert.ok(state.title.length > 0, `${label}: empty title`);
  assert.ok(state.mainText > 50, `${label}: white/empty main (text ${state.mainText})`);
  assert.equal(state.mainTransform, '', `${label}: main transform not cleared: ${state.mainTransform}`);
  assert.ok(state.overflow <= 2, `${label}: horizontal overflow ${state.overflow}`);
  assert.equal(state.previewShells, 0, `${label}: leftover swipe preview shell`);
}

async function waitScrollY(page, expected, timeout = 5000) {
  try {
    await page.waitForFunction((y) => Math.abs(window.scrollY - y) <= 2, expected, { timeout });
  } catch (e) {
    const state = await page.evaluate(() => ({
      url: location.pathname,
      y: Math.round(scrollY),
      hist: history.state,
      ss: sessionStorage.getItem('pai-page-scroll-v1'),
    }));
    throw new Error(`scrollY did not reach ${expected}: ${JSON.stringify(state)}`);
  }
}

// applyPage clears main's inline willChange only when the SPA transition
// fully finishes (after the 105ms + 175ms animations). Waiting for it
// before issuing the next history navigation avoids racing the site's
// `navigating` guard, which drops a second navigation issued mid-transition.
async function waitSettled(page, timeout = 5000) {
  await page.waitForFunction(
    () => {
      const m = document.querySelector('main');
      return !!m && m.style.willChange === '';
    },
    { timeout },
  );
}

(async () => {
  const browser = await engine.launch({
    headless: true,
    ...(engine === chromium ? { args: ['--no-sandbox'] } : {}),
  });
  const errs = [];
  try {
    const ctx = await browser.newContext({
      viewport: { width: 390, height: 844 },
      locale: 'zh-CN',
      isMobile: true,
      hasTouch: true,
    });
    await ctx.route(BASE + '**', (route) => {
      const u = new URL(route.request().url());
      let name = decodeURIComponent(u.pathname.slice('/pai-web/'.length));
      if (!name || name.endsWith('/')) name += 'index.html';
      const file = path.resolve(ROOT, name);
      if (!file.startsWith(ROOT + path.sep) || !fs.existsSync(file)) {
        return route.fulfill({ status: 404, body: name });
      }
      const ext = path.extname(file).toLowerCase();
      const mime = {
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
      }[ext] || 'application/octet-stream';
      return route.fulfill({ status: 200, body: fs.readFileSync(file), contentType: mime });
    });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errs.push(e.message));

    // TouchEvent/Touch constructors must exist in this WebKit build.
    await check('Touch/TouchEvent constructors exist', async () => {
      await p.goto(BASE + 'about.html');
      const ok = await p.evaluate(
        () => typeof Touch === 'function' && typeof TouchEvent === 'function',
      );
      assert.equal(ok, true);
    });

    // 1. Swipe left (dx<0) moves forward in page order: about -> team (zh).
    await check('swipe left zh about -> team', async () => {
      await p.goto(BASE + 'about.html');
      await swipeAndWaitUrl(p, 300, 75, BASE + 'team.html');
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/team.html');
      await assertCleanPage(p, 'team after swipe left');
    });

    // 2. Swipe right (dx>0) moves back: team -> about (zh).
    await check('swipe right zh team -> about', async () => {
      await swipeAndWaitUrl(p, 75, 300, BASE + 'about.html');
      await assertCleanPage(p, 'about after swipe right');
    });

    // 3. Bilingual: en about -> en team -> en about.
    await check('swipe left/right en about <-> team', async () => {
      await p.goto(BASE + 'en/about.html');
      await swipeAndWaitUrl(p, 300, 75, BASE + 'en/team.html');
      await assertCleanPage(p, 'en team after swipe left');
      await swipeAndWaitUrl(p, 75, 300, BASE + 'en/about.html');
      await assertCleanPage(p, 'en about after swipe right');
    });

    // 4. Rapid consecutive swipes: about -> team -> research without long waits.
    await check('rapid consecutive swipes about -> team -> research', async () => {
      await p.goto(BASE + 'about.html');
      await swipeAndWaitUrl(p, 300, 75, BASE + 'team.html');
      await swipeAndWaitUrl(p, 300, 75, BASE + 'research.html');
      await assertCleanPage(p, 'research after rapid swipes');
    });

    // 5. Gesture cancel mid-swipe: locked drag + touchcancel stays on page.
    await check('touchcancel after locked drag stays on page', async () => {
      await p.goto(BASE + 'about.html');
      await dispatchTouch(p, 'touchstart', [{ x: 300, y: 320 }], [{ x: 300, y: 320 }]);
      for (const x of [250, 200, 150]) {
        await dispatchTouch(p, 'touchmove', [{ x, y: 320 }], [{ x, y: 320 }]);
        await sleep(30);
      }
      await sleep(300);
      await dispatchTouch(p, 'touchcancel', [], [{ x: 150, y: 320 }]);
      await sleep(700);
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/about.html');
      await assertCleanPage(p, 'about after touchcancel');
    });

    // 6. Short slow swipe (30px, ~600ms) is below commit thresholds: no nav.
    await check('short slow swipe settles back, no navigation', async () => {
      await p.goto(BASE + 'about.html');
      await swipe(p, 300, 270, 320, { stepMs: 120, holdMs: 0 });
      await sleep(700);
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/about.html');
      await assertCleanPage(p, 'about after short swipe');
    });

    // 7. Edge guard: swipe starting in the 32px edge zones must not navigate
    // (reserved for the iOS system back gesture).
    await check('edge-guard left start x=10 does not navigate', async () => {
      await p.goto(BASE + 'about.html');
      await swipe(p, 10, 200, 320, { holdMs: 100 });
      await sleep(600);
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/about.html');
      await assertCleanPage(p, 'about after left-edge swipe');
    });
    await check('edge-guard right start x=380 does not navigate', async () => {
      await swipe(p, 380, 200, 320, { holdMs: 100 });
      await sleep(600);
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/about.html');
      await assertCleanPage(p, 'about after right-edge swipe');
    });

    // 8. Mostly-vertical gesture must not trigger a page swipe.
    await check('vertical gesture does not navigate', async () => {
      await p.goto(BASE + 'about.html');
      await dispatchTouch(p, 'touchstart', [{ x: 200, y: 300 }], [{ x: 200, y: 300 }]);
      for (const y of [350, 420, 500]) {
        await dispatchTouch(p, 'touchmove', [{ x: 205, y }], [{ x: 205, y }]);
        await sleep(30);
      }
      await dispatchTouch(p, 'touchend', [], [{ x: 205, y: 500 }]);
      await sleep(600);
      assert.equal(await p.evaluate(() => location.pathname), '/pai-web/about.html');
      await assertCleanPage(p, 'about after vertical gesture');
    });

    // 9. Outside-click closes the mobile menu (tap on plain main content).
    await check('outside-click closes mobile menu', async () => {
      await p.goto(BASE + 'index.html');
      const menu = p.locator('.menu-btn');
      await menu.click();
      assert.equal(await menu.getAttribute('aria-expanded'), 'true');
      assert.equal(await p.locator('.mobile-menu.open').count(), 1);
      const point = await p.evaluate(() => {
        for (const y of [600, 700, 500, 800]) {
          const el = document.elementFromPoint(195, y);
          if (el && !el.closest('a,button,.site-header,.mobile-menu')) return { x: 195, y };
        }
        return null;
      });
      assert.ok(point, 'no plain main-content tap point found');
      await p.mouse.click(point.x, point.y);
      await sleep(200);
      assert.equal(await menu.getAttribute('aria-expanded'), 'false');
      assert.equal(await p.locator('.mobile-menu.open').count(), 0);
    });

    // 10. Back/Forward restores saved scroll positions (SPA history state).
    await check('back/forward restores scroll position', async () => {
      await p.goto(BASE + 'about.html');
      await p.evaluate(() => window.scrollTo(0, 600));
      await sleep(400);
      // Direct DOM click (not locator.click): Playwright's click scrolls the
      // footer link into view first, which would overwrite the saved 600px
      // scroll position before the navigation handler reads it. This matches
      // verify_navigation.cjs's linkTo helper.
      await p
        .locator('.site-footer a[href="research.html"]')
        .first()
        .evaluate((a) => a.click());
      await p.waitForURL(BASE + 'research.html');
      // Let the SPA transition finish its own scroll restoration (outgoing
      // 105ms + incoming 175ms + rAF) before scrolling, or it clobbers the
      // test's scrollTo back to the destination's restored position.
      await sleep(700);
      await p.evaluate(() => window.scrollTo(0, 350));
      await sleep(400);
      await p.goBack();
      await p.waitForURL(BASE + 'about.html');
      await waitScrollY(p, 600);
      await waitSettled(p);
      await p.goForward();
      await p.waitForURL(BASE + 'research.html');
      await waitScrollY(p, 350);
      await waitSettled(p);
    });

    // 11. Desktop viewport: the same touch handler path still works at 1280px.
    await check('desktop 1280 swipe left about -> team', async () => {
      const ctx2 = await browser.newContext({
        viewport: { width: 1280, height: 844 },
        locale: 'zh-CN',
      });
      await ctx2.route(BASE + '**', (route) => {
        const u = new URL(route.request().url());
        let name = decodeURIComponent(u.pathname.slice('/pai-web/'.length));
        if (!name || name.endsWith('/')) name += 'index.html';
        const file = path.resolve(ROOT, name);
        if (!file.startsWith(ROOT + path.sep) || !fs.existsSync(file)) {
          return route.fulfill({ status: 404, body: name });
        }
        const ext = path.extname(file).toLowerCase();
        const mime = {
          '.html': 'text/html',
          '.js': 'application/javascript',
          '.css': 'text/css',
          '.json': 'application/json',
          '.jpg': 'image/jpeg',
          '.png': 'image/png',
          '.svg': 'image/svg+xml',
          '.webp': 'image/webp',
        }[ext] || 'application/octet-stream';
        return route.fulfill({ status: 200, body: fs.readFileSync(file), contentType: mime });
      });
      const p2 = await ctx2.newPage();
      p2.on('pageerror', (e) => errs.push(`desktop: ${e.message}`));
      await p2.goto(BASE + 'about.html');
      await swipe(p2, 900, 500, 400, { holdMs: 350 });
      await p2.waitForURL(BASE + 'team.html', { timeout: 8000 });
      await sleep(700);
      await assertCleanPage(p2, 'desktop team after swipe left');
      await ctx2.close();
    });

    await check('no JS page errors during swipe run', async () => {
      assert.deepEqual(errs, []);
    });

    await ctx.close();
  } finally {
    await browser.close();
  }
  const passed = results.filter((r) => r.startsWith('PASS')).length;
  console.log(`WEBKIT SWIPE SUMMARY: ${passed} passed, ${failures} failed (engine=${process.env.PAI_BROWSER || 'chromium'})`);
  if (failures > 0) {
    console.log(results.filter((r) => r.startsWith('FAIL')).join('\n'));
    process.exitCode = 1;
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
