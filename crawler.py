import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.browser_profiler import BrowserProfiler
from crawl4ai.async_logger import AsyncLogger
from colorama import Fore, Style, init

# Initialize colorama
init()

# Create a shared logger instance
logger = AsyncLogger(verbose=True)

# Create a shared BrowserProfiler instance
profiler = BrowserProfiler(logger=logger)

async def crawl_url(crawler, url, output_dir):
    """Crawl a single URL and save to output_dir"""
    logger.info(f"Crawling {Fore.CYAN}{url}{Style.RESET_ALL}", tag="CRAWL")
    
    run_config = CrawlerRunConfig(
        cache_mode="bypass",
        word_count_threshold=10,
        remove_overlay_elements=True,
        process_iframes=True
    )

    result = await crawler.arun(url, config=run_config)

    if result.success:
        # Generate filename from URL
        safe_name = url.split("//")[-1].replace("/", "_").replace(".", "_").strip("_")
        filepath = os.path.join(output_dir, f"{safe_name}.md")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        logger.success(f"Saved: {filepath}", tag="CRAWL")
        return True
    else:
        logger.error(f"Failed {url}: {result.error_message}", tag="CRAWL")
        return False

async def process_config(profile_path, config_path):
    """Read JSON config and process all groups"""
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    browser_config = BrowserConfig(
        headless=False,
        use_managed_browser=True,
        user_data_dir=profile_path
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for group in config_data:
            group_name = group.get("name", "default")
            urls = group.get("urls", [])
            
            logger.info(f"\nProcessing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}", tag="GROUP")
            
            # Create directory for this group
            group_dir = os.path.join("output", group_name)
            os.makedirs(group_dir, exist_ok=True)
            
            for url in urls:
                await crawl_url(crawler, url, group_dir)

async def main():
    logger.info(f"{Fore.CYAN}LLM Context Crawler (Authenticated Markdown Generator){Style.RESET_ALL}", tag="DEMO")
    
    profiles = profiler.list_profiles()
    
    if not profiles:
        logger.info("No profile found. Creating one. PLEASE LOGIN when the browser opens to the target site.", tag="SETUP")
        profile_path = await profiler.create_profile()
    else:
        logger.info("Available profiles:", tag="SETUP")
        for i, p in enumerate(profiles):
            logger.info(f"[{i}] {p['name']}", tag="SETUP")
        
        choice = input(f"{Fore.CYAN}Choose profile [0]: {Style.RESET_ALL}") or "0"
        profile_path = profiles[int(choice)]["path"]

    config_path = input(f"{Fore.CYAN}Enter config JSON path [config.json]: {Style.RESET_ALL}") or "config.json"
    
    await process_config(profile_path, config_path)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user", tag="EXIT")
    except Exception as e:
        logger.error(f"Error: {str(e)}", tag="ERROR")
