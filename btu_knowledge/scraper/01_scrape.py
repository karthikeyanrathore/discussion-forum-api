"""
01_scrape.py
Scrapes the BTU AI MSc FAQ page and all linked pages.
Saves structured Q&A data to data/processed/btu/faq_general.json

BTU page uses TYPO3 accordion structure:
  <h2>Section Title</h2>
  <div class="accordion-item">
      <a class="accordion-title" href="#c395283">Question text</a>
      <div class="accordion-content" id="c395283">
          <div class="ce-bodytext">
              ...answer content...
          </div>
      </div>
  </div>

The trick: match anchor href="#cXXX" to div id="cXXX" to get the answer.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

FAQ_URL = "https://www.b-tu.de/en/artificial-intelligence-ms/faq"

# BTU serves the first accordion item with an empty accordion-content div
# (likely a server-side bug with the pre-expanded item). We patch it manually.
# Content verified from the raw page source on 2026-04-04.
MANUAL_PATCHES = {
    "What are the admission requirements for the Artificial Intelligence study programme?": {
        "answer": (
            "The primary admissions requirement is a first qualifying degree (at least bachelor's degree) "
            "or a qualification equivalent degree in a program closely related to Artificial Intelligence (AI). "
            "A degree is considered to be closely related to AI if the topics studied as part of the bachelors "
            "degree are similar in depth and range to those taken in BTU's bachelors degree in Artificial Intelligence. "
            "The program has a strong theoretical/mathematical component. Success in our academic program requires "
            "that the bachelors degree contain a solid background in theoretical computer science, mathematics "
            "(with special focus on probability theory but also including discrete mathematics and number theory, "
            "analysis, linear algebra), machine learning, software engineering, and programming. "
            "Bachelors degrees that are often, but not always, considered to be closely related include computer "
            "science, computer engineering, or mathematics with a minor in computer science. "
            "The examination board of Artificial Intelligence at BTU will decide whether an applicant's degree "
            "is sufficiently close in terms of content. "
            "Applicants need a certificate of proficiency in English as described in the official handout."
        ),
        "linked_urls": [
            "https://www.b-tu.de/kuenstliche-intelligenz-bs",
            "https://www-docs.b-tu.de/zulassung/public/universitaere/Merkblaetter_BA_MA/Sprachnachweise/MB_Sprachnachweis_Englisch_Language_Certificate_English.pdf"
        ]
    }
}
BASE_URL = "https://www.b-tu.de"
OUTPUT_PATH = Path("data/processed/btu/faq_general.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BTU-RAG-Bot/1.0; research project)"
    )
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [ERROR] Could not fetch {url}: {e}")
        return None


def scrape_linked_page(url: str) -> str:
    """Scrape main content text from a linked BTU page."""
    print(f"    → Following link: {url}")
    soup = fetch_page(url)
    if not soup:
        return ""

    # Find the TYPO3 bodytext content area
    content = (
        soup.find("div", class_="ce-bodytext")
        or soup.find("div", class_="user-content")
        or soup.find("main")
        or soup.find("article")
    )
    if not content:
        return ""

    for tag in content.find_all(["nav", "footer", "header", "script", "style"]):
        tag.decompose()

    text = content.get_text(separator=" ", strip=True)
    return " ".join(text.split())


# ── Main extraction ───────────────────────────────────────────────────────────

def extract_faq(soup: BeautifulSoup) -> list[dict]:
    results = []

    # Each FAQ section is a btu_foundation_accordion_container
    accordion_containers = soup.find_all(
        "div", class_="frame-type-btu_foundation_accordion_container"
    )

    for container in accordion_containers:
        # Get section name from <h2> inside the container's <header>
        header = container.find("header")
        section = header.find("h2").get_text(strip=True) if header else "General"

        # Each Q&A is an accordion-item
        items = container.find_all("div", class_="accordion-item")

        for item in items:
            # Question = text of the accordion-title anchor
            title_anchor = item.find("a", class_="accordion-title")
            if not title_anchor:
                continue
            question = title_anchor.get_text(strip=True)

            # Answer = content inside accordion-content div
            content_div = item.find("div", class_="accordion-content")
            if not content_div:
                continue

            # Get all text and links from the bodytext area
            bodytext = content_div.find("div", class_="ce-bodytext")
            target = bodytext if bodytext else content_div

            # Collect linked URLs
            linked_urls = []
            for a_tag in target.find_all("a", href=True):
                href = a_tag["href"]
                if href and not href.startswith("#"):
                    full_url = href if href.startswith("http") else BASE_URL + href
                    if full_url not in linked_urls:
                        linked_urls.append(full_url)

            answer = target.get_text(separator=" ", strip=True)
            answer = " ".join(answer.split())

            # If stub answer (just "Please check this website") → scrape linked pages
            linked_content = ""
            is_stub = len(answer) < 100 and linked_urls

            if is_stub:
                scraped = []
                for url in linked_urls:
                    if "b-tu.de" in url:
                        text = scrape_linked_page(url)
                        if text:
                            scraped.append(text)
                        time.sleep(0.5)  # be polite to the server
                linked_content = " ".join(scraped)

            # Apply manual patch BEFORE appending if answer is empty
            if not answer and not linked_content and question in MANUAL_PATCHES:
                patch = MANUAL_PATCHES[question]
                answer = patch.get("answer", "")
                linked_urls = patch.get("linked_urls", linked_urls)
                print(f"  ✓ [{section}] {question[:65]}... (patched)")
            else:
                has_content = bool(answer or linked_content)
                status = "✓" if has_content else "⚠ empty"
                print(f"  {status} [{section}] {question[:65]}...")

            results.append({
                "section": section,
                "question": question,
                "answer": answer,
                "source_url": FAQ_URL,
                "linked_urls": linked_urls,
                "linked_content": linked_content,
            })

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print(f"Fetching: {FAQ_URL}\n")
    soup = fetch_page(FAQ_URL)
    if not soup:
        print("Failed to fetch page. Exiting.")
        return

    faq_data = extract_faq(soup)

    if not faq_data:
        print("No Q&A pairs extracted. Check the page structure.")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(faq_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! {len(faq_data)} Q&A pairs saved to {OUTPUT_PATH}")

    empty = [q for q in faq_data if not q["answer"] and not q["linked_content"]]
    if empty:
        print(f"⚠  {len(empty)} entries still have empty answers:")
        for q in empty:
            print(f"   - {q['question'][:70]}")


if __name__ == "__main__":
    main()