name: Auto Fix SEO on New Blog Post

on:
  push:
    branches:
      - main
    paths:
      - 'blog/**.html'   # triggers ONLY when a file in /blog/ is added or changed
      - '**.html'        # also triggers for root HTML files

jobs:
  auto-fix-seo:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0   # fetch full history so we can detect changed files

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install beautifulsoup4

      - name: Get changed HTML files
        id: changed
        run: |
          # Get list of HTML files that were added or modified in this push
          CHANGED=$(git diff --name-only HEAD~1 HEAD -- '*.html' 'blog/*.html' | tr '\n' ' ')
          echo "files=$CHANGED" >> $GITHUB_OUTPUT
          echo "Changed files: $CHANGED"

      - name: Run SEO fix on changed files only
        run: python fix_all_blogs.py --files "${{ steps.changed.outputs.files }}"

      - name: Commit and push fixes
        run: |
          git config user.name "NeuraPulse SEO Bot"
          git config user.email "seo-bot@neuraplus-ai.github.io"
          git add .
          git diff-index --quiet HEAD || git commit -m "🤖 Auto-fix SEO for new/updated blog posts"
          git push
