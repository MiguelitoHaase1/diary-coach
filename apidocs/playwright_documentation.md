# playwright API Documentation

*Fetched using Context7 MCP server on 2025-07-28 10:00:41*

---

========================
CODE SNIPPETS
========================
TITLE: Debug Tests on Specific Browser Project (JS)
DESCRIPTION: Enables debugging tests for a specific browser configuration defined in `playwright.config`. Use the `--project` flag along with `--debug` to target tests on a particular browser or device profile, such as Chromium or Mobile Safari.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_2

LANGUAGE: bash
CODE:
```
npx playwright test --project=chromium --debug
```

LANGUAGE: bash
CODE:
```
npx playwright test --project="Mobile Safari" --debug
```

LANGUAGE: bash
CODE:
```
npx playwright test --project="Microsoft Edge" --debug
```

----------------------------------------

TITLE: Playwright Browser Console API
DESCRIPTION: Provides methods to interact with the browser's developer console within Playwright. These functions allow querying elements using Playwright's selectors, inspecting elements, and generating selectors for existing DOM elements.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_10

LANGUAGE: APIDOC
CODE:
```
playwright.$(selector)
  - Queries the Playwright selector engine for the first matching element.
  - Example: playwright.$('.auth-form >> text=Log in');

playwright.$$(selector)
  - Queries the Playwright selector engine for all matching elements.
  - Example: playwright.$$('li >> text=John')

playwright.inspect(selector)
  - Reveals the specified element in the browser's Elements panel.
  - Example: playwright.inspect('text=Log in')

playwright.locator(selector, options)
  - Creates a Locator object for querying matching elements, supporting options like 'hasText'.
  - Example: playwright.locator('.auth-form', { hasText: 'Log in' });

playwright.selector(element)
  - Generates a Playwright-compatible selector for a given DOM element.
  - Example: playwright.selector($0) // $0 refers to the currently inspected element
```

----------------------------------------

TITLE: Debug Specific Test Line on Specific Browser (JS)
DESCRIPTION: Combines debugging a specific test line with targeting a particular browser project. This command allows precise debugging of a single test case on a chosen browser configuration, identified by the test file, line number, and `--project` flag.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_3

LANGUAGE: bash
CODE:
```
npx playwright test example.spec.ts:10 --project=webkit --debug
```

----------------------------------------

TITLE: Page.click() strict mode
DESCRIPTION: Introduces a 'strict' mode for selectors to ensure that a selector points to a single element. If multiple elements match the selector, an error is thrown. This helps prevent ambiguity in automation testing.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_172

LANGUAGE: js
CODE:
```
// This will throw if you have more than one button!
await page.click('button', { strict: true });
```

----------------------------------------

TITLE: Run Playwright Tests in UI Mode
DESCRIPTION: Launches Playwright tests in interactive UI mode, providing features like a locator picker, watch mode, and step-through debugging. Recommended for enhanced developer experience.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_1

LANGUAGE: bash
CODE:
```
npx playwright test --ui
```

----------------------------------------

TITLE: Pause Test Execution
DESCRIPTION: Demonstrates how to pause test execution at specific points using the `page.pause()` method across various Playwright supported languages. This allows for interactive debugging within the browser's developer tools.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_7

LANGUAGE: js
CODE:
```
await page.pause();
```

LANGUAGE: java
CODE:
```
page.pause();
```

LANGUAGE: python
CODE:
```
await page.pause()
```

LANGUAGE: python
CODE:
```
page.pause()
```

LANGUAGE: csharp
CODE:
```
await page.PauseAsync();
```

----------------------------------------

TITLE: Run Playwright Tests on Specific Browser
DESCRIPTION: Specify the browser engine for test execution using the --browser flag. Supports engines like webkit, firefox, and chromium.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_2

LANGUAGE: bash
CODE:
```
pytest --browser webkit
```

----------------------------------------

TITLE: Run Tests on Different Browsers (Environment Variable)
DESCRIPTION: Specifies the browser to run tests on by setting the BROWSER environment variable. Supported values include 'chromium', 'firefox', and 'webkit'.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-csharp.md#_snippet_2

LANGUAGE: csharp
CODE:
```
BROWSER=webkit dotnet test
```

LANGUAGE: csharp
CODE:
```
set BROWSER=webkit
dotnet test
```

LANGUAGE: csharp
CODE:
```
$env:BROWSER="webkit"
dotnet test
```

----------------------------------------

TITLE: Debug Specific Test Line (JS)
DESCRIPTION: Allows debugging a single test case at a specific line number. By appending the file name and line number to the test command with the `--debug` flag, Playwright focuses debugging efforts on that particular test across configured browsers.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_1

LANGUAGE: bash
CODE:
```
npx playwright test example.spec.ts:10 --debug
```

----------------------------------------

TITLE: Run Tests on Different Browsers (Launch Configuration)
DESCRIPTION: Configures the browser for test execution using command-line arguments or a runsettings file. This method allows for more granular control over browser selection.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-csharp.md#_snippet_3

LANGUAGE: bash
CODE:
```
dotnet test -- Playwright.BrowserName=webkit
```

LANGUAGE: bash
CODE:
```
dotnet test --settings:chromium.runsettings
dotnet test --settings:firefox.runsettings
dotnet test --settings:webkit.runsettings
```

LANGUAGE: xml
CODE:
```
<?xml version="1.0" encoding="utf-8"?>
  <RunSettings>
    <Playwright>
      <BrowserName>chromium</BrowserName>
    </Playwright>
  </RunSettings>
```

----------------------------------------

TITLE: Run Playwright Tests in Debug Mode (JS)
DESCRIPTION: Enables Playwright's debug mode using the `--debug` command-line flag. This automatically configures browsers to launch in headed mode and sets the default timeout to 0 for uninterrupted debugging. It's useful for general debugging sessions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_0

LANGUAGE: bash
CODE:
```
npx playwright test --debug
```

----------------------------------------

TITLE: Start Playwright UI Mode
DESCRIPTION: Initiates Playwright in UI Mode, offering an enhanced debugging experience with features like step-through execution, locator picking, and live editing.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_7

LANGUAGE: bash
CODE:
```
npx playwright test --ui
```

----------------------------------------

TITLE: Debug Playwright Tests with Inspector
DESCRIPTION: Enable the Playwright Inspector for debugging by setting the PWDEBUG=1 environment variable. This opens a browser window and the inspector to step through API calls and inspect locators.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_8

LANGUAGE: bash
CODE:
```
PWDEBUG=1 pytest -s
```

LANGUAGE: batch
CODE:
```
set PWDEBUG=1
pytest -s
```

LANGUAGE: powershell
CODE:
```
$env:PWDEBUG=1
pytest -s
```

----------------------------------------

TITLE: Verify Labels by Selector
DESCRIPTION: Verifies accessibility labels for elements matching a given CSS selector using AriaUtils. This utility is employed in testing accessibility name computation, specifically for tooltip-related components.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/comp_tooltip.html#_snippet_0

LANGUAGE: JavaScript
CODE:
```
AriaUtils.verifyLabelsBySelector(".ex");
```

----------------------------------------

TITLE: Verify Accessibility Labels by Selector in Playwright
DESCRIPTION: This snippet demonstrates how to use `AriaUtils.verifyLabelsBySelector` to check the accessibility labels of elements matching a specific CSS selector. This is typically used in Playwright tests to ensure that UI components have correct and verifiable ARIA labels for accessibility.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/comp_name_from_content.html#_snippet_5

LANGUAGE: JavaScript
CODE:
```
AriaUtils.verifyLabelsBySelector(".ex");
```

----------------------------------------

TITLE: Verify Labels Using Selector
DESCRIPTION: Verifies accessibility labels for elements matching a given CSS selector using AriaUtils. This function is typically part of a testing framework to automate accessibility checks.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/comp_label.html#_snippet_0

LANGUAGE: javascript
CODE:
```
AriaUtils.verifyLabelsBySelector(".ex");
```

----------------------------------------

TITLE: Enable Debugging with PWDEBUG=console
DESCRIPTION: Instructions on how to enable Playwright's debug mode via the `PWDEBUG=console` environment variable. This makes the `playwright` object available in browser developer tools, aiding in DOM inspection and log analysis.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_8

LANGUAGE: bash
CODE:
```
PWDEBUG=console npx playwright test
```

LANGUAGE: batch
CODE:
```
set PWDEBUG=console
npx playwright test
```

LANGUAGE: powershell
CODE:
```
$env:PWDEBUG="console"
npx playwright test
```

LANGUAGE: bash
CODE:
```
# Source directories in the list are separated by : on macos and linux and by ; on win.
PWDEBUG=console PLAYWRIGHT_JAVA_SRC=<java source dirs> mvn test
```

LANGUAGE: batch
CODE:
```
# Source directories in the list are separated by : on macos and linux and by ; on win.
set PLAYWRIGHT_JAVA_SRC=<java source dirs>
set PWDEBUG=console
mvn test
```

LANGUAGE: powershell
CODE:
```
# Source directories in the list are separated by : on macos and linux and by ; on win.
$env:PLAYWRIGHT_JAVA_SRC="<java source dirs>"
$env:PWDEBUG="console"
mvn test
```

----------------------------------------

TITLE: Playwright Test Example (JS/TS)
DESCRIPTION: Shows how to achieve similar browser automation tasks using Playwright Test. This example highlights Playwright Test's assertion style and test runner integration, requiring `@playwright/test`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/library-js.md#_snippet_1

LANGUAGE: js-ts
CODE:
```
import { expect, test, devices } from '@playwright/test';

test.use(devices['iPhone 11']);

test('should be titled', async ({ page, context }) => {
  await context.route('**.jpg', route => route.abort());
  await page.goto('https://example.com/');

  await expect(page).toHaveTitle('Example');
});
```

LANGUAGE: js-js
CODE:
```
const { expect, test, devices } = require('@playwright/test');

test.use(devices['iPhone 11']);

test('should be titled', async ({ page, context }) => {
  await context.route('**.jpg', route => route.abort());
  await page.goto('https://example.com/');

  await expect(page).toHaveTitle('Example');
});
```

----------------------------------------

TITLE: Configure `headless` mode in Playwright
DESCRIPTION: Determines whether the browser runs in headless mode (no visible UI) or headed mode (with a visible UI). Setting `headless` to `false` is useful for debugging or visual inspection during test execution.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-api/class-testoptions.md#_snippet_8

