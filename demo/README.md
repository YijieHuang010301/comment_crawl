# Comment Crawl Demo

This folder contains a static portfolio demo for the Comment Crawl project.

It is intentionally independent from the crawler runtime. The page simulates the
project workflow with representative data:

- product URL parsing
- platform detection
- Redis job payload generation
- crawl pipeline status
- normalized rating and review output

## Local preview

Open `index.html` directly in a browser, or run a tiny static server:

```bash
python3 -m http.server 4173 -d demo
```

Then visit `http://localhost:4173`.

## CloudBase deployment

Deploy the contents of this `demo/` directory as a static website.
