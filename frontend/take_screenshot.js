const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://localhost:8080', { waitUntil: 'networkidle2' });
  
  // Wait a moment for images to load
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Scroll down to products
  await page.evaluate(() => {
    window.scrollBy(0, 800);
  });
  
  // Wait a bit after scrolling
  await new Promise(resolve => setTimeout(resolve, 500));
  
  await page.screenshot({ path: 'screenshot_products.png' });
  await browser.close();
})();