LANGUAGE: TypeScript
CODE:
```
import {
  defineConfig
} from '@playwright/test';

export default defineConfig({
  use: {
    headless: false
  },
});
```

----------------------------------------

TITLE: Debug Playwright Browser Launches
DESCRIPTION: Use the `DEBUG` environment variable to enable detailed logging for Playwright, specifically for debugging browser launch issues. Setting it to `pw:browser` provides insights into browser process interactions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/ci.md#_snippet_25

LANGUAGE: js
CODE:
```
DEBUG=pw:browser npx playwright test
```

LANGUAGE: python
CODE:
```
DEBUG=pw:browser pytest
```

LANGUAGE: java
CODE:
```
DEBUG=pw:browser mvn test
```

LANGUAGE: csharp
CODE:
```
DEBUG=pw:browser dotnet test
```

----------------------------------------

TITLE: Select Element by ARIA Role and Name in Playwright
DESCRIPTION: Demonstrates using new role selectors to find elements based on their ARIA role, ARIA attributes, and accessible name. This enhances accessibility-focused testing by allowing selection via semantic roles.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_121

LANGUAGE: js
CODE:
```
await page.locator('role=button[name="log in"]').click();
```

----------------------------------------

TITLE: Configure Headless Mode and Slow Motion
DESCRIPTION: Demonstrates how to launch Playwright browsers in headed mode (visible UI) and control execution speed using the `slowMo` option. This is essential for debugging and observing browser interactions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_11

LANGUAGE: js
CODE:
```
await chromium.launch({ headless: false, slowMo: 100 });
```

LANGUAGE: java
CODE:
```
chromium.launch(new BrowserType.LaunchOptions()
  .setHeadless(false)
  .setSlowMo(100));
```

LANGUAGE: python async
CODE:
```
await chromium.launch(headless=False, slow_mo=100)
```

LANGUAGE: python sync
CODE:
```
chromium.launch(headless=False, slow_mo=100)
```

LANGUAGE: csharp
CODE:
```
await using var browser = await playwright.Chromium.LaunchAsync(new()
{
    Headless = false,
    SlowMo = 100
});
```

----------------------------------------

TITLE: Playwright CLI Common Test Options
DESCRIPTION: Details common options for the 'playwright test' command to customize test execution. These options control debugging, browser modes, test filtering, project selection, worker count, and UI mode.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-cli-js.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
Playwright CLI Test Options:

--debug
  Run tests with Playwright Inspector. Shortcut for `PWDEBUG=1` environment variable and `--timeout=0 --max-failures=1 --headed --workers=1` options.

--headed
  Run tests in headed browsers (default: headless).

-g <grep> or --grep <grep>
  Only run tests matching this regular expression (default: ".*").

--project <project-name...>
  Only run tests from the specified list of projects, supports '*' wildcard (default: run all projects).

--ui
  Run tests in interactive UI mode.

-j <workers> or --workers <workers>
  Number of concurrent workers or percentage of logical CPU cores, use 1 to run in a single worker (default: 50%).
```

----------------------------------------

TITLE: Playwright Locators: Text, Role, Label, TestId, Placeholder, AltText, Title (JS)
DESCRIPTION: Demonstrates using various Playwright locator methods to find elements by text content, ARIA role, associated label, data-testid attribute, placeholder text, alt text, and title attribute. These methods simplify element selection in automated tests.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_93

LANGUAGE: js
CODE:
```
await page.getByLabel('User Name').fill('John');

await page.getByLabel('Password').fill('secret-password');

await page.getByRole('button', { name: 'Sign in' }).click();

await expect(page.getByText('Welcome, John!')).toBeVisible();
```

----------------------------------------

TITLE: Run Playwright Tests on Multiple Browsers
DESCRIPTION: Execute tests concurrently across multiple specified browsers by repeating the --browser flag.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_3

LANGUAGE: bash
CODE:
```
pytest --browser webkit --browser firefox
```

----------------------------------------

TITLE: Conditionally Skip Playwright Test Group for Specific Browser
DESCRIPTION: Shows how to use `test.skip()` within a `test.describe` block to conditionally skip all tests and hooks within that group. This example skips the entire group if the current browser is not Chromium, ensuring tests run only in the intended environment.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-annotations-js.md#_snippet_11

LANGUAGE: javascript
CODE:
```
test.describe('chromium only', () => {
  test.skip(({ browserName }) => browserName !== 'chromium', 'Chromium only!');

  test.beforeAll(async () => {
    // This hook is only run in Chromium.
  });

  test('test 1', async ({ page }) => {
    // This test is only run in Chromium.
  });

  test('test 2', async ({ page }) => {
    // This test is only run in Chromium.
  });
});
```

----------------------------------------

TITLE: Element Queries: Test ID
DESCRIPTION: Shows how to locate elements using a `data-testid` attribute.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/testing-library-js.md#_snippet_8

LANGUAGE: javascript
CODE:
```
screen.getByTestId('...');
```

LANGUAGE: javascript
CODE:
```
component.getByTestId('...');
```

----------------------------------------

TITLE: Element Queries: Role
DESCRIPTION: Illustrates querying elements by their ARIA role. Both libraries support this, with similar syntax for options.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/testing-library-js.md#_snippet_4

LANGUAGE: javascript
CODE:
```
screen.getByRole('button', { pressed: true });
```

LANGUAGE: javascript
CODE:
```
component.getByRole('button', { pressed: true });
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Values
DESCRIPTION: Checks if a select element has the specified options selected. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_26

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveValues()
```

----------------------------------------

TITLE: Run Playwright Tests in Headed Mode
DESCRIPTION: Run Playwright tests with a visible browser window. This flag opens a browser instance during test execution.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_1

LANGUAGE: bash
CODE:
```
pytest --headed
```

----------------------------------------

TITLE: Set Breakpoint with page.pause()
DESCRIPTION: Allows pausing test execution at a specific point by inserting the `page.pause()` method into the test script. When the inspector is active, clicking 'Resume' will run the test until this method is encountered, enabling focused debugging of subsequent actions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_6

LANGUAGE: js
CODE:
```
await page.pause();
```

LANGUAGE: java
CODE:
```
page.pause();
```

LANGUAGE: python async
CODE:
```
await page.pause()
```

LANGUAGE: python sync
CODE:
```
page.pause()
```

LANGUAGE: csharp
CODE:
```
await page.PauseAsync();
```

----------------------------------------

TITLE: Filter Visible Elements with Locator.filter
DESCRIPTION: Introduces the `visible: true` option for `Locator.filter`, allowing users to match only elements that are currently visible in the DOM. This is useful for scenarios where invisible elements should be ignored during testing.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_11

LANGUAGE: ts
CODE:
```
test('some test', async ({ page }) => {
  // Ignore invisible todo items.
  const todoItems = page.getByTestId('todo-item').filter({ visible: true });
  // Check there are exactly 3 visible ones.
  await expect(todoItems).toHaveCount(3);
});
```

----------------------------------------

TITLE: Playwright Locators and Web-First Assertions
DESCRIPTION: Documentation for Playwright's recommended approach to element interaction and verification using Locators and web-first Assertions, providing more reliable and readable test code compared to direct DOM evaluation methods like `page.$eval()`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/puppeteer-js.md#_snippet_6

LANGUAGE: APIDOC
CODE:
```
class Locator
  - Purpose: Represents a way to find element(s) on the page at any moment. Locators are auto-waiting and retry-able.
  - Creation: `page.locator(selector, options)`
    - `selector`: (string) A CSS or XPath selector, or a text/role/label selector.
    - `options`: (object, optional) Options like `hasText`, `has` for further filtering.
  - Example: `const titleLocator = page.locator('.hero__title');`

class expect (Assertions)
  - Purpose: Provides web-first assertions for verifying the state of elements and pages, automatically waiting for conditions to be met.
  - Methods:
    - `expect(locator).toContainText(text)`
      - Purpose: Asserts that the element represented by the locator contains the specified text.
      - Parameters:
        - `locator`: (Locator) The locator to assert against.
        - `text`: (string | RegExp | Array<string | RegExp>) The expected text content.
      - Example: `await expect(titleLocator).toContainText('Playwright enables reliable end-to-end testing');`
    - Other common assertions (not explicitly detailed in text but implied by 'several matchers'): `toBeVisible()`, `toHaveText()`, `toHaveAttribute()`, `toHaveClass()`, etc.

Comparison with Puppeteer's `page.$eval()` / `page.evaluate()`:
  - `page.$eval(selector, pageFunction, ...args)`: Executes `pageFunction` in the browser context on the element matched by `selector`.
  - `page.evaluate(pageFunction, ...args)`: Executes `pageFunction` in the browser context.
  - Playwright's Locators and Assertions are preferred as they are more reliable, readable, and automatically handle waiting for elements and conditions, reducing flakiness.
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Attribute
DESCRIPTION: Checks if the element has a specific DOM attribute with an optional value. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_16

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveAttribute()
```

----------------------------------------

TITLE: Debug Custom Browser Builds
DESCRIPTION: Enable detailed debugging output for Playwright's browser interactions by setting the DEBUG environment variable. This is useful for diagnosing issues with custom browser builds.

SOURCE: https://github.com/microsoft/playwright/blob/main/CONTRIBUTING.md#_snippet_9

LANGUAGE: bash
CODE:
```
DEBUG=pw:browser
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Role
DESCRIPTION: Checks if the element has a specific ARIA role. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_22

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveRole()
```

----------------------------------------

TITLE: Playwright Import from @playwright/test
DESCRIPTION: Highlights a breaking change where `npx playwright test` may not work if both `playwright` and `@playwright/test` are installed. It shows the recommended way to import browser automation APIs directly from `@playwright/test`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_74

LANGUAGE: ts
CODE:
```
import { chromium, firefox, webkit } from '@playwright/test';
/* ... */
```

----------------------------------------

TITLE: Run Playwright Tests on Specific Browsers
DESCRIPTION: Specifies which browser(s) to run tests on using the --project flag. Multiple --project flags can be used to run on several browsers simultaneously.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_3

LANGUAGE: bash
CODE:
```
npx playwright test --project webkit
npx playwright test --project webkit --project firefox
```

----------------------------------------

TITLE: Scan Specific Page Elements for Accessibility Violations (Java)
DESCRIPTION: This example shows how to configure axe-core to scan only specific parts of a web page for accessibility violations within Playwright tests. It uses `AxeBuilder.include()` to target elements by CSS selector. Ensure you `waitFor()` the page state before analyzing for accurate results.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/accessibility-testing-java.md#_snippet_1

LANGUAGE: java
CODE:
```
import com.deque.html.axecore.playwright.*;
import com.deque.html.axecore.utilities.axeresults.*;

