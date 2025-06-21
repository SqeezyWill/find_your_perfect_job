import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

def scrape_brightermonday(query):
    print(f"🔍 Scraping BrighterMonday for '{query}'")
    jobs = []
    try:
        driver = init_driver()
        search_url = f"https://www.brightermonday.co.ke/jobs?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        listings = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-col.gap-y-2")

        for job in listings[:10]:  # Limit to top 10
            try:
                title_elem = job.find_element(By.CSS_SELECTOR, "p.text-body-s")
                link_elem = job.find_element(By.CSS_SELECTOR, "a")
                desc_elem = job.find_element(By.CSS_SELECTOR, "p.text-body-m")

                jobs.append({
                    'title': title_elem.text,
                    'link': link_elem.get_attribute('href'),
                    'description': desc_elem.text
                })
            except Exception:
                continue

        driver.quit()
        print(f"🧾 Found {len(jobs)} BM listings")
    except Exception as e:
        print(f"❌ Error scraping BrighterMonday: {e}")
    return jobs


def scrape_myjobsinkenya(query):
    print(f"🔍 Scraping MyJobsInKenya for '{query}'")
    jobs = []
    try:
        driver = init_driver()
        search_url = f"https://www.myjobsinkenya.com/jobs?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        listings = driver.find_elements(By.CSS_SELECTOR, "div.card-body")

        for job in listings[:10]:
            try:
                title_elem = job.find_element(By.CSS_SELECTOR, "h5.card-title a")
                desc_elem = job.find_element(By.CSS_SELECTOR, "p.card-text")

                jobs.append({
                    'title': title_elem.text,
                    'link': title_elem.get_attribute('href'),
                    'description': desc_elem.text
                })
            except Exception:
                continue

        driver.quit()
        print(f"🧾 Found {len(jobs)} MJK listings")
    except Exception as e:
        print(f"❌ Error scraping MyJobsInKenya: {e}")
    return jobs
