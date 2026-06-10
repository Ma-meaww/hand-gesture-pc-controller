from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

THAIJO_URL = "https://www.tci-thaijo.org/"

driver = None
last_search_box = None


def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def is_driver_alive() -> bool:
    global driver

    if driver is None:
        return False

    try:
        _ = driver.current_url
        return True
    except WebDriverException:
        driver = None
        return False


def get_driver():
    global driver

    if not is_driver_alive():
        driver = create_driver()

    return driver


def is_thaijo_open() -> bool:
    global driver

    if not is_driver_alive():
        return False

    try:
        return "tci-thaijo.org" in driver.current_url
    except WebDriverException:
        driver = None
        return False


def open_thaijo() -> str:
    global last_search_box

    browser = get_driver()
    browser.get(THAIJO_URL)
    last_search_box = None

    return "Opened ThaiJO"


def find_search_box(timeout: int = 10):
    if not is_thaijo_open():
        return None

    wait = WebDriverWait(driver, timeout)

    try:
        return wait.until(lambda d: d.execute_script("""
            const elements = Array.from(document.querySelectorAll('input, textarea'));

            function isVisible(el) {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);

                return (
                    rect.width > 80 &&
                    rect.height > 20 &&
                    style.display !== 'none' &&
                    style.visibility !== 'hidden' &&
                    !el.disabled &&
                    el.type !== 'hidden'
                );
            }

            const candidates = elements.filter(isVisible);

            const target = candidates.find(el => {
                const placeholder = (el.placeholder || '').toLowerCase();
                const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                const title = (el.getAttribute('title') || '').toLowerCase();
                const name = (el.name || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                const type = (el.type || '').toLowerCase();

                return (
                    placeholder.includes('ค้น') ||
                    placeholder.includes('ค้นหา') ||
                    placeholder.includes('search') ||
                    ariaLabel.includes('ค้น') ||
                    ariaLabel.includes('ค้นหา') ||
                    ariaLabel.includes('search') ||
                    title.includes('ค้น') ||
                    title.includes('ค้นหา') ||
                    title.includes('search') ||
                    name.includes('search') ||
                    name.includes('keyword') ||
                    name.includes('query') ||
                    id.includes('search') ||
                    id.includes('keyword') ||
                    id.includes('query') ||
                    type === 'search'
                );
            });

            if (target) {
                target.scrollIntoView({ block: 'center' });
                return target;
            }

            return null;
        """))
    except TimeoutException:
        return None


def input_thaijo_search(keyword: str) -> str:
    global last_search_box

    if not keyword:
        return "No keyword to search"

    if not is_thaijo_open():
        return "ThaiJO is not open. Please use OPEN_THAIJO first."

    search_box = find_search_box()

    if search_box is None:
        return "ThaiJO search box not found"

    last_search_box = search_box

    search_box.click()
    search_box.send_keys(Keys.CONTROL, "a")
    search_box.send_keys(keyword)

    return f"Input ThaiJO keyword: {keyword}"


def submit_thaijo_search() -> str:
    global last_search_box

    if not is_thaijo_open():
        return "ThaiJO is not open. Please use OPEN_THAIJO first."

    search_box = find_search_box(timeout=5)

    if search_box is None:
        return "ThaiJO search box not found"

    last_search_box = search_box
    search_box.send_keys(Keys.ENTER)

    return "Submitted ThaiJO search"

def close_browser() -> str:
    global driver, last_search_box

    if driver is None:
        return "Browser is not open"

    try:
        driver.quit()
    except WebDriverException:
        pass

    driver = None
    last_search_box = None

    return "Browser closed"