import org.junit.jupiter.api.*;
import com.microsoft.playwright.*;

import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.Collections;

public class HomepageTests {
  // Assuming 'page' is initialized elsewhere, e.g., in a @BeforeEach method
  Page page;

  @Test
  void navigationMenuFlyoutShouldNotHaveAutomaticallyDetectableAccessibilityViolations() throws Exception {
    page.navigate("https://your-site.com/");

    page.locator("button[aria-label=\"Navigation Menu\"]").click();

    // It is important to waitFor() the page to be in the desired
    // state *before* running analyze(). Otherwise, axe might not
    // find all the elements your test expects it to scan.
    page.locator("#navigation-menu-flyout").waitFor();

    AxeResults accessibilityScanResults = new AxeBuilder(page)
      .include(Arrays.asList("#navigation-menu-flyout"))
      .analyze();

    assertEquals(Collections.emptyList(), accessibilityScanResults.getViolations());
  }
}
```

----------------------------------------

TITLE: UI Test: Create Issue via UI and Validate via API
DESCRIPTION: This test demonstrates creating a GitHub issue through the browser UI and then verifying its existence and details by making an API call using Playwright's request context. It highlights the integration of UI and API testing.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api-testing-js.md#_snippet_8

LANGUAGE: js
CODE:
```
import { test, expect } from '@playwright/test';

const REPO = 'test-repo-1';
const USER = 'github-username';

// Request context is reused by all tests in the file.
let apiContext;

test.beforeAll(async ({ playwright }) => {
  apiContext = await playwright.request.newContext({
    // All requests we send go to this API endpoint.
    baseURL: 'https://api.github.com',
    extraHTTPHeaders: {
      // We set this header per GitHub guidelines.
      'Accept': 'application/vnd.github.v3+json',
      // Add authorization token to all requests.
      // Assuming personal access token available in the environment.
      'Authorization': `token ${process.env.API_TOKEN}`,
    },
  });
});

test.afterAll(async ({ }) => {
  // Dispose all responses.
  await apiContext.dispose();
});

test('last created issue should be on the server', async ({ page }) => {
  await page.goto(`https://github.com/${USER}/${REPO}/issues`);
  await page.getByText('New Issue').click();
  await page.getByRole('textbox', { name: 'Title' }).fill('Bug report 1');
  await page.getByRole('textbox', { name: 'Comment body' }).fill('Bug description');
  await page.getByText('Submit new issue').click();
  const issueId = new URL(page.url()).pathname.split('/').pop();

  const newIssue = await apiContext.get(
      `https://api.github.com/repos/${USER}/${REPO}/issues/${issueId}`
  );
  expect(newIssue.ok()).toBeTruthy();
  expect(newIssue.json()).toEqual(expect.objectContaining({
    title: 'Bug report 1'
  }));
});
```

----------------------------------------

TITLE: Locate by CSS or XPath
DESCRIPTION: Use `page.locator` with CSS or XPath selectors to find elements. Playwright auto-detects selector types if prefixes like `css=` or `xpath=` are omitted. While flexible, relying on complex or deeply nested selectors can lead to brittle tests.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/locators.md#_snippet_13

LANGUAGE: js
CODE:
```
await page.locator('css=button').click();
await page.locator('xpath=//button').click();

await page.locator('button').click();
await page.locator('//button').click();
```

LANGUAGE: java
CODE:
```
page.locator("css=button").click();
page.locator("xpath=//button").click();

page.locator("button").click();
page.locator("//button").click();
```

LANGUAGE: python async
CODE:
```
await page.locator("css=button").click()
await page.locator("xpath=//button").click()

await page.locator("button").click()
await page.locator("//button").click()
```

LANGUAGE: python sync
CODE:
```
page.locator("css=button").click()
page.locator("xpath=//button").click()

page.locator("button").click()
page.locator("//button").click()
```

LANGUAGE: csharp
CODE:
```
await Page.Locator("css=button").ClickAsync();
await Page.Locator("xpath=//button").ClickAsync();

await Page.Locator("button").ClickAsync();
await Page.Locator("//button").ClickAsync();
```

----------------------------------------

TITLE: Playwright Test: Isolated Browser Context
DESCRIPTION: Demonstrates how Playwright's test runner automatically provides isolated browser contexts for each test, ensuring clean-slate environments. It shows accessing the `page` and `context` objects within a test function, highlighting their independence from other tests.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browser-contexts.md#_snippet_0

LANGUAGE: js
CODE:
```
import { test } from '@playwright/test';

test('example test', async ({ page, context }) => {
  // "context" is an isolated BrowserContext, created for this specific test.
  // "page" belongs to this context.
});

test('another test', async ({ page, context }) => {
  // "context" and "page" in this second test are completely
  // isolated from the first test.
});
```

----------------------------------------

TITLE: Run Test on a Specific Browser
DESCRIPTION: Demonstrates how to run a test exclusively on a specified browser using the `pytest.mark.only_browser` decorator. This helps in targeted testing or debugging.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-runners-python.md#_snippet_10

LANGUAGE: python
CODE:
```
import pytest

@pytest.mark.only_browser("chromium")
def test_visit_example(page):
    page.goto("https://example.com")
    # ...

```

----------------------------------------

TITLE: Playwright: Expect Locator to be Enabled
DESCRIPTION: Checks if the element is enabled. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_7

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeEnabled()
```

----------------------------------------

TITLE: Run Playwright Tests in Headed Mode
DESCRIPTION: Executes Playwright tests with browser windows visible, allowing visual inspection of test execution. Use this flag to see the browser interact with the website.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_2

LANGUAGE: bash
CODE:
```
npx playwright test --headed
```

----------------------------------------

TITLE: Locate Element by Test ID (Default Attribute)
DESCRIPTION: Demonstrates how to locate elements using the `getByTestId` method with the default `data-testid` attribute. This is a resilient testing strategy. It shows examples in JavaScript, Java, Python, and C#.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/locators.md#_snippet_10

LANGUAGE: javascript
CODE:
```
await page.getByTestId('directions').click();
```

LANGUAGE: java
CODE:
```
page.getByTestId("directions").click();
```

LANGUAGE: python async
CODE:
```
await page.get_by_test_id("directions").click()
```

LANGUAGE: python sync
CODE:
```
page.get_by_test_id("directions").click()
```

LANGUAGE: csharp
CODE:
```
await Page.GetByTestId("directions").ClickAsync();
```

----------------------------------------

TITLE: Open Playwright UI Mode
DESCRIPTION: This command launches Playwright's interactive UI Mode, enabling exploration, running, and debugging of tests with time travel capabilities. It allows for individual test execution and detailed inspection of test steps.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-ui-mode-js.md#_snippet_0

LANGUAGE: bash
CODE:
```
npx playwright test --ui
```

----------------------------------------

TITLE: Run Playwright Tests in Debug Mode
DESCRIPTION: Execute Playwright tests with the `--debug` flag to enable interactive debugging. This allows you to pause test execution, inspect elements, and step through your code. It's compatible with various package managers like npm, yarn, and pnpm.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/best-practices-js.md#_snippet_7

LANGUAGE: npm
CODE:
```
npx playwright test --debug
```

LANGUAGE: yarn
CODE:
```
yarn playwright test --debug
```

LANGUAGE: pnpm
CODE:
```
pnpm exec playwright test --debug
```

----------------------------------------

TITLE: Element Queries: Text Content
DESCRIPTION: Examples of finding elements based on their visible text content.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/testing-library-js.md#_snippet_7

LANGUAGE: javascript
CODE:
```
screen.findByText('...');
```

LANGUAGE: javascript
CODE:
```
component.getByText('...');
```

----------------------------------------

TITLE: Log Current URL in Browser
DESCRIPTION: This JavaScript code logs the current page's URL (href) to the browser's developer console. It's commonly used for debugging or inspecting the current page state within automated testing frameworks like Playwright.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/consolelog.html#_snippet_0

LANGUAGE: javascript
CODE:
```
console.log('here:' + location.href)
```

----------------------------------------

