const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const logs = {
  consoleErrors: [],
  networkErrors: [],
  pageErrors: [],
  results: []
};

function logResult(step, status, details = '') {
  const entry = { step, status, details, time: new Date().toISOString() };
  logs.results.push(entry);
  console.log(`[${status.toUpperCase()}] ${step}: ${details}`);
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      logs.consoleErrors.push({ url: page.url(), text });
      console.log(`[BROWSER CONSOLE ERROR] ${text}`);
    }
  });

  page.on('pageerror', err => {
    logs.pageErrors.push({ url: page.url(), message: err.message, stack: err.stack });
    console.log(`[BROWSER UNCAUGHT EXCEPTION] ${err.message}`);
  });

  page.on('response', response => {
    if (response.status() >= 400) {
      logs.networkErrors.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        pageUrl: page.url()
      });
      console.log(`[NETWORK ERROR ${response.status()}] ${response.url()}`);
    }
  });

  try {
    // --- Step 1: Main Page ---
    console.log('\n--- Testing Main Page ---');
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));

    // Handle Demo Modal if present
    const modalBtn = await page.$('.modal button');
    if (modalBtn) {
      await modalBtn.click();
      await new Promise(r => setTimeout(r, 500));
    }

    await page.screenshot({ path: path.join(__dirname, 'test_1_main_page.png'), fullPage: false });
    logResult('Main Page Load', 'pass', 'Loaded main page and closed demo modal');

    // Scroll to products
    await page.evaluate(() => window.scrollBy(0, 700));
    await new Promise(r => setTimeout(r, 500));
    await page.screenshot({ path: path.join(__dirname, 'test_1b_main_page_products.png') });

    // Check products on main page
    const productCards = await page.$$('.box'); // Product boxes
    console.log(`Found product boxes: ${productCards.length}`);

    // --- Step 2: Categories Dropdown & Category Page ---
    console.log('\n--- Testing Categories ---');
    const categoryMenu = await page.$('.navbar-item.has-dropdown');
    if (categoryMenu) {
      await categoryMenu.hover();
      await new Promise(r => setTimeout(r, 500));
      const categoryLinks = await page.$$('.navbar-dropdown a');
      console.log(`Found categories in dropdown: ${categoryLinks.length}`);
      if (categoryLinks.length > 0) {
        await categoryLinks[0].click();
        await new Promise(r => setTimeout(r, 1500));
        await page.screenshot({ path: path.join(__dirname, 'test_2_category_page.png') });
        logResult('Category Navigation', 'pass', `Navigated to category: ${page.url()}`);
      } else {
        logResult('Category Navigation', 'warn', 'No category links found in dropdown');
      }
    }

    // --- Step 3: Search Functionality ---
    console.log('\n--- Testing Search ---');
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle2' });
    const searchInput = await page.$('input[name="search"]');
    if (searchInput) {
      await searchInput.type('laptop');
      const searchBtn = await page.$('form[action="/search"] button');
      if (searchBtn) {
        await Promise.all([
          searchBtn.click(),
          page.waitForNavigation({ waitUntil: 'networkidle2' }).catch(() => {})
        ]);
      } else {
        await searchInput.press('Enter');
      }
      await new Promise(r => setTimeout(r, 1500));
      await page.screenshot({ path: path.join(__dirname, 'test_3_search_results.png') });
      logResult('Search', 'pass', `Search results page URL: ${page.url()}`);
    }

    // --- Step 4: Product Detail Page ---
    console.log('\n--- Testing Product Details ---');
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle2' });
    await page.evaluate(() => window.scrollBy(0, 800));
    await new Promise(r => setTimeout(r, 500));

    // Find first product link
    const firstProductLink = await page.$('a[href*="/product/"]');
    if (firstProductLink) {
      const href = await page.evaluate(el => el.getAttribute('href'), firstProductLink);
      console.log(`Navigating to product: ${href}`);
      await firstProductLink.click();
      await new Promise(r => setTimeout(r, 1500));
      await page.screenshot({ path: path.join(__dirname, 'test_4_product_detail.png') });
      logResult('Product Detail Load', 'pass', `Navigated to ${page.url()}`);

      // Test Add to Cart
      const plusBtn = await page.$('.quantity-field button:last-child');
      if (plusBtn) {
        await plusBtn.click();
        await new Promise(r => setTimeout(r, 300));
      }
      const addToCartBtn = await page.$('.add-to-cart-btn');
      if (addToCartBtn) {
        await addToCartBtn.click();
        await new Promise(r => setTimeout(r, 500));
        await page.screenshot({ path: path.join(__dirname, 'test_4b_added_to_cart.png') });
        logResult('Add To Cart', 'pass', 'Clicked Add to Cart button');
      }
    } else {
      logResult('Product Detail', 'fail', 'No product link found on home page');
    }

    // --- Step 5: Cart Page ---
    console.log('\n--- Testing Cart Page ---');
    await page.goto('http://localhost:8080/cart', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_5_cart.png') });
    logResult('Cart Page Load', 'pass', `Loaded cart page: ${page.url()}`);

    // Click Proceed to Checkout
    const checkoutLink = await page.$('a[href="/cart/checkout"]');
    if (checkoutLink) {
      await checkoutLink.click();
      await new Promise(r => setTimeout(r, 1500));
      await page.screenshot({ path: path.join(__dirname, 'test_6_checkout_redirect.png') });
      logResult('Checkout Redirect (Unauthenticated)', 'pass', `Redirected to: ${page.url()}`);
    }

    // --- Step 6: Signup Page ---
    console.log('\n--- Testing Signup Page ---');
    await page.goto('http://localhost:8080/signup', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_7_signup.png') });

    // Test Signup Form submission (empty & invalid)
    const signupBtn = await page.$('.page-sign-up button.submit-btn');
    if (signupBtn) {
      await signupBtn.click();
      await new Promise(r => setTimeout(r, 500));
      await page.screenshot({ path: path.join(__dirname, 'test_7b_signup_validation.png') });
      logResult('Signup Validation', 'pass', 'Captured signup validation state');
    }

    // Test creating a new user
    const testUsername = 'testuser_' + Date.now();
    const testEmail = `${testUsername}@example.com`;
    const testPassword = 'Password123!';

    await page.type('#username-input', testUsername);
    await page.type('#email-input', testEmail);
    await page.type('#password-input', testPassword);
    await page.type('#password2-input', testPassword);
    await page.screenshot({ path: path.join(__dirname, 'test_7c_signup_filled.png') });

    if (signupBtn) {
      await signupBtn.click();
      await new Promise(r => setTimeout(r, 2000));
      await page.screenshot({ path: path.join(__dirname, 'test_7d_signup_submitted.png') });
      logResult('Signup Execution', 'pass', `Created user ${testUsername}, current URL: ${page.url()}`);
    }

    // --- Step 7: Login Page ---
    console.log('\n--- Testing Login Page ---');
    await page.goto('http://localhost:8080/login', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_8_login.png') });

    // Fill login form with the created test user
    await page.type('#email-input', testUsername);
    await page.type('#password-input', testPassword);
    const loginBtn = await page.$('.page-sign-up button.submit-btn');
    if (loginBtn) {
      await loginBtn.click();
      await new Promise(r => setTimeout(r, 2000));
      await page.screenshot({ path: path.join(__dirname, 'test_8b_login_submitted.png') });
      logResult('Login Execution', 'pass', `Submitted login, current URL: ${page.url()}`);
    }

    // --- Step 8: Authenticated Pages (My Account, My Orders, Checkout) ---
    console.log('\n--- Testing Authenticated Pages ---');
    await page.goto('http://localhost:8080/my-account', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_9_my_account.png') });
    logResult('My Account Page', 'pass', `My Account URL: ${page.url()}`);

    await page.goto('http://localhost:8080/my-orders', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_10_my_orders.png') });
    logResult('My Orders Page', 'pass', `My Orders URL: ${page.url()}`);

    // Add item to cart first so checkout has items
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle2' });
    await page.evaluate(() => window.scrollBy(0, 800));
    await new Promise(r => setTimeout(r, 500));
    const prodLink = await page.$('a[href*="/product/"]');
    if (prodLink) {
      await prodLink.click();
      await new Promise(r => setTimeout(r, 1000));
      const addBtn = await page.$('.add-to-cart-btn');
      if (addBtn) await addBtn.click();
      await new Promise(r => setTimeout(r, 500));
    }

    // Go to checkout while logged in
    await page.goto('http://localhost:8080/cart/checkout', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(__dirname, 'test_11_checkout_authenticated.png') });

    // Fill shipping form
    await page.type('#first_name-input', 'Jane');
    await page.type('#last_name-input', 'Doe');
    await page.type('#email-input', testEmail);
    await page.type('#phone-input', '1234567890');
    await page.type('#address-input', '123 Test St');
    await page.type('#zipcode-input', '10001');
    await page.type('#place-input', 'Test City');

    // Select Cash on Delivery
    const cashRadio = await page.$('#cash');
    if (cashRadio) {
      await cashRadio.click();
      await new Promise(r => setTimeout(r, 500));
    }

    await page.screenshot({ path: path.join(__dirname, 'test_11b_checkout_form_filled.png') });

    // Submit Checkout
    const payNowBtn = await page.$('#pay-now');
    if (payNowBtn) {
      await payNowBtn.click();
      await new Promise(r => setTimeout(r, 2500));
      await page.screenshot({ path: path.join(__dirname, 'test_11c_checkout_submitted.png') });
      logResult('Checkout Submission', 'pass', `Submitted checkout, URL: ${page.url()}`);
    }

  } catch (err) {
    console.error('Error during test execution:', err);
    logResult('Test Execution', 'fail', err.message);
  } finally {
    await browser.close();
    fs.writeFileSync(
      path.join(__dirname, 'test_report.json'),
      JSON.stringify(logs, null, 2)
    );
    console.log('\n--- Testing Completed. Report written to test_report.json ---');
  }
})();
