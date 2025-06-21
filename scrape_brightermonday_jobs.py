from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def scrape_brightermonday_jobs(query=None, max_jobs=10):
    # Configure headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    base_url = "https://www.brightermonday.co.ke/jobs"
    if query:
        search_term = query.replace(' ', '+')
        url = f"{base_url}?search={search_term}"
    else:
        url = base_url

    driver.get(url)
    time.sleep(3)  # wait for JavaScript to load

    jobs = []

    job_cards = driver.find_elements(By.CLASS_NAME, 'job-card')[:max_jobs]
    for card in job_cards:
        try:
            title_element = card.find_element(By.CLASS_NAME, 'job-card-title')
            title = title_element.text.strip()
            link = title_element.find_element(By.TAG_NAME, 'a').get_attribute('href')

            company = card.find_element(By.CLASS_NAME, 'company-name').text.strip()
            location = card.find_element(By.CLASS_NAME, 'job-location').text.strip()
            summary = card.find_element(By.CLASS_NAME, 'job-snippet').text.strip()

            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'summary': summary,
                'link': link
            })
        except Exception as e:
            print("Error scraping a job card:", e)
            continue

    driver.quit()
    return jobs
