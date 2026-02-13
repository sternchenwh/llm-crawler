---
name: llm-context-crawler
description: High-fidelity authenticated web crawling for LLM context extraction. Use when you need to extract clean source code or structured data from protected websites (like Tailwind UI) that require manual login and interactive sessions.
---

# LLM Context Crawler

This skill provides a workflow for extracting high-fidelity Markdown context from authenticated websites, specifically focusing on capturing raw source code from embedded components (iframes).

## Workflow

1. **Setup Environment**: Ensure Python 3.10+, Playwright, and BeautifulSoup4 are installed.
2. **Configuration**: Use `config.json` to define crawl groups. Set `"inspect": ["iframe"]` for component libraries.
3. **Interactive Session**:
   - Open a non-headless browser.
   - Navigate to the target site and perform manual login.
   - Confirm readiness in the terminal to proceed.
4. **Extraction**:
   - Crawl targets using the authenticated session.
   - Use Python BeautifulSoup to extract `srcdoc` from iframes.
   - Drill down through layout wrappers to find the innermost component HTML.
5. **Context Generation**: Save clean Markdown files to the `output/` directory, organized by group.

## Best Practices

- **Manual Login**: Always use non-headless mode for the initial browser launch to handle 2FA or complex auth flows.
- **Drill-Down Logic**: TUI and similar libraries wrap components in many layout divs. Always inspect the structure and adjust the drill-down logic if extraction returns empty results.
- **Wait for Network**: Use `wait_until: "networkidle"` and significant delays (5s+) for JS-heavy documentation.
- **Raw HTML**: For LLM context, raw HTML snippets are often better than processed text for technical documentation.

## Troubleshooting

- **Empty Output**: Verify that `srcdoc` is populated. Some sites load iframes lazily; increase `delay_before_return_html`.
- **Boilerplate Bloat**: Decompose `script`, `style`, and `meta` tags within the `srcdoc` parser.
