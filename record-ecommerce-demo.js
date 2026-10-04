const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

async function injectCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-cursor')) return;
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    cursor.innerHTML = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 3L19 12L12 13L9 20L5 3Z" fill="#10b981" stroke="#0f172a" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>`;
    cursor.style.cssText = `
      position: fixed; z-index: 9999999; pointer-events: none;
      width: 28px; height: 28px;
      transition: left 0.08s ease-out, top 0.08s ease-out;
      filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));
    `;
    cursor.style.left = '100px';
    cursor.style.top = '100px';
    document.body.appendChild(cursor);
    document.addEventListener('mousemove', (e) => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
    });
  });
}

async function smoothScroll(page, distance, steps = 25, delay = 45) {
  const stepDist = distance / steps;
  for (let i = 0; i < steps; i++) {
    await page.evaluate((d) => window.scrollBy(0, d), stepDist);
    await page.waitForTimeout(delay);
  }
}

async function moveMouseTo(page, x, y, steps = 15) {
  await page.mouse.move(x, y, { steps });
  await page.waitForTimeout(200);
}

async function run() {
  const videoDir = '/home/renovibe79/ecommerce/ecommerce-video-raw';
  if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });

  const browser = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--disable-gpu'
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: videoDir, size: { width: 1280, height: 720 } }
  });

  const page = await context.newPage();

  console.log('1. Loading live store at ishop.locionic.com...');
  await page.goto('https://ishop.locionic.com/', { waitUntil: 'networkidle', timeout: 30000 });
  await injectCursor(page);
  await moveMouseTo(page, 640, 360, 20);
  await page.waitForTimeout(1000);

  // Dismiss disclaimer modal cleanly
  try {
    const modalBtn = page.locator('button:has-text("I Understand"), button:has-text("Accept"), .modal-close').first();
    if (await modalBtn.isVisible({ timeout: 2000 })) {
      const box = await modalBtn.boundingBox();
      if (box) await moveMouseTo(page, box.x + box.width / 2, box.y + box.height / 2, 15);
      await modalBtn.click();
      await page.waitForTimeout(800);
    }
  } catch (e) {
    console.log('Modal note:', e.message);
  }

  console.log('2. Scrolling through live product catalog...');
  await smoothScroll(page, 550, 25, 45);
  await page.waitForTimeout(1200);

  console.log('3. Selecting product to view details...');
  try {
    const detailsBtn = page.locator('a:has-text("View Details")').first();
    if (await detailsBtn.isVisible({ timeout: 2000 })) {
      const box = await detailsBtn.boundingBox();
      if (box) await moveMouseTo(page, box.x + box.width / 2, box.y + box.height / 2, 15);
      await detailsBtn.click();
      await page.waitForLoadState('networkidle');
      await injectCursor(page);
      await page.waitForTimeout(1200);

      console.log('4. Exploring product gallery & adding to cart...');
      await smoothScroll(page, 350, 15, 40);
      await page.waitForTimeout(800);

      const addBtn = page.locator('button:has-text("Add to Cart")').first();
      if (await addBtn.isVisible({ timeout: 2000 })) {
        const bBox = await addBtn.boundingBox();
        if (bBox) await moveMouseTo(page, bBox.x + bBox.width / 2, bBox.y + bBox.height / 2, 15);
        await addBtn.click();
        await page.waitForTimeout(1200);
      }
    }
  } catch (e) {
    console.log('Product flow note:', e.message);
  }

  console.log('5. Navigating to shopping cart...');
  try {
    const cartBtn = page.locator('a:has-text("Cart")').first();
    if (await cartBtn.isVisible({ timeout: 2000 })) {
      const cBox = await cartBtn.boundingBox();
      if (cBox) await moveMouseTo(page, cBox.x + cBox.width / 2, cBox.y + cBox.height / 2, 15);
      await cartBtn.click();
      await page.waitForLoadState('networkidle');
      await injectCursor(page);
      await page.waitForTimeout(1200);

      console.log('6. Reviewing cart items...');
      await smoothScroll(page, 300, 15, 40);
      await page.waitForTimeout(1000);

      console.log('7. Proceeding to checkout...');
      const checkoutBtn = page.locator('a[href*="checkout"], a:has-text("Proceed to checkout"), button:has-text("Checkout")').first();
      if (await checkoutBtn.isVisible({ timeout: 2000 })) {
        const chBox = await checkoutBtn.boundingBox();
        if (chBox) await moveMouseTo(page, chBox.x + chBox.width / 2, chBox.y + chBox.height / 2, 15);
        await checkoutBtn.click();
        await page.waitForLoadState('networkidle');
        await injectCursor(page);
        await page.waitForTimeout(1500);

        console.log('8. Viewing secure checkout form...');
        await smoothScroll(page, 450, 20, 45);
        await page.waitForTimeout(2000);
      }
    }
  } catch (e) {
    console.log('Cart flow note:', e.message);
  }

  console.log('Finishing fresh recording...');
  await page.waitForTimeout(1000);

  await page.close();
  await context.close();
  await browser.close();

  const files = fs.readdirSync(videoDir).filter(f => f.endsWith('.webm'));
  if (files.length > 0) {
    console.log('SUCCESS: Fresh live video recorded:', path.join(videoDir, files[files.length - 1]));
  }
}

run().catch(err => {
  console.error('Fatal recording error:', err);
  process.exit(1);
});
