# South River Blog - GitHub Pages

A GitHub Pages site

# Build with
poetry install
# download posts
python scripts/download_post.py

## Setup for GitHub Pages

1. Push this repository to GitHub
2. Go to your repository settings
3. Navigate to "Pages" in the sidebar
4. Under "Source", select the branch (usually `main` or `master`)
5. Click "Save"
6. Your site will be available at `https://[your-username].github.io/[repository-name]/`

# push
git commit --allow-empty -m "force pages rebuild"
git push


## Local Development

Simply open `index.html` in your web browser, or use a local server:

```bash
# Using Python
python -m http.server 8000
```

Then navigate to `http://localhost:8000` in your browser.
