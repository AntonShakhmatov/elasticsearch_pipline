from bs4 import BeautifulSoup
import re

def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "No title"
    text = soup.get_text(separator=" ", strip=True)
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phones = re.findall(r'\+?\d[\d\s-]{7,}', text)
    links = []

    for a in soup.find_all("a", href=True):
        links.append(a["href"])

        return {
            "title": title,
            "text": text[:5000],
            "emails": email,
            "phones": phones,
            "links": links[:50]
        }