TITLE: Click Button by Role and Name (C#)
DESCRIPTION: Demonstrates using role selectors to find elements by ARIA role and accessible name. This allows for more robust element selection based on accessibility attributes.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-csharp.md#_snippet_75

LANGUAGE: csharp
CODE:
```
await page.Locator("role=button[name='log in']").ClickAsync();
```

----------------------------------------

TITLE: Playwright: Verify Labels with AriaUtils
DESCRIPTION: Utilizes AriaUtils to verify labels by a given CSS selector. This is part of accessibility testing workflows in Playwright.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/shadowdom/slot.html#_snippet_1

LANGUAGE: javascript
CODE:
```
AriaUtils.verifyLabelsBySelector('.labelled');
```

----------------------------------------

TITLE: Run Playwright Tests
DESCRIPTION: Execute all Playwright tests using pytest. By default, tests run in headless mode on the Chromium browser.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_0

LANGUAGE: bash
CODE:
```
pytest
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have CSS
DESCRIPTION: Checks if the element has a specific CSS property with an optional value. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_19

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveCSS()
```

----------------------------------------

TITLE: Enable Playwright UI Mode
DESCRIPTION: Launches Playwright's new UI Mode for exploring, running, and debugging tests. This mode provides an interactive interface for test development and is activated using the `--ui` flag.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_79

LANGUAGE: sh
CODE:
```
npx playwright test --ui
```

----------------------------------------

TITLE: Run All Playwright Tests (CLI)
DESCRIPTION: Executes all Playwright tests across configured browsers in headless mode. This is the default command for initiating a test run.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_0

LANGUAGE: bash
CODE:
```
npx playwright test
```

----------------------------------------

TITLE: Role Selectors
DESCRIPTION: Enables selecting elements by their ARIA role, ARIA attributes, and accessible name. This provides a more robust and accessible way to locate elements.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-java.md#_snippet_71

LANGUAGE: java
CODE:
```
// Click a button with accessible name "log in"
page.locator("role=button[name='log in']").click();
```

----------------------------------------

TITLE: Locator.click Method Example
DESCRIPTION: Illustrates a scenario where Playwright clicks a 'Sign Up' button. The example highlights how the button's state (disabled then enabled) affects the interaction, demonstrating Playwright's ability to handle dynamic element states during actions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/actionability.md#_snippet_2

LANGUAGE: APIDOC
CODE:
```
method: Locator.click

Description:
  Performs a click action on the locator.

Example Scenario:
  Consider a scenario where Playwright will click `Sign Up` button regardless of when the [`method: Locator.click`] call was made:
  - page is checking that user name is unique and `Sign Up` button is disabled;
  - after checking with the server, the disabled `Sign Up` button is replaced with another one that is now enabled.

Related Concepts:
  - [Enabled]: Element is considered enabled when it is not disabled.
  - [Receives Events]: Element is considered receiving pointer events when it is the hit target of the pointer event at the action point.
```

----------------------------------------

TITLE: Launch Browser with Options (C#)
DESCRIPTION: Shows how to launch a browser with specific options, such as disabling headless mode to view the browser UI and enabling slow motion for debugging. These options help in observing and debugging Playwright execution.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/library-csharp.md#_snippet_2

LANGUAGE: csharp
CODE:
```
await using var browser = await playwright.Firefox.LaunchAsync(new()
{
    Headless = false,
    SlowMo = 50,
});
```

----------------------------------------

TITLE: Playwright Test Fixtures and Hooks
DESCRIPTION: Documentation for Playwright Test's built-in fixtures, specifically the `page` object, and test lifecycle hooks like `test.beforeAll` and `test.afterAll` for managing browser contexts and pages across tests.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/puppeteer-js.md#_snippet_5

LANGUAGE: APIDOC
CODE:
```
test(name, async ({ page }) => { ... })
  - Purpose: Defines a test case. The `page` object is a built-in fixture providing an isolated Page object for each test.
  - Parameters:
    - `name`: (string) The name of the test.
    - `page`: (Page) An isolated Page object provided by Playwright Test for interacting with the browser.
  - Usage: `test('my test', async ({ page }) => { await page.goto('...'); });`

test.beforeAll(async () => { ... })
  - Purpose: Runs code once before all tests in the current describe block or file.
  - Note: Can be used to reuse a single Page object or browser context between multiple tests, for example, by creating it here and closing in `afterAll`.
  - Usage: `test.beforeAll(async () => { browser = await puppeteer.launch(); page = await browser.newPage(); });`

test.afterAll(async () => { ... })
  - Purpose: Runs code once after all tests in the current describe block or file.
  - Note: Typically used to close resources opened in `beforeAll`.
  - Usage: `test.afterAll(() => browser.close());`
```

----------------------------------------

TITLE: Playwright nth and visible Selectors
DESCRIPTION: New selector engines: 'nth' for matching elements by index (e.g., `nth=0` for the first element) and 'visible' for matching only visible elements.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-csharp.md#_snippet_88

LANGUAGE: csharp
CODE:
```
// select the first button among all buttons
await button.ClickAsync("button >> nth=0");
// or if you are using locators, you can use First, Nth() and Last
await page.Locator("button").First.ClickAsync();

// click a visible button
await button.ClickAsync("button >> visible=true");
```

----------------------------------------

TITLE: Verify ARIA Labels by Selector
DESCRIPTION: Utility function to verify ARIA labels for elements matching a given CSS selector. This function is part of the testing suite for ARIA name computation.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/comp_labelledby.html#_snippet_0

LANGUAGE: javascript
CODE:
```
AriaUtils.verifyLabelsBySelector(".ex");
```

----------------------------------------

TITLE: Run Playwright Tests in Debug Mode (Environment Variable)
DESCRIPTION: Enables Playwright's debug mode by setting the `PWDEBUG` environment variable to `1`. This method is cross-platform and configures Playwright for debugging, launching browsers in headed mode and disabling default timeouts. It's commonly used with test runners like pytest.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_snippet_4

LANGUAGE: python
CODE:
```
PWDEBUG=1 pytest -s
```

LANGUAGE: python
CODE:
```
set PWDEBUG=1
pytest -s
```

LANGUAGE: python
CODE:
```
$env:PWDEBUG=1
pytest -s
```

LANGUAGE: csharp
CODE:
```
PWDEBUG=1 dotnet test
```

LANGUAGE: csharp
CODE:
```
set PWDEBUG=1
dotnet test
```

LANGUAGE: csharp
CODE:
```
$env:PWDEBUG=1
dotnet test
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Value
DESCRIPTION: Checks if an input or select element has the specified value. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_25

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveValue()
```

----------------------------------------

TITLE: Run Tests in Headed Mode
DESCRIPTION: Runs tests with a visible browser window, allowing you to observe the test execution. This is achieved by setting the HEADED environment variable to 1.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-csharp.md#_snippet_1

LANGUAGE: csharp
CODE:
```
HEADED=1 dotnet test
```

LANGUAGE: csharp
CODE:
```
set HEADED=1
dotnet test
```

LANGUAGE: csharp
CODE:
```
$env:HEADED="1"
dotnet test
```

----------------------------------------

TITLE: Generate Playwright Locators with Codegen
DESCRIPTION: Generate locators for web elements using Playwright's test generator. Interact with elements in the browser to highlight and select locators, which can then be fine-tuned in the provided field or copied directly into your code.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/codegen.md#_snippet_2

LANGUAGE: js
CODE:
```
npx playwright codegen --help
```

LANGUAGE: java
CODE:
```
mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="codegen --help"
```

LANGUAGE: python
CODE:
```
playwright codegen --help
```

LANGUAGE: csharp
CODE:
```
pwsh bin/Debug/netX/playwright.ps1 codegen --help
```

----------------------------------------

TITLE: nth and visible selector engines
DESCRIPTION: New selector engines for selecting elements by their position or visibility. The 'nth' engine is equivalent to :nth-match, and the 'visible' engine is equivalent to :visible, allowing combination with other selectors.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_175

LANGUAGE: js
CODE:
```
// select the first button among all buttons
await button.click('button >> nth=0');
// or if you are using locators, you can use first(), nth() and last()
await page.locator('button').first().click();

// click a visible button
await button.click('button >> visible=true');
```

----------------------------------------

TITLE: Playwright Inspector Debugging
DESCRIPTION: Instructions on how to launch the Playwright Inspector for debugging tests by setting an environment variable. The Inspector provides line-by-line debugging, recording, and selector generation.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-java.md#_snippet_100

LANGUAGE: bash
CODE:
```
PWDEBUG=1
```

----------------------------------------

TITLE: JavaScript: Verify Labels with AriaUtils Selector
DESCRIPTION: Verifies accessibility labels using a provided CSS selector. This utility function is likely used in testing scenarios to assert the correct computed accessible names for elements.

SOURCE: https://github.com/microsoft/playwright/blob/main/tests/assets/wpt/accname/name/comp_text_node.html#_snippet_0

LANGUAGE: javascript
CODE:
```
AriaUtils.verifyLabelsBySelector(".ex");
```

----------------------------------------

TITLE: Element Interaction with Playwright (JavaScript)
DESCRIPTION: Locates an element using the `getByRole` locator and performs a click action. Playwright automatically waits for the element to be actionable before executing the click.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/writing-tests-js.md#_snippet_2

LANGUAGE: javascript
CODE:
```
// Create a locator.
const getStarted = page.getByRole('link', { name: 'Get started' });

// Click it.
await getStarted.click();
```

LANGUAGE: javascript
CODE:
```
await page.getByRole('link', { name: 'Get started' }).click();
```

----------------------------------------

TITLE: Nth and Visible Selectors
DESCRIPTION: Illustrates the usage of 'nth' and 'visible' selector engines for selecting elements based on their position or visibility status, offering flexibility beyond standard CSS pseudo-classes.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-java.md#_snippet_96

LANGUAGE: javascript
CODE:
```
// select the first button among all buttons
button.click("button >> nth=0");
// or if you are using locators, you can use first(), nth() and last()
page.locator("button").first().click();

// click a visible button
button.click("button >> visible=true");
```

----------------------------------------

TITLE: Run Playwright Tests in UI Mode
DESCRIPTION: Execute Playwright tests with the integrated UI Mode, offering features like time-travel debugging and watch mode. This command is executed via the command line using various package managers.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/intro-js.md#_snippet_3

LANGUAGE: npm
CODE:
```
npx playwright test --ui
```

LANGUAGE: yarn
CODE:
```
yarn playwright test --ui
```

LANGUAGE: pnpm
CODE:
```
pnpm exec playwright test --ui
```

----------------------------------------

TITLE: Playwright API: CSS Selectors and Locators
DESCRIPTION: This section covers new CSS selector extensions and locator strategies introduced in Playwright, enabling more flexible and powerful element selection.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_199

LANGUAGE: APIDOC
CODE:
```
CSS Selectors:
  - :has-text("example")
    - Matches any element containing the text "example" anywhere inside, including descendants.

  - :left-of(selector)
    - Matches elements positioned to the left of the specified selector.

  - :right-of(selector)
    - Matches elements positioned to the right of the specified selector.

  - :above(selector)
    - Matches elements positioned above the specified selector.

  - :below(selector)
    - Matches elements positioned below the specified selector.

  - :near(selector)
    - Matches elements positioned near the specified selector (combines above, below, left-of, right-of).

  - :text("exact text")
    - Matches elements with exact text content.

  - :text(/regex/)
    - Matches elements whose text content matches the regular expression.

  - :role(roleName, options)
    - Matches elements by their ARIA role.

  - :label(text)
    - Matches form controls by their associated label text.

  - :placeholder(text)
    - Matches input elements by their placeholder text.

  - :button(text)
    - Matches buttons by their text or ARIA label.
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Disabled
DESCRIPTION: Checks if the element is disabled. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_4

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeDisabled()
```

----------------------------------------

TITLE: Test GitHub API & UI: Verify Issue Order
DESCRIPTION: This test combines API calls with UI interaction to verify issue ordering. It creates two issues via the API, navigates to the project's issues page in the browser, and uses Playwright locators to assert that the most recently created issue appears first in the list.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api-testing-python.md#_snippet_6

LANGUAGE: python
CODE:
```
def test_last_created_issue_should_be_first_in_the_list(api_request_context: APIRequestContext, page: Page) -> None:
    def create_issue(title: str) -> None:
        data = {
            "title": title,
            "body": "Feature description",
        }
        new_issue = api_request_context.post(
            f"/repos/{GITHUB_USER}/{GITHUB_REPO}/issues", data=data
        )
        assert new_issue.ok
    create_issue("[Feature] request 1")
    create_issue("[Feature] request 2")
    page.goto(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues")
    first_issue = page.locator("a[data-hovercard-type='issue']").first
    expect(first_issue).to_have_text("[Feature] request 2")
```

----------------------------------------

TITLE: Debug Specific Playwright Test File
DESCRIPTION: Debugs a particular test file by specifying its name along with the --debug flag.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_9

LANGUAGE: bash
CODE:
```
npx playwright test example.spec.ts --debug
```

----------------------------------------

TITLE: React and Vue Selectors
DESCRIPTION: Demonstrates how to use experimental React and Vue selector engines to locate elements based on component names and property values, similar to CSS attribute selectors.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-java.md#_snippet_95

LANGUAGE: javascript
CODE:
```
page.locator("_react=SubmitButton[enabled=true]").click();
page.locator("_vue=submit-button[enabled=true]").click();
```

----------------------------------------

TITLE: Enable Tracing Locally
DESCRIPTION: This command allows you to force Playwright tracing to be enabled when running tests locally, even without using UI Mode. This is useful for debugging specific test runs.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/trace-viewer-intro-js.md#_snippet_1

LANGUAGE: bash
CODE:
```
npx playwright test --trace on
```

----------------------------------------

TITLE: LocatorAssertions.toBeAttached Assertion
DESCRIPTION: Describes the new web-first assertion `LocatorAssertions.toBeAttached()`, which verifies if an element is present in the DOM, distinguishing it from `toBeVisible()` which also checks for visibility.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_77

LANGUAGE: js
CODE:
```
await expect(locator).toBeAttached();
```

----------------------------------------

TITLE: Create GitHub Issue via API and Verify in UI (C#)
DESCRIPTION: This test creates a new GitHub issue using the API and then navigates to the project's issue list in the browser to confirm its presence. It utilizes Playwright's Request and Page objects for API calls and UI interactions, respectively.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api-testing-csharp.md#_snippet_4

LANGUAGE: csharp
CODE:
```
class TestGitHubAPI : PageTest
{
    [TestMethod]
    public async Task LastCreatedIssueShouldBeFirstInTheList()
    {
        var data = new Dictionary<string, string>
        {
            { "title", "[Feature] request 1" },
            { "body", "Feature description" }
        };
        var newIssue = await Request.PostAsync("/repos/" + USER + "/" + REPO + "/issues", new() { DataObject = data });
        await Expect(newIssue).ToBeOKAsync();

        // When inheriting from 'PlaywrightTest' it only gives you a Playwright instance. To get a Page instance, either start
        // a browser, context, and page manually or inherit from 'PageTest' which will launch it for you.
        await Page.GotoAsync("https://github.com/" + USER + "/" + REPO + "/issues");
        var firstIssue = Page.Locator("a[data-hovercard-type='issue']").First;
        await Expect(firstIssue).ToHaveTextAsync("[Feature] request 1");
    }
}
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Visible
DESCRIPTION: Checks if the element is visible. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_11

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeVisible()
```

----------------------------------------

TITLE: Assert Element Matches Inline ARIA Snapshot
DESCRIPTION: This snippet demonstrates how to use `toMatchAriaSnapshot` to assert that a target element's accessibility tree matches a provided inline string snapshot. This is useful for quickly verifying specific ARIA roles and names within an element's subtree.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locatorassertions.md#_snippet_65

LANGUAGE: javascript
CODE:
```
await page.goto('https://demo.playwright.dev/todomvc/');
await expect(page.locator('body')).toMatchAriaSnapshot(`
  - heading "todos"
  - textbox "What needs to be done?"
`);
```

LANGUAGE: python
CODE:
```
await page.goto("https://demo.playwright.dev/todomvc/")
await expect(page.locator('body')).to_match_aria_snapshot('''
  - heading "todos"
  - textbox "What needs to be done?"
''')
```

LANGUAGE: python
CODE:
```
page.goto("https://demo.playwright.dev/todomvc/")
expect(page.locator('body')).to_match_aria_snapshot('''
  - heading "todos"
  - textbox "What needs to be done?"
''')
```

LANGUAGE: csharp
CODE:
```
await page.GotoAsync("https://demo.playwright.dev/todomvc/");
await Expect(page.Locator("body")).ToMatchAriaSnapshotAsync(@"
  - heading ""todos""
  - textbox ""What needs to be done?""
");
```

LANGUAGE: java
CODE:
```
page.navigate("https://demo.playwright.dev/todomvc/");
assertThat(page.locator("body")).matchesAriaSnapshot("""
  - heading "todos"
  - textbox "What needs to be done?"
""");
```

----------------------------------------

TITLE: Playwright: Expect Locator to be In Viewport
DESCRIPTION: Checks if the element intersects with the viewport. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_10

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeInViewport()
```

----------------------------------------

TITLE: Run Playwright Tests on Specific Browser (C#)
DESCRIPTION: Executes Playwright tests on a specific browser by passing the browser name as a command-line argument to `dotnet test`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md#_snippet_18

LANGUAGE: bash
CODE:
```
dotnet test -- Playwright.BrowserName=webkit
```

----------------------------------------

TITLE: GitHub Actions Workflow for Playwright
DESCRIPTION: A GitHub Actions workflow file that automates the execution of Playwright tests on push or pull requests. It checks out code, sets up Node.js, installs dependencies, installs Playwright browsers, runs tests, and uploads test reports as an artifact.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/ci.md#_snippet_3

LANGUAGE: yml
CODE:
```
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Empty
DESCRIPTION: Checks if the container element (like input, textarea, or select) is empty. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_6

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeEmpty()
```

----------------------------------------

TITLE: Basic Playwright Page Fixture Usage for UI Interaction
DESCRIPTION: The `page` fixture is the most commonly used fixture, providing an isolated `Page` instance for each test. This snippet showcases typical UI interactions like navigating to a URL, filling form fields, and clicking elements, demonstrating how to automate user flows.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-api/class-fixtures.md#_snippet_4

LANGUAGE: js
CODE:
```
import { test, expect } from '@playwright/test';

test('basic test', async ({ page }) => {
  await page.goto('/signin');
  await page.getByLabel('User Name').fill('user');
  await page.getByLabel('Password').fill('password');
  await page.getByText('Sign in').click();
  // ...
});
```

----------------------------------------

TITLE: Playwright: Locate by Test ID
DESCRIPTION: Locates elements using the `data-testid` attribute. Demonstrates usage for clicking elements and configuring a custom test ID attribute via Playwright's configuration.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/params.md#_snippet_136

LANGUAGE: javascript
CODE:
```
await page.getByTestId('directions').click();
```

LANGUAGE: java
CODE:
```
page.getByTestId("directions").click();
```

LANGUAGE: python async
CODE:
```
await page.get_by_test_id("directions").click()
```

LANGUAGE: python sync
CODE:
```
page.get_by_test_id("directions").click()
```

LANGUAGE: csharp
CODE:
```
await page.GetByTestId("directions").ClickAsync();
```

LANGUAGE: javascript
CODE:
```
// Set custom test id attribute from @playwright/test config:
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    testIdAttribute: 'data-pw'
  },
});
```

----------------------------------------

TITLE: Playwright CLI Test Execution Modes
DESCRIPTION: Control how Playwright tests are executed via CLI flags. Options include disabling parallelization, running in debug mode with the Inspector, and enabling interactive UI mode.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-cli-js.md#_snippet_1

LANGUAGE: bash
CODE:
```
# Disable parallelization (run tests sequentially)
npx playwright test --workers=1
```

LANGUAGE: bash
CODE:
```
# Run in debug mode with Playwright Inspector
npx playwright test --debug
```

LANGUAGE: bash
CODE:
```
# Run tests in interactive UI mode
npx playwright test --ui
```

----------------------------------------

TITLE: Debugging with pdb
DESCRIPTION: Demonstrates how to use the `breakpoint()` function within Playwright tests to pause execution and enter a Python debugger (pdb) session for inspection.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-runners-python.md#_snippet_19

LANGUAGE: python
CODE:
```
def test_bing_is_working(page):
    page.goto("https://bing.com")
    breakpoint()
    # ...

