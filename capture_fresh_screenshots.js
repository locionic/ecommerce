const { chromium } = require('playwright-core');
const path = require('path');

async function capture() {
  const assetsDir = '/home/renovibe79/ecommerce/fiverr-gig-assets';

  const browser = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage({ viewport: { width: 1280, height: 769 } });

  console.log('Navigating to ishop home...');
  await page.goto('https://ishop.locionic.com/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Dismiss modal if present
  try {
    const modalBtn = page.locator('button:has-text("I Understand"), button:has-text("Accept"), .modal-close').first();
    if (await modalBtn.isVisible({ timeout: 1500 })) {
      await modalBtn.click();
      await page.waitForTimeout(500);
    }
  } catch (e) {}

  // 1. Capture Storefront
  await page.screenshot({ path: path.join(assetsDir, 'fiverr_gallery_2_storefront.png') });
  console.log('Saved fiverr_gallery_2_storefront.png');

  // 2. Navigate to a product
  const productLink = page.locator('a:has-text("View Details")').first();
  await productLink.click();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  // Capture Product Detail
  await page.screenshot({ path: path.join(assetsDir, 'fiverr_gallery_3_product_detail.png') });
  console.log('Saved fiverr_gallery_3_product_detail.png');

  // 3. Add to cart
  const addBtn = page.locator('button:has-text("Add to Cart")').first();
  await addBtn.click();
  await page.waitForTimeout(1000);

  // Navigate to Cart
  const cartBtn = page.locator('a:has-text("Cart")').first();
  await cartBtn.click();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  // Capture Cart
  await page.screenshot({ path: path.join(assetsDir, 'fiverr_gallery_4_cart.png') });
  console.log('Saved fiverr_gallery_4_cart.png');

  await browser.close();
}

capture().catch(console.error);
