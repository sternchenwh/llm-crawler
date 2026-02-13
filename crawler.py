import asyncio
import os
import json
import re
import html
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.async_logger import AsyncLogger
from colorama import Fore, Style, init

# Initialize colorama
init()

# Create a shared logger instance
logger = AsyncLogger(verbose=True)

def extract_innermost_component(srcdoc_html):
    """Parse the srcdoc and drill down to the actual component source code"""
    if not srcdoc_html:
        return ""
    
    # srcdoc often contains HTML-escaped content like &lt;!doctype html&gt;
    # We unescape it first to get real HTML
    unescaped = html.unescape(srcdoc_html)
    
    soup = BeautifulSoup(unescaped, 'lxml')
    
    # 1. Remove all noise
    for noise in soup.find_all(['script', 'style', 'link', 'meta', 'noscript', 'head']):
        noise.decompose()
    
    # 2. Get the body
    body = soup.body
    if not body:
        return ""
    
    # 3. Drill down through Tailwind UI layout wrappers
    # These are usually single-child divs with background/padding/mx-auto classes
    current = body
    while len(current.find_all(recursive=False)) == 1 and current.find(recursive=False).name == 'div':
        child = current.find(recursive=False)
        classes = " ".join(child.get('class', [])).lower()
        # If it looks like a wrapper, dive in
        if any(cls in classes for cls in ['bg-', 'p-', 'mx-auto', 'flex']):
            current = child
        else:
            break
            
    # Return the inner content which contains the real components (buttons, etc.)
    return current.decode_contents().strip()

async def crawl_url(crawler, url, output_dir, inspect_options=None):
    """Crawl URL and use BeautifulSoup to extract component source from iframes"""
    logger.info(f"Crawling {Fore.CYAN}{url}{Style.RESET_ALL}", tag="CRAWL")
    
    run_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="networkidle",
        delay_before_return_html=5.0, # Wait for iframes to fully populate
        word_count_threshold=0,
        remove_overlay_elements=True,
        process_iframes=False # Don't turn them into text
    )

    result = await crawler.arun(url, config=run_config)

    if result.success:
        safe_name = url.split("//")[-1].replace("/", "_").replace(".", "_").replace(":", "_").strip("_")
        filepath = os.path.join(output_dir, f"{safe_name}.md")
        
        # Use result.html which is the raw rendered HTML of the main page
        soup = BeautifulSoup(result.html, 'lxml')
        
        # Build the Markdown
        markdown_content = f"# Documentation for {url}\n\n"
        extracted_any = False
        
        # Find all iframes that have a srcdoc (TUI components)
        iframes = soup.find_all('iframe')
        
        for index, iframe in enumerate(iframes):
            src_doc = iframe.get('srcdoc')
            if not src_doc:
                continue
                
            # Find a title: look for the closest section's h2
            section = iframe.find_parent('section')
            title = "Component"
            if section:
                h2 = section.find('h2')
                if h2:
                    title = h2.get_text(strip=True)
                elif section.get('id'):
                    title = section.get('id')
            
            if title == "Component":
                title = f"Component {index + 1}"
                
            # Extract and clean
            component_code = extract_innermost_component(src_doc)
            
            if component_code:
                markdown_content += f"## {title}\n"
                markdown_content += "```html\n"
                markdown_content += component_code
                markdown_content += "\n```\n\n"
                extracted_any = True

        if not extracted_any:
            logger.warning(f"Python parsing failed to find components for {url}. Saving default markdown.", tag="CRAWL")
            markdown_content += result.markdown

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        logger.success(f"Saved: {filepath} ({len(markdown_content)} bytes)", tag="CRAWL")
        return True
    else:
        logger.error(f"Failed {url}: {result.error_message}", tag="CRAWL")
        return False

async def main():
    logger.info(f"{Fore.CYAN}LLM Context Crawler (Python Source Extractor){Style.RESET_ALL}", tag="DEMO")
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    browser_config = BrowserConfig(
        headless=False,
        use_managed_browser=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        logger.info(f"\n{Fore.YELLOW}STEP 1: BROWSER PREPARATION{Style.RESET_ALL}", tag="SETUP")
        logger.info("A browser window will open. Navigate to Tailwind UI and LOGIN.")
        
        await crawler.arun("https://www.google.com")
        
        print(f"\n{Fore.GREEN}--> ACTION REQUIRED:{Style.RESET_ALL}")
        print(f"1. Log in to Tailwind UI in the opened browser.")
        print(f"2. Navigate to the component category.")
        print(f"3. Press ENTER in this terminal.")
        input(f"{Fore.CYAN}Press [ENTER] to extract source code using Python BeautifulSoup...{Style.RESET_ALL}")

        logger.info(f"\n{Fore.YELLOW}STEP 2: EXTRACTION{Style.RESET_ALL}", tag="CRAWL")
        
        for group in config_data:
            group_name = group.get("name", "default")
            urls = group.get("urls", [])
            inspect_options = group.get("inspect", [])
            
            logger.info(f"Processing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}", tag="GROUP")
            group_dir = os.path.join("output", group_name)
            os.makedirs(group_dir, exist_ok=True)
            
            for url in urls:
                await crawl_url(crawler, url, group_dir, inspect_options)

    logger.success("\nAll tasks completed!", tag="FINISH")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user", tag="EXIT")
    except Exception as e:
        logger.error(f"Error: {str(e)}", tag="ERROR")
