import requests
import logging
import sqlite3
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from contextlib import closing

# Set up logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set up SQLite database
conn = sqlite3.connect("leads.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
                    link TEXT UNIQUE,
                    score INTEGER)''')
conn.commit()

# User-Agent
ua = UserAgent()

# Lead Scoring Function
def score_lead(title):
    keywords = {"luxury": 5, "high-end": 5, "exclusive": 5, "premium": 5, "professional": 4}
    score = sum([keywords[word] for word in keywords if word in title.lower()])
    return score

# Store Leads
def store_lead(title, link):
    try:
        score = score_lead(title)
        with closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO leads (title, link, score) VALUES (?, ?, ?)", (title, link, score))
            conn.commit()
    except sqlite3.IntegrityError:
        logging.warning(f"Duplicate entry skipped: {title}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

# Scraping Function
def scrape_site(url, platform):
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else f"{platform} Lead"
            # Filter for high-paying clients
            if any(word in title.lower() for word in ["luxury", "high-end", "exclusive", "premium"]):
                store_lead(title, url)
    except Exception as e:
        logging.error(f"Error scraping {platform}: {e}")

# Automate Scraping
def automate_scraper():
    logging.info("Starting scraper execution...")
    urls = [
        ("https://www.reddit.com/r/freelance/search.json?q=premium+piano+lessons&restrict_sr=1", "Reddit"),
        ("https://twitter.com/search?q=high-end+piano+teacher&f=live", "Twitter"),
        ("https://www.linkedin.com/jobs/search/?keywords=exclusive+piano+lessons", "LinkedIn"),
        ("https://www.upwork.com/ab/profiles/search/?q=luxury+piano+teacher", "Upwork")
    ]
    for url, platform in urls:
        scrape_site(url, platform)
    logging.info("Scraper execution finished.")

# Run the Scraper
if __name__ == "__main__":
    logging.info("Running Lead Scraper...")
    while True:
        automate_scraper()
        time.sleep(6 * 60 * 60)  # Run every 6 hours