```

----------------------------------------

TITLE: Playwright: Expect Locator to be Focused
DESCRIPTION: Checks if the element has focus. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_8

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeFocused()
```

----------------------------------------

TITLE: Debug Playwright .NET tests with Playwright Inspector
DESCRIPTION: Enable the Playwright Inspector for debugging Playwright .NET tests by setting the `PWDEBUG` environment variable before running `dotnet test`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-csharp.md#_snippet_7

LANGUAGE: bash
CODE:
```
PWDEBUG=1 dotnet test
```

LANGUAGE: batch
CODE:
```
set PWDEBUG=1
dotnet test
```

LANGUAGE: powershell
CODE:
```
$env:PWDEBUG=1
dotnet test
```

----------------------------------------

TITLE: Debug Specific Playwright Test File and Line
DESCRIPTION: To debug a particular test, specify the test file name and the line number followed by the `--debug` flag. This focuses the debugging session on the exact test you intend to troubleshoot, improving efficiency.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/best-practices-js.md#_snippet_8

LANGUAGE: npm
CODE:
```
npx playwright test example.spec.ts:9 --debug
```

LANGUAGE: yarn
CODE:
```
yarn playwright test example.spec.ts:9 --debug
```

LANGUAGE: pnpm
CODE:
```
pnpm exec playwright test example.spec.ts:9 --debug
```

----------------------------------------

TITLE: React and Vue selector engines
DESCRIPTION: Experimental selector engines for React and Vue components. These allow selecting elements based on component names and/or property values, using syntax similar to CSS attribute selectors.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_174

LANGUAGE: js
CODE:
```
await page.locator('_react=SubmitButton[enabled=true]').click();
await page.locator('_vue=submit-button[enabled=true]').click();
```

----------------------------------------

TITLE: Register and Use Custom Selector in C#
DESCRIPTION: Demonstrates registering a custom selector engine named 'tag' in Playwright using C#. It defines the query and queryAll functions for the selector and shows how to use the custom selector to locate elements on a page.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-selectors.md#_snippet_1

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;

