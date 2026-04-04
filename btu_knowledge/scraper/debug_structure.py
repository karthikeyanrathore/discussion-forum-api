"""
debug_structure.py
Run this to print the actual HTML structure of the BTU FAQ page.
This tells us exactly how to fix the scraper.

Usage: python debug_structure.py
"""

import requests
from bs4 import BeautifulSoup

FAQ_URL = "https://www.b-tu.de/en/artificial-intelligence-ms/faq"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BTU-RAG-Bot/1.0)"}

response = requests.get(FAQ_URL, headers=HEADERS, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

print("=" * 60)
print("1) ALL <h2> tags on the page:")
print("=" * 60)
for h2 in soup.find_all("h2"):
    print(f"  <h2> → '{h2.get_text(strip=True)[:80]}'")

print()
print("=" * 60)
print("2) ALL <a> tags whose href starts with #c (question anchors):")
print("=" * 60)
for a in soup.find_all("a", href=lambda h: h and h.startswith("#c")):
    print(f"  <a href='{a['href']}'> → '{a.get_text(strip=True)[:80]}'")

print()
print("=" * 60)
print("3) RAW HTML around the FIRST question anchor (50 lines):")
print("=" * 60)
first_anchor = soup.find("a", href=lambda h: h and h.startswith("#c"))
if first_anchor:
    # Print the parent and its siblings to understand the structure
    parent = first_anchor.parent
    print(f"  Parent tag: <{parent.name} class='{parent.get('class', '')}'>")
    print()
    print("  Parent HTML (first 2000 chars):")
    print(str(parent)[:2000])
else:
    print("  No #c anchors found at all!")

print()
print("=" * 60)
print("4) What tags are DIRECT CHILDREN of <main> or <body>?")
print("=" * 60)
main = soup.find("main") or soup.find("body")
if main:
    for child in list(main.children)[:30]:
        if hasattr(child, 'name') and child.name:
            cls = child.get('class', '')
            text_preview = child.get_text(strip=True)[:60]
            print(f"  <{child.name} class='{cls}'> → '{text_preview}'")

print()
print("=" * 60)
print("5) Save full HTML for manual inspection:")
print("=" * 60)
with open("btu_faq_raw.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("  Saved to btu_faq_raw.html — open in browser to inspect")