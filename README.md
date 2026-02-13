# LLM Context Crawler

This project uses [Crawl4AI](https://github.com/unclecode/crawl4ai) to crawl authenticated websites and generate Markdown files optimized for LLMs. It supports identity-based browsing, allowing you to login once and crawl protected content.

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) installed on your system.
- Python 3.10 or higher (managed by pyenv).

## Setup Instructions

1. **Clone or enter the project directory:**
   ```bash
   cd llm-crawler
   ```

2. **Run the setup script:**
   This script will create a virtual environment, install dependencies, and setup Playwright.
   ```bash
   ./setup.sh
   ```

3. **Activate the environment:**
   ```bash
   source venv/bin/activate
   ```

## Usage

### 1. Configure your URLs
Create or edit `config.json` with the sites you want to crawl:
```json
[
    {
        "name": "tailwindcss-llm",
        "urls": [
            "https://tailwindui.com/plus/components/marketing/sections/heroes",
            "https://tailwindui.com/plus/components/application-ui/elements/buttons"
        ]
    }
]
```

### 2. Run the Crawler
```bash
python crawler.py
```
- The script will ask for your browser profile.
- It will then ask for the config file path (default is `config.json`).
- Files will be generated inside `output/{group-name}/`.

## Output Structure
```
output/
├── tailwindcss-llm/
│   ├── tailwindui_com_plus_components_marketing_sections_heroes.md
│   └── ...
└── another-site-llm/
    └── ...
```

## Troubleshooting

- **Headless Mode:** If you want to run completely in the background after setup, you can change `headless=False` to `headless=True` in `crawler.py`. However, for initial login, it MUST be `False`.
- **Browser Issues:** If the browser doesn't open, ensure `playwright install chromium` was successful.
