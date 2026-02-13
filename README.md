# LLM Context Crawler

A high-fidelity web crawler designed to extract clean, authenticated content (like component source code) for use as LLM context. Optimized for modern, JS-heavy component libraries like Tailwind UI.

## Features

- **Authenticated Crawling:** Log in manually via a non-headless browser session.
- **Interactive Flow:** Browser opens for preparation; crawling starts only after your confirmation.
- **High-Fidelity Extraction:** Automatically drills down through layout wrappers to get raw component source code.
- **Configurable:** Define multiple crawl groups and inspection types via `config.json`.
- **Automatic Cleanup:** Resets the `output/` directory on every run to ensure fresh data.

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) with Python 3.10+
- Playwright dependencies

## Setup

1. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Activate the environment:**
   ```bash
   source venv/bin/activate
   ```

## Usage

### 1. Configure URLs
Edit `config.json` to define your targets:
```json
[
    {
        "name": "tailwindcss-llm",
        "inspect": ["iframe"],
        "urls": [
            "https://tailwindui.com/plus/ui-blocks/application-ui/elements/buttons"
        ]
    }
]
```
- **`name`**: Subfolder name inside `output/`.
- **`inspect`**: Set to `["iframe"]` to extract raw source code from component previews. Leave empty for standard markdown.

### 2. Run the Crawler
```bash
python crawler.py
```

### 3. Interactive Login
1. A browser window will open to Google.
2. Navigate to your target site (e.g., Tailwind UI) and **Log In**.
3. Once logged in and on the desired page, return to the terminal and press **ENTER**.
4. The crawler will then process all URLs in your config using your active session.

## Output Structure
```
output/
└── tailwindcss-llm/
    └── elements_buttons.md  <-- Contains clean <html> source for each component
```

## Future Agent Skills
This project serves as a template for "Identity-Based High-Fidelity Extraction". Future agents can extend this by adding new `inspect` types or using LLM extraction strategies for complex data.