using var playwright = await Playwright.CreateAsync();
// Script that evaluates to a selector engine instance. The script is evaluated in the page context.
await playwright.Selectors.RegisterAsync("tag", new()
{
    Script = @"{ 
    // Returns the first element matching given selector in the root's subtree.
    query(root, selector) { 
        return root.querySelector(selector);
      },
      // Returns all elements matching given selector in the root's subtree.
      queryAll(root, selector) { 
        return Array.from(root.querySelectorAll(selector));
      }
    }"
});

await using var browser = await playwright.Chromium.LaunchAsync();
var page = await browser.NewPageAsync();
await page.SetContentAsync("<div><button>Click me</button></div>");
// Use the selector prefixed with its name.
var button = page.Locator("tag=button");
// Combine it with built-in locators.
await page.Locator("tag=div").GetByText("Click me").ClickAsync();
// Can use it in any methods supporting selectors.
int buttonCount = await page.Locator("tag=button").CountAsync();
```

----------------------------------------

TITLE: Launch Browser, Navigate, and Screenshot
DESCRIPTION: Demonstrates launching a browser instance, creating a new page, navigating to a specified URL, and capturing a screenshot of the page. This functionality is crucial for web scraping and automated testing.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-page.md#_snippet_0

LANGUAGE: js
CODE:
```
const { webkit } = require('playwright');  // Or 'chromium' or 'firefox'.

(async () => {
  const browser = await webkit.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'screenshot.png' });
  await browser.close();
})();
```

LANGUAGE: java
CODE:
```
import com.microsoft.playwright.*;

public class Example {
  public static void main(String[] args) {
    try (Playwright playwright = Playwright.create()) {
      BrowserType webkit = playwright.webkit();
      Browser browser = webkit.launch();
      BrowserContext context = browser.newContext();
      Page page = context.newPage();
      page.navigate("https://example.com");
      page.screenshot(new Page.ScreenshotOptions().setPath(Paths.get("screenshot.png")));
      browser.close();
    }
  }
}
```

LANGUAGE: python async
CODE:
```
import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
    webkit = playwright.webkit
    browser = await webkit.launch()
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://example.com")
    await page.screenshot(path="screenshot.png")
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
```

LANGUAGE: python sync
CODE:
```
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    webkit = playwright.webkit
    browser = webkit.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;
using System.Threading.Tasks;

class PageExamples
{
    public static async Task Run()
    {
        using var playwright = await Playwright.CreateAsync();
        await using var browser = await playwright.Webkit.LaunchAsync();
        var page = await browser.NewPageAsync();
        await page.GotoAsync("https://www.theverge.com");
        await page.ScreenshotAsync(new() { Path = "theverge.png" });
    }
}
```

----------------------------------------

TITLE: Skip Test by Browser
DESCRIPTION: Shows how to skip a test execution on a specific browser using the `pytest.mark.skip_browser` decorator. This is useful for tests that are not compatible with certain browsers.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-runners-python.md#_snippet_9

LANGUAGE: python
CODE:
```
import pytest

@pytest.mark.skip_browser("firefox")
def test_visit_example(page):
    page.goto("https://example.com")
    # ...

