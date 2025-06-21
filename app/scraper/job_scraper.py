import requests
from bs4 import BeautifulSoup

def scrape_jobs_brightermonday(query="credit", location="kenya", max_results=10):
    """
    Scrapes BrighterMonday Kenya job listings.
    Returns a list of dicts with 'title', 'company', 'description', 'link'
    """
    jobs = []
    base_url = "https://www.brightermonday.co.ke/jobs"
    params = {"q": query, "location": location}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("div", class_="search-result__job", limit=max_results)

        for listing in listings:
            title_tag = listing.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            link_tag = title_tag.find("a") if title_tag else None
            link = "https://www.brightermonday.co.ke" + link_tag["href"] if link_tag else "#"

            company_tag = listing.find("a", class_="company")
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"

            desc_tag = listing.find("p", class_="job-description")
            description = desc_tag.get_text(strip=True) if desc_tag else "No description provided"

            jobs.append({
                "title": title,
                "company": company,
                "description": description,
                "link": link
            })

    except Exception as e:
        print(f"Error scraping BrighterMonday: {e}")

    return jobs
