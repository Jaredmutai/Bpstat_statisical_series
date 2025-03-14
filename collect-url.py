import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_all_urls(start_url):
    driver = setup_driver()
    visited_urls = set()
    urls_to_visit = {start_url}
    base_domain = "https://bpstat.bportugal.pt"

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url in visited_urls:
            continue

        try:
            driver.get(current_url)
            time.sleep(1)  # Wait for page to load
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            visited_urls.add(current_url)
            print(f"Visited: {current_url} | Total URLs: {len(visited_urls)}")

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(base_domain, link['href'])
                # Only include URLs within the domain
                if absolute_url.startswith(base_domain) and absolute_url not in visited_urls:
                    urls_to_visit.add(absolute_url)

            # Basic stopping condition (remove/adjust as needed)
            if len(visited_urls) >= 250000:  # Slightly above 200k to ensure coverage
                break

        except Exception as e:
            print(f"Error accessing {current_url}: {e}")
            continue

    driver.quit()
    return visited_urls

def save_to_csv(urls, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])
        for url in urls:
            writer.writerow([url])

if __name__ == "__main__":
    start_url = "https://bpstat.bportugal.pt/"
    all_urls = get_all_urls(start_url)
    save_to_csv(all_urls, "bpstat_all_urls.csv")
    print(f"Found and saved {len(all_urls)} URLs to bpstat_all_urls.csv")