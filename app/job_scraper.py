from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_brightermonday(search_term):
    url = f"https://www.brightermonday.co.ke/jobs?q={search_term.replace(' ', '+')}"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    job_cards = soup.select("article.search-result")
    jobs = []

    for card in job_cards:
        title_el = card.select_one("h3 a")
        company_el = card.select_one("div.company")
        location_el = card.select_one("span.location")
        summary_el = card.select_one("p")

        if title_el:
            job = {
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "location": location_el.get_text(strip=True) if location_el else "",
                "summary": summary_el.get_text(strip=True) if summary_el else "",
                "link": title_el['href']
            }
            jobs.append(job)

    driver.quit()
    print(f"BrighterMonday: {len(jobs)} jobs found")
    return jobs

def scrape_myjobsinkenya(search_term):
    url = f"https://www.myjobsinkenya.com/jobs?q={search_term.replace(' ', '+')}"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    job_cards = soup.select("div.job-item")
    jobs = []

    for card in job_cards:
        title_el = card.select_one("h3 a")
        company_el = card.select_one(".company")
        location_el = card.select_one(".location")
        summary_el = card.select_one(".description")

        if title_el:
            job = {
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "location": location_el.get_text(strip=True) if location_el else "",
                "summary": summary_el.get_text(strip=True) if summary_el else "",
                "link": title_el['href']
            }
            jobs.append(job)

    driver.quit()
    print(f"MyJobsInKenya: {len(jobs)} jobs found")
    return jobs

def scrape_all_jobs(search_term):
    jobs = []
    try:
        bm_jobs = scrape_brightermonday(search_term)
        mj_jobs = scrape_myjobsinkenya(search_term)
        jobs += bm_jobs + mj_jobs
    except Exception as e:
        print(f"Scraping error: {e}")
    return jobs
