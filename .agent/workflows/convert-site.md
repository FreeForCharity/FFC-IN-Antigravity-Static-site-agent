---
description: Convert a website to a static GitHub repository automatically.
---

This workflow identifies a website's type (WordPress, Generic HTML, etc.), scrapes it into static files (HTML, CSS, JS, images), creates a new GitHub repository, and pushes the static site to that repository.

### Requirements
- Node.js and Python 3 installed.
- A GitHub Personal Access Token (PAT) with `repo` scope.
- `requests` python library (`pip install requests`)
- `website-scraper`, `axios`, and `cheerio` npm packages.

### Usage

1. **Run the Conversion**:
   Provide the URL of the site to scrape and the name for the new GitHub repository.

   // turbo
   ```bash
   # Variables
   SITE_URL="https://example.com"
   REPO_NAME="my-static-site"
   TEMP_DIR="./temp_scraped_site"

   # 1. Identify and Scrape
   node ./scripts/identify_and_scrape.js "$SITE_URL" "$TEMP_DIR"

   # 2. Automated Repair (Layout & Videos)
   node ./scripts/repair_site.js "$TEMP_DIR"

   # 3. Push to GitHub (Automatically uses credentials if available)
   python3 ./scripts/github_push.py "$TEMP_DIR" "$REPO_NAME"
   ```

2. **Automated Verification**:
   The workflow should now trigger a browser check to confirm the deployment.
   ```bash
   # Verify the live site
   # (The assistant will automatically navigate to the Pages URL and report status)
   ```
