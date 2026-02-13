import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.async_logger import AsyncLogger
from colorama import Fore, Style, init

# Initialize colorama
init()

# Create a shared logger instance
logger = AsyncLogger(verbose=True)

async def crawl_url(crawler, url, output_dir):
    """Crawl a single URL and save to output_dir"""
    logger.info(f"Crawling {Fore.CYAN}{url}{Style.RESET_ALL}", tag="CRAWL")
    
    run_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_for="networkidle",
        delay_before_return_secs=2, 
        word_count_threshold=0,
        remove_overlay_elements=True,
        process_iframes=True,
        excluded_tags=[],
        exclude_external_links=False
    )

    result = await crawler.arun(url, config=run_config)

    if result.success:
        safe_name = url.split("//")[-1].replace("/", "_").replace(".", "_").strip("_")
        filepath = os.path.join(output_dir, f"{safe_name}.md")
        
        content = result.markdown
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.success(f"Saved: {filepath} ({len(content)} bytes)", tag="CRAWL")
        return True
    else:
        logger.error(f"Failed {url}: {result.error_message}", tag="CRAWL")
        return False

async def main():
    logger.info(f"{Fore.CYAN}LLM Context Crawler (Interactive Mode){Style.RESET_ALL}", tag="DEMO")
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    # Use a managed browser but without a persistent user_data_dir for a fresh session
    browser_config = BrowserConfig(
        headless=False,
        use_managed_browser=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Step 1: Open browser for user to login
        logger.info(f"\n{Fore.YELLOW}STEP 1: LOGIN{Style.RESET_ALL}", tag="SETUP")
        logger.info("A browser window will open. Please navigate to the site and login.")
        
        # Navigate to a logical starting point (e.g., the first URL in config or a login page)
        initial_url = "https://tailwindui.com/login"
        await crawler.arun(initial_url)
        
        print(f"\n{Fore.GREEN}--> ACTION REQUIRED:{Style.RESET_ALL}")
        print(f"1. Use the opened browser to log in to your account.")
        print(f"2. Once you have logged in and reached the content, come back here.")
        input(f"{Fore.CYAN}Press [ENTER] to start crawling all URLs from config...{Style.RESET_ALL}")

        # Step 2: Proceed with crawling
        logger.info(f"\n{Fore.YELLOW}STEP 2: CRAWLING{Style.RESET_ALL}", tag="CRAWL")
        
        for group in config_data:
            group_name = group.get("name", "default")
            urls = group.get("urls", [])
            
            logger.info(f"Processing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}", tag="GROUP")
            group_dir = os.path.join("output", group_name)
            os.makedirs(group_dir, exist_ok=True)
            
            for url in urls:
                await crawl_url(crawler, url, group_dir)

    logger.success("\nAll tasks completed!", tag="FINISH")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user", tag="EXIT")
    except Exception as e:
        logger.error(f"Error: {str(e)}", tag="ERROR")
