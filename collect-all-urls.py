import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_urls_and_links(start_url):
    driver = setup_driver()
    visited_urls = set()
    urls_to_visit = {start_url}
    base_domain = "https://bpstat.bportugal.pt"
    url_connections = []  # List to store [source_url, linked_url] pairs

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
            page_links = set()
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(base_domain, link['href'])
                if absolute_url.startswith(base_domain):
                    page_links.add(absolute_url)
                    if absolute_url != current_url:  # Avoid self-references
                        url_connections.append([current_url, absolute_url])
                    if absolute_url not in visited_urls:
                        urls_to_visit.add(absolute_url)

            # Stopping condition
            if len(visited_urls) >= 250000:
                break

        except Exception as e:
            print(f"Error accessing {current_url}: {e}")
            continue

    driver.quit()
    return visited_urls, url_connections

def save_urls_to_csv(urls, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])
        for url in urls:
            writer.writerow([url])

def save_connections_to_csv(connections, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Source_URL', 'Linked_URL'])
        for connection in connections:
            writer.writerow(connection)

if __name__ == "__main__":
    start_url = "https://bpstat.bportugal.pt/"
    all_urls, url_connections = get_urls_and_links(start_url)
    
    save_urls_to_csv(all_urls, "bpstat_all_urls.csv")
    save_connections_to_csv(url_connections, "bpstat_url_connections.csv")
    
    print(f"Saved {len(all_urls)} URLs to bpstat_all_urls.csv")
    print(f"Saved {len(url_connections)} connections to bpstat_url_connections.csv")