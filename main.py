from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://reddit.com")
    
    # Scroll down to load multiple posts dynamically
    for _ in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2) # Wait for dynamic posts to inject
        
    # Scrape all posts using reliable X data-testids
    posts = page.locator('[data-testid="post-container"]').all()
    
    for post in posts:
        # Extract the title text using a CSS sub-selector
        title = post.locator('h3').text_content() if post.locator('h3').is_visible() else "No Title"
        print(f"Post Title: {title}")
        
    browser.close()