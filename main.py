from playwright.sync_api import sync_playwright
import html

OUTPUT_HTML = "main.html"
TARGET_URL = "https://www.reddit.com"
MAX_SCROLLS = 15
ARTICLE_XPATH = "/html/body/shreddit-app/div[1]/div/div/main/shreddit-feed/article[{i}]/shreddit-post/a[1]"


def scrape_reddit():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        page.wait_for_selector("shreddit-feed article", timeout=30000)

        # Auto-scroll to load more posts
        for _ in range(MAX_SCROLLS):
            prev_count = page.locator("shreddit-feed article").count()
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            new_count = page.locator("shreddit-feed article").count()
            if new_count == prev_count:
                break

        total = page.locator("shreddit-feed article").count()
        print(f"Found {total} articles")

        # Loop through articles by index, replicating the full XPath
        for i in range(1, total + 1):
            xpath_selector = f"xpath={ARTICLE_XPATH.format(i=i)}"
            anchor = page.locator(xpath_selector).first
            if anchor.count() == 0:
                continue
            try:
                description = (anchor.text_content() or "").strip()
                href = anchor.get_attribute("href") or ""
                if not description:
                    continue
                full_link = href if href.startswith("http") else f"https://www.reddit.com{href}"
                results.append({"description": description, "link": full_link})
                print(f"[{i}] {description[:80]}")
            except Exception as e:
                print(f"Skip article {i}: {e}")

        browser.close()
    return results


def write_html(posts):
    cards = "\n".join(
        f'        <li class="post">\n'
        f'            <a href="{html.escape(p["link"])}" target="_blank" rel="noopener">'
        f'{html.escape(p["description"])}</a>\n'
        f'        </li>'
        for p in posts
    )
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>hip-hip vikas learned selenium</title>
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
        h2 {{ border-bottom: 2px solid #ff4500; padding-bottom: .5rem; }}
        .post {{ margin: .75rem 0; padding: .75rem; background: #f6f7f8; border-radius: 6px; list-style: none; }}
        .post a {{ color: #1a1a1b; text-decoration: none; font-weight: 500; }}
        .post a:hover {{ color: #ff4500; }}
        .count {{ color: #878a8c; font-size: .9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>reddit posts scapper project</h2>
        <p class="count">Scraped {len(posts)} posts from reddit.com</p>
        <ul class="posts">
{cards}
        </ul>
    </div>
</body>
</html>"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Wrote {len(posts)} posts to {OUTPUT_HTML}")


if __name__ == "__main__":
    posts = scrape_reddit()
    write_html(posts)
