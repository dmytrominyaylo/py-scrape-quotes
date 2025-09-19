import csv
from dataclasses import dataclass, fields
import time
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page(page_number: int) -> bytes:
    url = urljoin(BASE_URL, f"page/{page_number}/")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.content
    except RequestException as e:
        print(f"Request failed for {url}: {e}")
        return b""


def get_all_quotes() -> list[Quote]:
    collected_quotes = []
    page = 1
    while True:
        html_content = get_page(page)
        if not html_content:
            break
        soup = BeautifulSoup(html_content, "html.parser")
        quotes_on_page = soup.select("div.quote")
        if not quotes_on_page:
            break
        for quote in quotes_on_page:
            collected_quotes.append(Quote(
                text=quote.select_one("span.text").text,
                author=quote.select_one("small.author").text,
                tags=[tag.text for tag in quote.select("div.tags a")]
            ))
        page += 1
        time.sleep(0.2)
    return collected_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