```

----------------------------------------

TITLE: Assert Element Matches Aria Snapshot (Inline)
DESCRIPTION: Asserts that the target element matches the given accessibility snapshot string. This method is useful for quick, inline snapshot testing of an element's accessibility tree. It requires the Playwright assertion library.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-locatorassertions.md#_snippet_52

LANGUAGE: js
CODE:
```
await expect(page.locator('body')).toMatchAriaSnapshot(`
  - heading "todos"
  - textbox "What needs to be done?"
`);
```

LANGUAGE: python
CODE:
```
await page.goto("https://demo.playwright.dev/todomvc/")
await expect(page.locator('body')).to_match_aria_snapshot('''
  - heading "todos"
  - textbox "What needs to be done?"
''')
```

LANGUAGE: python
CODE:
```
page.goto("https://demo.playwright.dev/todomvc/")
expect(page.locator('body')).to_match_aria_snapshot('''
  - heading "todos"
  - textbox "What needs to be done?"
''')
```

LANGUAGE: csharp
CODE:
```
await page.GotoAsync("https://demo.playwright.dev/todomvc/");
await Expect(page.Locator("body")).ToMatchAriaSnapshotAsync(@"
  - heading \"todos\"
  - textbox \"What needs to be done?\"
");
```

LANGUAGE: java
CODE:
```
page.navigate("https://demo.playwright.dev/todomvc/");
assertThat(page.locator("body")).matchesAriaSnapshot("""
  - heading \"todos\"
  - textbox \"What needs to be done?\"
""");
```

----------------------------------------

TITLE: Playwright C# Tag Selectors
DESCRIPTION: Demonstrates registering and using custom 'tag=' selectors in Playwright for C#. This involves providing a script to the selector engine that defines how to query elements. Once registered, 'tag=' selectors can be used similarly to built-in locators.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/extensibility.md#_snippet_3

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;
using System;
using System.Threading.Tasks;

public class TagSelectorsExample
{
    public static async Task Main(string[] args)
    {
        using var playwright = await Playwright.CreateAsync();
        await using var browser = await playwright.Chromium.LaunchAsync();
        var page = await browser.NewPageAsync();
        await page.GotoAsync("data:text/html,<button>Click Me</button><div>Click Me</div>");

        // Register the engine. Selectors will be prefixed with "tag=".
        // The script is evaluated in the page context.
        await playwright.Selectors.RegisterAsync("tag", new Selectors.RegisterOptions
        {
            // Must evaluate to a selector engine instance.
            Script = @"(
              // Returns the first element matching given selector in the root's subtree.
              query = (root, selector) => root.querySelector(selector),

              // Returns all elements matching given selector in the root's subtree.
              queryAll = (root, selector) => Array.from(root.querySelectorAll(selector))
            )"
        });

        // Now we can use "tag=" selectors.
        await page.Locator("tag=button").ClickAsync();

        // We can combine it with built-in locators.
        await page.Locator("tag=div").GetByText("Click me").ClickAsync();

        // Get the count of elements matching a selector
        var buttonCount = await page.Locator("tag=button").CountAsync();
        Console.WriteLine($"Button count: {buttonCount}");

        await browser.CloseAsync();
    }
}
```

----------------------------------------

TITLE: Run Playwright Tests on Multiple Browsers (C#)
DESCRIPTION: Runs Playwright tests on multiple browsers or configurations by invoking `dotnet test` multiple times, specifying the browser via environment variables or runsettings files.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md#_snippet_19

LANGUAGE: bash
CODE:
```
dotnet test --settings:chromium.runsettings
dotnet test --settings:firefox.runsettings
dotnet test --settings:webkit.runsettings
```

----------------------------------------

TITLE: Playwright React and Vue Selectors
DESCRIPTION: Experimental selector engines for React and Vue components. They allow selecting elements by component name and/or property values, supporting attribute selector operators.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-csharp.md#_snippet_87

LANGUAGE: csharp
CODE:
```
await page.Locator("_react=SubmitButton[enabled=true]").ClickAsync();
await page.Locator("_vue=submit-button[enabled=true]").ClickAsync();
```

----------------------------------------

TITLE: Debug Specific Playwright Test by Name with Inspector
DESCRIPTION: Enable the Playwright Inspector for debugging a specific test function by name using PWDEBUG=1 and the -k flag.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_10

LANGUAGE: bash
CODE:
```
PWDEBUG=1 pytest -s -k test_get_started_link
```

LANGUAGE: batch
CODE:
```
set PWDEBUG=1
pytest -s -k test_get_started_link
```

LANGUAGE: powershell
CODE:
```
$env:PWDEBUG=1
pytest -s -k test_get_started_link
```

----------------------------------------

TITLE: Element Queries: Label Text
DESCRIPTION: Shows how to find elements associated with a label using its text content.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/testing-library-js.md#_snippet_5

LANGUAGE: javascript
CODE:
```
screen.getByLabelText('...');
```

LANGUAGE: javascript
CODE:
```
component.getByLabel('...');
```

----------------------------------------

TITLE: Debug Specific Playwright Test File with Inspector
DESCRIPTION: Enable the Playwright Inspector for debugging a specific test file by setting PWDEBUG=1 and providing the file name.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-python.md#_snippet_9

LANGUAGE: bash
CODE:
```
PWDEBUG=1 pytest -s test_example.py
```

LANGUAGE: batch
CODE:
```
set PWDEBUG=1
pytest -s test_example.py
```

LANGUAGE: powershell
CODE:
```
$env:PWDEBUG=1
pytest -s test_example.py
```

----------------------------------------

TITLE: Scan for WCAG A/AA Violations with AxeBuilder
DESCRIPTION: Scans a page for WCAG 2.1 A and AA violations using AxeBuilder with specific tags. This example demonstrates how to filter accessibility rules to match WCAG 2.1 A and AA success criteria.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/accessibility-testing-js.md#_snippet_2

LANGUAGE: js
CODE:
```
test('should not have any automatically detectable WCAG A or AA violations', async ({ page }) => {
  await page.goto('https://your-site.com/');

  const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

----------------------------------------

TITLE: Debug Specific Line in Playwright Test
DESCRIPTION: Debugs a Playwright test starting from a specific line number within a file by appending the line number to the filename.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_10

LANGUAGE: bash
CODE:
```
npx playwright test example.spec.ts:10 --debug
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Hidden
DESCRIPTION: Checks if the element is not visible. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_9

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeHidden()
```

----------------------------------------

TITLE: Page.getByRole - Locate elements by ARIA role
DESCRIPTION: Creates a Locator that finds an element by its ARIA role. This is a powerful method for accessibility-focused testing, allowing selection based on semantic roles like 'button', 'textbox', etc.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-page.md#_snippet_70

LANGUAGE: APIDOC
CODE:
```
Page.getByRole(role: str, options?: { name?: str, exact?: bool, includeHidden?: bool }): Locator

- Parameters:
  - role: The ARIA role to match (e.g., 'button', 'textbox').
  - options:
    - name: Text associated with the role (e.g., button label).
    - exact: Whether the name should match exactly (default: false).
    - includeHidden: Whether to include hidden elements (default: false).

- Returns:
  A Locator instance.
```

----------------------------------------

TITLE: Debug All Playwright Tests
DESCRIPTION: Runs all tests and opens the Playwright Inspector, allowing you to step through test execution and inspect elements on the page.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_8

LANGUAGE: bash
CODE:
```
npx playwright test --debug
```

----------------------------------------

TITLE: Run Specific Playwright Test Files or Directories
DESCRIPTION: Allows running individual test files, directories containing tests, or tests matching specific keywords. This is useful for focused testing or debugging.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_snippet_4

LANGUAGE: bash
CODE:
```
npx playwright test landing-page.spec.ts
npx playwright test tests/todo-page/ tests/landing-page/
npx playwright test landing login
```

----------------------------------------

TITLE: Playwright CSS Selectors by Text and Layout
DESCRIPTION: Details new CSS selector capabilities in Playwright for matching elements based on their text content and relative layout positions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-java.md#_snippet_101

LANGUAGE: APIDOC
CODE:
```
CSS Selectors:

:has-text("example")
  - Matches any element containing "example" somewhere inside, possibly in a child or a descendant element.

Layout-based selectors:
  - :left-of(selector)
  - :right-of(selector)
  - :above(selector)
  - :below(selector)
  - These selectors match elements based on their spatial relationship to another element identified by the provided selector.
```

----------------------------------------

TITLE: Run Playwright Tests with JUnit 5
DESCRIPTION: Demonstrates how to set up and run Playwright tests using JUnit 5. It covers initializing Playwright and Browser in @BeforeAll, creating BrowserContext and Page in @BeforeEach, and closing them in @AfterAll and @AfterEach. The example includes tests for clicking buttons, checking checkboxes, and performing searches, showcasing basic Playwright interactions.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-java.md#_snippet_0

LANGUAGE: java
CODE:
```
package org.example;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestExample {
  // Shared between all tests in this class.
  static Playwright playwright;
  static Browser browser;

  // New instance for each test method.
  BrowserContext context;
  Page page;

  @BeforeAll
  static void launchBrowser() {
    playwright = Playwright.create();
    browser = playwright.chromium().launch();
  }

  @AfterAll
  static void closeBrowser() {
    playwright.close();
  }

  @BeforeEach
  void createContextAndPage() {
    context = browser.newContext();
    page = context.newPage();
  }

  @AfterEach
  void closeContext() {
    context.close();
  }

  @Test
  void shouldClickButton() {
    page.navigate("data:text/html,<script>var result;</script><button onclick='result="Clicked"'>Go</button>");
    page.locator("button").click();
    assertEquals("Clicked", page.evaluate("result"));
  }

  @Test
  void shouldCheckTheBox() {
    page.setContent("<input id='checkbox' type='checkbox'></input>");
    page.locator("input").check();
    assertTrue((Boolean) page.evaluate("() => window['checkbox'].checked"));
  }

  @Test
  void shouldSearchWiki() {
    page.navigate("https://www.wikipedia.org/");
    page.locator("input[name=\"search\"]").click();
    page.locator("input[name=\"search\"]").fill("playwright");
    page.locator("input[name=\"search\"]").press("Enter");
    assertEquals("https://en.wikipedia.org/wiki/Playwright", page.url());
  }
}
```

----------------------------------------

TITLE: Playwright: Expect Locator to Match Aria Snapshot
DESCRIPTION: Checks if the element matches the Aria snapshot. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_27

LANGUAGE: javascript
CODE:
```
await expect(locator).toMatchAriaSnapshot()
```

----------------------------------------

TITLE: Playwright Selectors.setTestIdAttribute API
DESCRIPTION: Defines a custom attribute name to be used by Playwright's `Page.getByTestId` method. By default, `data-testid` is used, but this method allows overriding it to a different attribute.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-selectors.md#_snippet_4

LANGUAGE: APIDOC
CODE:
```
Selectors.setTestIdAttribute(attributeName)
  - since: v1.27
  - attributeName: <string>
    - Test id attribute name.
```

----------------------------------------

TITLE: Record Trace Locally
DESCRIPTION: Enables trace recording during local test execution using the Playwright CLI. Setting the `--trace` flag to `on` will record traces for all tests. This is helpful for debugging during development, and can be combined with UI Mode for an enhanced experience.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/trace-viewer.md#_snippet_3

LANGUAGE: bash
CODE:
```
npx playwright test --trace on
```

----------------------------------------

TITLE: Configure Browser Context with Device Profiles
DESCRIPTION: Shows how to configure browser contexts with predefined device profiles, such as mobile devices, for testing responsive web applications. This involves accessing the `devices` dictionary and passing device options to `browser.newContext()`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-playwright.md#_snippet_1

LANGUAGE: js
CODE:
```
const { webkit, devices } = require('playwright');
const iPhone = devices['iPhone 6'];

(async () => {
  const browser = await webkit.launch();
  const context = await browser.newContext({
    ...iPhone
  });
  const page = await context.newPage();
  await page.goto('http://example.com');
  // other actions...
  await browser.close();
})();
```

LANGUAGE: python
CODE:
```
import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
    webkit = playwright.webkit
    iphone = playwright.devices["iPhone 6"]
    browser = await webkit.launch()
    context = await browser.new_context(**iphone)
    page = await context.new_page()
    await page.goto("http://example.com")
    # other actions...
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
```

LANGUAGE: python
CODE:
```
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    webkit = playwright.webkit
    iphone = playwright.devices["iPhone 6"]
    browser = webkit.launch()
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto("http://example.com")
    # other actions...
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;
using System.Threading.Tasks;

class PlaywrightExample
{
    public static async Task Main()
    {
        using var playwright = await Playwright.CreateAsync();
        await using var browser = await playwright.Webkit.LaunchAsync();
        await using var context = await browser.NewContextAsync(playwright.Devices["iPhone 6"]);

        var page = await context.NewPageAsync();
        await page.GotoAsync("https://www.theverge.com");
        // other actions...
    }
}
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Editable
DESCRIPTION: Checks if the element is editable. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_5

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeEditable()
```

----------------------------------------

TITLE: Running .NET Tests with Browser Channel
DESCRIPTION: Executes .NET tests using the `dotnet test` command, passing Playwright configuration options like browser name and channel as arguments. This method overrides default settings for test execution.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md#_snippet_38

LANGUAGE: bash
CODE:
```
dotnet test -- Playwright.BrowserName=chromium Playwright.LaunchOptions.Channel=msedge
```

----------------------------------------

TITLE: Playwright Locator API: Highlight Element
DESCRIPTION: Introduces the `Locator.highlight` method, which visually outlines the selected element(s) on the page. This is a valuable debugging tool for quickly identifying which elements are being targeted by Playwright selectors.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/release-notes-js.md#_snippet_129

LANGUAGE: APIDOC
CODE:
```
method: Locator.highlight
  Description: Highlights the element(s) on the page.
  Usage:
    await page.locator('selector').highlight();
```

----------------------------------------

TITLE: Run Tests with Custom Browser Build
DESCRIPTION: Execute tests using a custom browser executable by setting the CRPATH environment variable. This allows testing against specific browser builds or configurations.

SOURCE: https://github.com/microsoft/playwright/blob/main/CONTRIBUTING.md#_snippet_8

LANGUAGE: bash
CODE:
```
CRPATH=<path-to-executable> npm run ctest
```

----------------------------------------

TITLE: Frame.querySelector and Frame.querySelectorAll
DESCRIPTION: Find elements within a frame using CSS selectors. `querySelector` returns the first matching element or null, while `querySelectorAll` returns an array of all matching elements. These methods are discouraged in favor of locator-based approaches. They accept a selector string and an optional strict mode parameter.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-frame.md#_snippet_28

LANGUAGE: APIDOC
CODE:
```
async method: Frame.querySelector
  * since: v1.9
  * discouraged: Use locator-based [`method: Frame.locator`] instead. Read more about [locators](../locators.md).
  * langs:
    - alias-python: query_selector
    - alias-js: $
  - returns: <[null]|[ElementHandle]>

  Returns the ElementHandle pointing to the frame element.

  :::caution
  The use of [ElementHandle] is discouraged, use [Locator] objects and web-first assertions instead.
  :::

  The method finds an element matching the specified selector within the frame. If no elements match the selector,
  returns `null`.

  ### param: Frame.querySelector.selector = %%-query-selector-%%
    * since: v1.9

  ### option: Frame.querySelector.strict = %%-input-strict-%%
    * since: v1.14

async method: Frame.querySelectorAll
  * since: v1.9
  * discouraged: Use locator-based [`method: Frame.locator`] instead. Read more about [locators](../locators.md).
  * langs:
    - alias-python: query_selector_all
    - alias-js: $$
  - returns: <[Array]<[ElementHandle]>>

  Returns the ElementHandles pointing to the frame elements.

  :::caution
  The use of [ElementHandle] is discouraged, use [Locator] objects instead.
  :::

  The method finds all elements matching the specified selector within the frame. If no elements match the selector,
  returns empty array.

  ### param: Frame.querySelectorAll.selector = %%-query-selector-%%
    * since: v1.9
```

----------------------------------------

TITLE: Disable JavaScript Execution
DESCRIPTION: Illustrates how to configure Playwright to disable JavaScript execution in the browser. This is useful for testing websites that rely on progressive enhancement or for debugging JavaScript-related issues.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/emulation.md#_snippet_33

LANGUAGE: javascript
CODE:
```
import { test, expect } from '@playwright/test';

test.use({ javaScriptEnabled: false });

test('test with no JavaScript', async ({ page }) => {
  // ...
});
```

LANGUAGE: javascript
CODE:
```
const context = await browser.newContext({
  javaScriptEnabled: false
});
```

----------------------------------------

TITLE: Playwright: Expect Locator to be Attached
DESCRIPTION: Checks if the element is attached to the DOM. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_2

LANGUAGE: javascript
CODE:
```
await expect(locator).toBeAttached()
```

----------------------------------------

TITLE: Run Playwright Tests on Multiple Browsers (Python)
DESCRIPTION: Runs Playwright tests concurrently on multiple specified browsers by repeating the `--browser` argument with pytest.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md#_snippet_13

LANGUAGE: bash
CODE:
```
pytest test_login.py --browser webkit --browser firefox
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Accessible Description
DESCRIPTION: Checks if the element has a matching accessible description. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_14

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveAccessibleDescription()
```

----------------------------------------

TITLE: Test UI & GitHub API: Verify Issue Creation
DESCRIPTION: This test case validates issue creation through the user interface and then confirms it via the GitHub API. It simulates user actions to create an issue in the browser, extracts the issue ID from the URL, and uses the APIRequestContext to fetch the issue details, asserting their correctness.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api-testing-python.md#_snippet_7

LANGUAGE: python
CODE:
```
def test_last_created_issue_should_be_on_the_server(api_request_context: APIRequestContext, page: Page) -> None:
    page.goto(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues")
    page.locator("text=New issue").click()
    page.locator("[aria-label='Title']").fill("Bug report 1")
    page.locator("[aria-label='Comment body']").fill("Bug description")
    page.locator("text=Submit new issue").click()
    issue_id = page.url.split("/")[-1]

    new_issue = api_request_context.get(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues/{issue_id}")
    assert new_issue.ok
    assert new_issue.json()["title"] == "[Bug] report 1"
    assert new_issue.json()["body"] == "Bug description"
```

----------------------------------------

TITLE: Playwright: Expect Locator to Have Class
DESCRIPTION: Checks if the element has the specified CSS class property. This assertion is auto-retrying and requires `await`.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-assertions-js.md#_snippet_17

LANGUAGE: javascript
CODE:
```
await expect(locator).toHaveClass()
```

----------------------------------------

TITLE: UI Test: Create Issue via API and Validate
DESCRIPTION: This example shows how to set up a Playwright request context in `beforeAll` to create a GitHub issue via API. It then navigates to the issues page in the browser and asserts that the newly created issue appears at the top of the list.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api-testing-js.md#_snippet_7

LANGUAGE: js
CODE:
```
import { test, expect } from '@playwright/test';

const REPO = 'test-repo-1';
const USER = 'github-username';

// Request context is reused by all tests in the file.
let apiContext;

test.beforeAll(async ({ playwright }) => {
  apiContext = await playwright.request.newContext({
    // All requests we send go to this API endpoint.
    baseURL: 'https://api.github.com',
    extraHTTPHeaders: {
      // We set this header per GitHub guidelines.
      'Accept': 'application/vnd.github.v3+json',
      // Add authorization token to all requests.
      // Assuming personal access token available in the environment.
      'Authorization': `token ${process.env.API_TOKEN}`,
    },
  });
});

test.afterAll(async ({ }) => {
  // Dispose all responses.
  await apiContext.dispose();
});

test('last created issue should be first in the list', async ({ page }) => {
  const newIssue = await apiContext.post(`/repos/${USER}/${REPO}/issues`, {
    data: {
      title: '[Feature] request 1',
    }
  });
  expect(newIssue.ok()).toBeTruthy();

  await page.goto(`https://github.com/${USER}/${REPO}/issues`);
  const firstIssue = page.locator(`a[data-hovercard-type='issue']`).first();
  await expect(firstIssue).toHaveText('[Feature] request 1');
});
```

----------------------------------------

TITLE: Playwright Frame.waitForSelector Method
DESCRIPTION: Waits for the specified selector to satisfy a given state (appear, disappear, visible, hidden). While functional, Playwright recommends using Locator-based assertions for more robust and maintainable tests, as they automatically handle waiting. This method returns an ElementHandle or null.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-frame.md#_snippet_48

LANGUAGE: js
CODE:
```
const { chromium } = require('playwright');  // Or 'firefox' or 'webkit'.

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const currentURL of ['https://google.com', 'https://bbc.com']) {
    await page.goto(currentURL);
    const element = await page.mainFrame().waitForSelector('img');
    console.log('Loaded image: ' + await element.getAttribute('src'));
  }
  await browser.close();
})();
```

LANGUAGE: java
CODE:
```
import com.microsoft.playwright.*;

public class Example {
  public static void main(String[] args) {
    try (Playwright playwright = Playwright.create()) {
      BrowserType chromium = playwright.chromium();
      Browser browser = chromium.launch();
      Page page = browser.newPage();
      for (String currentURL : Arrays.asList("https://google.com", "https://bbc.com")) {
        page.navigate(currentURL);
        ElementHandle element = page.mainFrame().waitForSelector("img");
        System.out.println("Loaded image: " + element.getAttribute("src"));
      }
      browser.close();
    }
  }
}
```

LANGUAGE: python
CODE:
```
import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    for current_url in ["https://google.com", "https://bbc.com"]:
        await page.goto(current_url, wait_until="domcontentloaded")
        element = await page.main_frame.wait_for_selector("img")
        print("Loaded image: " + str(await element.get_attribute("src")))
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
```

LANGUAGE: python
CODE:
```
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    for current_url in ["https://google.com", "https://bbc.com"]:
        page.goto(current_url, wait_until="domcontentloaded")
        element = page.main_frame.wait_for_selector("img")
        print("Loaded image: " + str(element.get_attribute("src")))
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;
using System;
using System.Threading.Tasks;

class FrameExamples
{
    public static async Task Main()
    {
        using var playwright = await Playwright.CreateAsync();
        await using var browser = await playwright.Chromium.LaunchAsync();
        var page = await browser.NewPageAsync();

        foreach (var currentUrl in new[] { "https://www.google.com", "https://bbc.com" })
        {
            await page.GotoAsync(currentUrl);
            element = await page.MainFrame.WaitForSelectorAsync("img");
            Console.WriteLine($"Loaded image: {await element.GetAttributeAsync("src")}");
        }
    }
}
```

----------------------------------------

TITLE: Registering Custom Selector Engine in Playwright C#
DESCRIPTION: This C# example demonstrates how to register a custom selector engine using `Playwright.Selectors.RegisterAsync`. The custom engine defines `query` and `queryAll` methods to find elements by a custom 'tag' selector. It then shows how to use this custom selector with `Locator` and other Playwright methods.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/api/class-selectors.md#_snippet_2

LANGUAGE: csharp
CODE:
```
using Microsoft.Playwright;

using var playwright = await Playwright.CreateAsync();
// Script that evaluates to a selector engine instance. The script is evaluated in the page context.
await playwright.Selectors.RegisterAsync("tag", new()
{
    Script = @"{
    // Returns the first element matching given selector in the root's subtree.
    query(root, selector) {
        return root.querySelector(selector);
      },
      // Returns all elements matching given selector in the root's subtree.
    queryAll(root, selector) {
        return Array.from(root.querySelectorAll(selector));
      }
    }"
});

