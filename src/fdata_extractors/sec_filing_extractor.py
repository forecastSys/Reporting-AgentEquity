from src.fdata_extractors.utils import extract_items
from src.abstractions import TextDataABC
import os
import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# SEC requires a descriptive User-Agent
USER_AGENT = os.getenv("SEC_USER_AGENT", "My Name <my.email@example.com>")
HEADERS = {"User-Agent": USER_AGENT}
BASE_URL = "https://www.sec.gov"

class SecFilingExtractor(TextDataABC):

    def fetch(self, ticker: str, form_type: str = "10-K") -> list[str]:
        """
        Return a list of text contents for all SEC filings of a given form and year.

        Args:
            cik (str): Company CIK or ticker.
            year (int): Filing year, e.g. 2024.
            form_type (str): e.g. "10-K", "8-K", etc.

        Returns:
            List of raw text strings (header + body) for each matching filing.
        """
        # 1. Fetch the RSS/Atom feed
        feed_url = (
            f"{BASE_URL}/cgi-bin/browse-edgar"
            f"?action=getcompany&CIK={ticker}"
            f"&type={form_type}&owner=exclude&count=100&output=atom"
        )
        resp = requests.get(feed_url, headers=HEADERS)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        latest_year = 2000
        for entry in feed.entries:
            # 2. Parse the entry date and filter by year
            entry_dt = datetime.strptime(entry['filing-date'], "%Y-%m-%d")
            if entry_dt.year > latest_year:
                latest_year = entry_dt.year

        results = []
        for entry in feed.entries:
            # 2. Parse the entry date and filter by year
            entry_dt = datetime.strptime(entry['filing-date'], "%Y-%m-%d")
            if entry_dt.year != latest_year:
                continue

            # 3. Load the filing detail page
            filing_page = requests.get(entry.link, headers=HEADERS)
            filing_page.raise_for_status()
            soup = BeautifulSoup(filing_page.content, "html.parser")

            # 4. Find the TXT document link in the “Document Format Files” table
            doc_table = soup.find(
                "table", {"summary": "Document Format Files"}
            )
            if not doc_table:
                continue

            for row in doc_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 4 and cols[3].get_text(strip=True) == form_type:
                    link_tag = cols[2].find("a", href=True)
                    if link_tag and link_tag["href"].endswith(".htm"):
                        htm_href = BASE_URL + link_tag["href"]
                        htm_href = htm_href.replace('/ix?doc=', '')
                        break

            if not htm_href:
                continue

            html_ = requests.get(htm_href, headers=HEADERS)

            items_output = extract_items(html_.text)
            # bsObj = BeautifulSoup(html_.text, 'html.parser')
            #
            # text = bsObj.find('body').get_text(separator="\n")
            #
            # # Clean up the text by removing excessive whitespace and non-breaking spaces
            # text = re.sub(r'\s{10,}', '\n', text)
            # text = re.sub(r'\s{10,}', '\n', text)
            #
            # # Find index that start with Form 10k, so that useless contents are ignored
            # regex = re.compile(r'Form\s*\n*{0}'.format(form_type), re.IGNORECASE)
            # matches = regex.finditer(text.lower())
            # for match in matches:
            #     start = match.start()
            #     break
            # text = text[start:]
            #
            # text = text.replace('\xa0', '')
            # text = re.sub(r'(\n){2,}', '\n', text)
            # text = re.sub(r'(\xa0\n){3,}', '\n', text)
            # ## Text
            # text_final = text + "\n\n"
            if items_output:
                break
        return items_output

if __name__ == "__main__":
    # Example usage:
    cik = "AAPL"  # or full CIK like "0000320193"
    year = 2025
    form = "10-K"

    filings = fetch_sec_filings_text(cik, form)
    print(filings)