await using var browser = await playwright.Chromium.LaunchAsync();
var page = await browser.NewPageAsync();
await page.SetContentAsync("<div><button>Click me</button></div>");
// Use the selector prefixed with its name.
var button = page.Locator("tag=button");
// Combine it with built-in locators.
await page.Locator("tag=div").GetByText("Click me").ClickAsync();
// Can use it in any methods supporting selectors.
int buttonCount = await page.Locator("tag=button").CountAsync();
```

----------------------------------------

TITLE: Run Playwright Tests on Specific Browser (Python)
DESCRIPTION: Executes Playwright tests targeting a particular browser like WebKit using the `--browser` command-line argument with pytest.

SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md#_snippet_12

LANGUAGE: bash
CODE:
```
pytest test_login.py --browser webkit
```

========================
QUESTIONS AND ANSWERS
========================
TOPIC: Debugging Playwright Tests with VS Code and Inspector
Q: How can Playwright tests be debugged on different browsers in VS Code?
A: You can debug Playwright tests on different browsers by right-clicking the debug icon in the testing sidebar, selecting 'Select Default Profile', and choosing the desired browser profile from the dropdown.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_qa_7

----------------------------------------

TOPIC: Debugging Playwright Tests with VS Code and Inspector
Q: How can you debug Playwright tests using Chrome DevTools?
A: To use Chrome DevTools, run your Playwright test with 'Show Browser' enabled in VS Code. Then, select 'Run Test' instead of 'Debug Test' to allow the browser session to be reused for DevTools debugging.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_qa_6

----------------------------------------

TOPIC: Running and debugging tests
Q: How can Playwright tests be run in a visible browser window?
A: Playwright tests can be run in headed mode using the `--headed` CLI argument. Alternatively, tests can be run in UI mode using the `--ui` flag, which also provides debugging features.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-js.md#_qa_1

----------------------------------------

TOPIC: Debugging Playwright Tests with VS Code and Inspector
Q: What is the 'Live Debugging' feature in Playwright with VS Code?
A: Live Debugging allows you to see locators highlighted in the browser window as you click on them in VS Code. You can also edit locators in VS Code and see the changes reflected live in the browser.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_qa_2

----------------------------------------

TOPIC: Debugging Playwright Tests with VS Code and Inspector
Q: How can you pick and copy locators using the VS Code Playwright extension?
A: You can use the 'Pick locator' button in the VS Code testing sidebar. Clicking this button, then clicking an element in the browser, will populate the locator in VS Code. Pressing 'enter' copies it to your clipboard.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/debug.md#_qa_3

----------------------------------------

TOPIC: UI Mode
Q: What is Playwright's UI Mode?
A: Playwright's UI Mode is a feature that allows you to explore, run, and debug tests with a time-traveling experience and a watch mode. It displays all test files in a sidebar, enabling individual running, viewing, watching, and debugging of each test.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-ui-mode-js.md#_qa_0

----------------------------------------

TOPIC: 
Q: Can Playwright Inspector be used to explore selectors?
A: Yes, Playwright Inspector includes a selector explorer that allows you to test and validate your selectors against the current DOM. This ensures that your selectors are robust and correctly target the intended elements.


SOURCE: https://github.com/microsoft/playwright/blob/main/packages/recorder/index.html#_qa_3

----------------------------------------

TOPIC: Running and debugging tests
Q: How can Playwright tests be executed on different browsers?
A: Playwright tests can be executed on different browsers by specifying the desired browser using the `BROWSER` environment variable, such as `BROWSER=webkit dotnet test`. Alternatively, you can configure the browser name directly in the launch configuration with `dotnet test --Playwright.BrowserName=webkit`.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-csharp.md#_qa_2

----------------------------------------

TOPIC: UI Mode
Q: How does Playwright's UI Mode help with debugging source code?
A: As you hover over actions in Playwright's UI Mode, the corresponding line of code in your test file is highlighted in the source panel. You can also click a button to open the test directly in VS Code at the highlighted line.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/test-ui-mode-js.md#_qa_7

----------------------------------------

TOPIC: Running and debugging tests
Q: How can Playwright and Browser objects be managed in JUnit tests?
A: In JUnit tests, Playwright and Browser objects can be initialized in an `@BeforeAll` method and destroyed in an `@AfterAll` method. This allows multiple test methods to share the same Browser instance.


SOURCE: https://github.com/microsoft/playwright/blob/main/docs/src/running-tests-java.md#_qa_3