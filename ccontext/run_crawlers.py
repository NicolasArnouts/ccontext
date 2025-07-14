import argparse
import asyncio
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from colorama import Fore, Style

# Global variable to store Windows browser path
WINDOWS_BROWSER_PATH = None


# Load configuration data from config.json
def load_config_data(config_file):
    with open(config_file, "r") as file:
        return json.load(file)


def find_windows_browser():
    """Find a Windows browser to use with Playwright in WSL."""
    possible_chrome_paths = [
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe",
        "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    ]

    for path in possible_chrome_paths:
        if os.path.exists(path):
            # Convert WSL path to Windows path for proper execution
            windows_path = subprocess.run(
                ["wslpath", "-w", path],
                capture_output=True,
                text=True,
                check=False
            ).stdout.strip()
            if windows_path:
                return windows_path
            return path

    return None


def install_playwright_dependencies():
    """Install required system dependencies for Playwright on Linux."""
    try:
        print(
            f"{Fore.YELLOW}Installing required system dependencies for Playwright...{Style.RESET_ALL}"
        )

        # Try to detect the Linux distribution
        if os.path.exists("/etc/debian_version") or os.path.exists(
            "/etc/ubuntu_version"
        ):
            # Debian/Ubuntu - first update
            print(f"{Fore.CYAN}Updating package lists...{Style.RESET_ALL}")
            update_cmd = ["sudo", "apt-get", "update", "-y"]
            update_result = subprocess.run(
                update_cmd, check=False, capture_output=True, text=True
            )

            if update_result.returncode != 0:
                print(
                    f"{Fore.YELLOW}Warning: apt-get update failed, but continuing with installation{Style.RESET_ALL}"
                )

            # Now install dependencies
            dependencies_cmd = [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "libnss3",
                "libnspr4",
                "libatk1.0-0",
                "libatk-bridge2.0-0",
                "libcups2",
                "libdrm2",
                "libdbus-1-3",
                "libxkbcommon0",
                "libxcomposite1",
                "libxdamage1",
                "libxfixes3",
                "libxrandr2",
                "libgbm1",
                "libasound2",
                "libatspi2.0-0",
                "libwayland-client0",
            ]
        elif os.path.exists("/etc/fedora-release") or os.path.exists(
            "/etc/redhat-release"
        ):
            # Fedora/RHEL/CentOS
            dependencies_cmd = [
                "sudo",
                "dnf",
                "install",
                "-y",
                "nss",
                "nspr",
                "atk",
                "at-spi2-atk",
                "cups",
                "drm",
                "dbus",
                "xkbcommon",
                "libXcomposite",
                "libXdamage",
                "libXfixes",
                "libXrandr",
                "gbm",
                "alsa-lib",
                "at-spi2-core",
                "wayland-client",
            ]
        else:
            # Run the playwright's own dependency installation
            print(
                f"{Fore.YELLOW}Using Playwright's built-in dependency installation...{Style.RESET_ALL}"
            )
            dependencies_cmd = [
                sys.executable,
                "-m",
                "playwright",
                "install-deps",
                "chromium",
            ]

        # Run the command
        print(f"{Fore.CYAN}Running: {' '.join(dependencies_cmd)}{Style.RESET_ALL}")
        result = subprocess.run(
            dependencies_cmd,
            check=False,  # Don't raise exception on error
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(
                f"{Fore.GREEN}Successfully installed system dependencies{Style.RESET_ALL}"
            )
            return True
        else:
            print(
                f"{Fore.RED}Failed to install dependencies with command: {' '.join(dependencies_cmd)}{Style.RESET_ALL}"
            )
            print(f"{Fore.RED}Error: {result.stderr}{Style.RESET_ALL}")

            # Try the playwright built-in dependency installer as a fallback
            print(
                f"{Fore.YELLOW}Trying Playwright's built-in dependency installation as fallback...{Style.RESET_ALL}"
            )
            fallback_cmd = [
                sys.executable,
                "-m",
                "playwright",
                "install-deps",
                "chromium",
            ]
            print(f"{Fore.CYAN}Running: {' '.join(fallback_cmd)}{Style.RESET_ALL}")

            fallback_result = subprocess.run(
                fallback_cmd, check=False, capture_output=True, text=True
            )

            if fallback_result.returncode == 0:
                print(
                    f"{Fore.GREEN}Successfully installed system dependencies with fallback method{Style.RESET_ALL}"
                )
                return True
            else:
                print(
                    f"{Fore.RED}Failed to install dependencies with fallback method: {fallback_result.stderr}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}You may need to manually install the required dependencies.{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}For Ubuntu/Debian: sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libatspi2.0-0 libwayland-client0{Style.RESET_ALL}"
                )
                return False

    except Exception as e:
        print(f"{Fore.RED}Error installing dependencies: {str(e)}{Style.RESET_ALL}")
        return False


def check_crawl4ai_installed():
    """Check if crawl4ai is installed and install if necessary."""
    global WINDOWS_BROWSER_PATH

    try:
        import crawl4ai

        print(f"{Fore.GREEN}crawl4ai is already installed.{Style.RESET_ALL}")

        # Even if crawl4ai is installed, we should check for system dependencies
        # Check if running in WSL
        is_wsl = "microsoft-standard" in os.uname().release.lower()

        if is_wsl:
            # Check if we already have the required system packages
            try:
                # Try to install libnss3 and other essential dependencies directly
                print(
                    f"{Fore.YELLOW}Installing required system dependencies for Playwright in WSL...{Style.RESET_ALL}"
                )

                # Direct installation of the most critical packages
                subprocess.run(
                    ["sudo", "apt-get", "update", "-y"],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                # Install the minimum required dependencies for Chromium
                install_result = subprocess.run(
                    [
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "libnss3",
                        "libnspr4",
                        "libatk1.0-0",
                        "libatk-bridge2.0-0",
                        "libcups2",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                if install_result.returncode == 0:
                    print(
                        f"{Fore.GREEN}Successfully installed system dependencies{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"{Fore.RED}Failed to install system dependencies: {install_result.stderr}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.YELLOW}You may need to manually install the packages with:{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.YELLOW}sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2{Style.RESET_ALL}"
                    )
            except Exception as e:
                print(
                    f"{Fore.RED}Error installing system dependencies: {str(e)}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}Try manually installing: sudo apt-get install -y libnss3{Style.RESET_ALL}"
                )

        # Try to find Windows browser as a fallback
        windows_browser = None
        if is_wsl:
            windows_browser = find_windows_browser()
            if windows_browser:
                print(
                    f"{Fore.GREEN}Found Windows browser at: {windows_browser}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.CYAN}Using Windows browser instead of WSL browser.{Style.RESET_ALL}"
                )

                # Force Playwright to use Windows browser
                os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

                # Set global variable for browser path
                WINDOWS_BROWSER_PATH = windows_browser

        return True

    except ImportError:
        print(f"{Fore.YELLOW}crawl4ai not found. Installing it now...{Style.RESET_ALL}")

        try:
            # Try to install crawl4ai using the current Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "crawl4ai==0.6.3"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"{Fore.GREEN}Successfully installed crawl4ai{Style.RESET_ALL}")

            # Check if running in WSL
            is_wsl = "microsoft-standard" in os.uname().release.lower()

            if is_wsl:
                print(f"{Fore.CYAN}WSL environment detected.{Style.RESET_ALL}")

                # First, try to install required system dependencies
                try:
                    # Try to install libnss3 and other essential dependencies directly
                    print(
                        f"{Fore.YELLOW}Installing required system dependencies for Playwright in WSL...{Style.RESET_ALL}"
                    )

                    # Direct installation of the most critical packages
                    subprocess.run(
                        ["sudo", "apt-get", "update", "-y"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    # Install the minimum required dependencies for Chromium
                    install_result = subprocess.run(
                        [
                            "sudo",
                            "apt-get",
                            "install",
                            "-y",
                            "libnss3",
                            "libnspr4",
                            "libatk1.0-0",
                            "libatk-bridge2.0-0",
                            "libcups2",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    if install_result.returncode == 0:
                        print(
                            f"{Fore.GREEN}Successfully installed system dependencies{Style.RESET_ALL}"
                        )
                    else:
                        print(
                            f"{Fore.RED}Failed to install system dependencies: {install_result.stderr}{Style.RESET_ALL}"
                        )
                        print(
                            f"{Fore.YELLOW}You may need to manually install the packages with:{Style.RESET_ALL}"
                        )
                        print(
                            f"{Fore.YELLOW}sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2{Style.RESET_ALL}"
                        )
                except Exception as e:
                    print(
                        f"{Fore.RED}Error installing system dependencies: {str(e)}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.YELLOW}Try manually installing: sudo apt-get install -y libnss3{Style.RESET_ALL}"
                    )

                # Try to find Windows browser
                windows_browser = find_windows_browser()
                if windows_browser:
                    print(
                        f"{Fore.GREEN}Found Windows browser at: {windows_browser}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}Using Windows browser instead of installing in WSL.{Style.RESET_ALL}"
                    )

                    # Force Playwright to use our Chrome installation
                    os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

                    # These settings don't work as expected with WSL->Windows paths
                    # os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.dirname(windows_browser)
                    # os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"] = windows_browser

                    # Install Playwright but skip browser download
                    print(
                        f"{Fore.YELLOW}Installing Playwright without browsers...{Style.RESET_ALL}"
                    )
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", "playwright"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        print(
                            f"{Fore.GREEN}Successfully installed Playwright{Style.RESET_ALL}"
                        )

                        # For WSL with Windows browsers, we need to use the browsers with the browser_path option
                        # Set global variable that will be used in the crawl_url function
                        WINDOWS_BROWSER_PATH = windows_browser

                    except subprocess.CalledProcessError as e:
                        print(
                            f"{Fore.RED}Failed to install Playwright: {e.stderr}{Style.RESET_ALL}"
                        )
                        return False
                else:
                    print(
                        f"{Fore.YELLOW}No Windows browser found automatically.{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}You can use Windows browsers by setting these environment variables:{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}export PLAYWRIGHT_BROWSERS_PATH=/mnt/c/path/to/browser/directory{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/mnt/c/path/to/browser.exe{Style.RESET_ALL}"
                    )

                    use_windows_browser = input(
                        f"{Fore.YELLOW}Would you like to skip browser installation and configure manually? (y/n): {Style.RESET_ALL}"
                    )
                    if use_windows_browser.lower() == "y":
                        print(
                            f"{Fore.GREEN}Skipping browser installation. Make sure to set the environment variables.{Style.RESET_ALL}"
                        )
                        os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"
                    else:
                        # Install Playwright browsers
                        print(
                            f"{Fore.YELLOW}Installing Playwright browsers in WSL...{Style.RESET_ALL}"
                        )
                        try:
                            # Install system dependencies first
                            install_playwright_dependencies()

                            subprocess.run(
                                [
                                    sys.executable,
                                    "-m",
                                    "playwright",
                                    "install",
                                    "chromium",
                                ],
                                check=True,
                                capture_output=True,
                                text=True,
                            )
                            print(
                                f"{Fore.GREEN}Successfully installed Playwright browsers{Style.RESET_ALL}"
                            )
                        except subprocess.CalledProcessError as e:
                            print(
                                f"{Fore.RED}Failed to install Playwright browsers: {e.stderr}{Style.RESET_ALL}"
                            )
                            print(
                                f"{Fore.YELLOW}You may need to run 'playwright install' manually{Style.RESET_ALL}"
                            )
            else:
                # Not WSL, install browsers normally
                print(
                    f"{Fore.YELLOW}Installing Playwright browsers...{Style.RESET_ALL}"
                )
                try:
                    # Install system dependencies first
                    install_playwright_dependencies()

                    subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print(
                        f"{Fore.GREEN}Successfully installed Playwright browsers{Style.RESET_ALL}"
                    )
                except subprocess.CalledProcessError as e:
                    print(
                        f"{Fore.RED}Failed to install Playwright browsers: {e.stderr}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.YELLOW}You may need to run 'playwright install' manually{Style.RESET_ALL}"
                    )

            # Try to import again after installation
            import crawl4ai

            return True

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Failed to install crawl4ai: {e.stderr}{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}You can install it manually in several ways:{Style.RESET_ALL}"
            )
            print(
                f"{Fore.CYAN}1. Using a virtual environment (recommended):{Style.RESET_ALL}"
            )
            print(f"{Fore.CYAN}   python -m venv venv{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}   source venv/bin/activate  # On Windows: venv\\Scripts\\activate{Style.RESET_ALL}"
            )
            print(f"{Fore.CYAN}   pip install crawl4ai{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}2. Using pipx for isolated installation:{Style.RESET_ALL}"
            )
            print(f"{Fore.CYAN}   pipx install crawl4ai{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}3. If you're sure it's safe, you can override with:{Style.RESET_ALL}"
            )
            print(
                f"{Fore.CYAN}   pip install --break-system-packages crawl4ai{Style.RESET_ALL}"
            )
            return False
        except ImportError:
            print(
                f"{Fore.RED}Failed to import crawl4ai after installation.{Style.RESET_ALL}"
            )
            return False


async def crawl_with_windows_browser(
    url, max_pages=100, deep_crawl=None, browser_path=None
):
    """Custom crawl function to use Windows browser directly from WSL."""
    try:
        from playwright.async_api import async_playwright

        print(
            f"{Fore.CYAN}Initializing direct crawl with Windows browser...{Style.RESET_ALL}"
        )

        # Set up a simple HTML crawler function
        async with async_playwright() as p:
            # Use WSL-compatible browser arguments
            browser_args = {
                "executable_path": browser_path,
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-first-run",
                    "--no-zygote",
                    "--single-process",
                    "--disable-extensions",
                ],
            }

            # Remove remote debugging args that cause issues with WSL
            browser = await p.chromium.launch(**browser_args)
            page = await browser.new_page()

            print(f"{Fore.CYAN}Navigating to {url}...{Style.RESET_ALL}")
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Get the page content
            content = await page.content()

            # Extract just the main content to convert to markdown
            title = await page.title()
            body_text = await page.evaluate("() => document.body.innerText")

            # Create a simple markdown output
            markdown = f"# {title}\n\n{body_text}\n\nSource: {url}"

            await browser.close()

            print(
                f"{Fore.GREEN}Successfully crawled {url} using Windows browser{Style.RESET_ALL}"
            )
            return markdown

    except Exception as e:
        print(
            f"{Fore.RED}Error in direct Windows browser crawl: {str(e)}{Style.RESET_ALL}"
        )
        import traceback

        traceback.print_exc()
        raise


def fallback_simple_crawler(url):
    """
    Enhanced crawler that creates structured research-oriented content.
    """
    import re
    import ssl
    import urllib.request
    from urllib.parse import urljoin, urlparse
    from datetime import datetime

    print(f"{Fore.YELLOW}Using enhanced research crawler for {url}{Style.RESET_ALL}")

    # Create an SSL context that doesn't verify certificates
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        # Fetch the content of the URL
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )

        with urllib.request.urlopen(req, context=context) as response:
            html = response.read().decode("utf-8", errors='ignore')

            # Extract metadata
            title_match = re.search(
                r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL
            )
            title = title_match.group(1).strip() if title_match else "Untitled Page"
            
            # Extract meta description
            desc_match = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                html, re.IGNORECASE
            )
            description = desc_match.group(1).strip() if desc_match else ""

            # Remove unwanted elements
            clean_html = re.sub(
                r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE
            )
            clean_html = re.sub(
                r"<style.*?>.*?</style>",
                "",
                clean_html,
                flags=re.DOTALL | re.IGNORECASE,
            )
            clean_html = re.sub(
                r"<noscript.*?>.*?</noscript>",
                "",
                clean_html,
                flags=re.DOTALL | re.IGNORECASE,
            )

            # Extract main content areas
            main_content = ""
            
            # Try to find main content areas
            main_patterns = [
                r'<main[^>]*>(.*?)</main>',
                r'<article[^>]*>(.*?)</article>',
                r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
                r'<div[^>]*id=["\']content["\'][^>]*>(.*?)</div>'
            ]
            
            for pattern in main_patterns:
                matches = re.findall(pattern, clean_html, re.DOTALL | re.IGNORECASE)
                if matches:
                    main_content = " ".join(matches)
                    break
            
            if not main_content:
                main_content = clean_html

            # Extract headings for structure
            headings = []
            for level in range(1, 4):
                heading_pattern = f'<h{level}[^>]*>(.*?)</h{level}>'
                h_matches = re.findall(heading_pattern, main_content, re.IGNORECASE)
                for h in h_matches:
                    clean_h = re.sub(r'<.*?>', '', h).strip()
                    if clean_h:
                        headings.append((level, clean_h))

            # Extract paragraphs
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', main_content, re.DOTALL | re.IGNORECASE)
            clean_paragraphs = []
            for p in paragraphs[:20]:  # Limit to first 20 paragraphs
                clean_p = re.sub(r'<.*?>', ' ', p).strip()
                clean_p = re.sub(r'\s+', ' ', clean_p)
                if len(clean_p) > 50:  # Only include substantial paragraphs
                    clean_paragraphs.append(clean_p)

            # Extract lists
            lists = re.findall(r'<(?:ul|ol)[^>]*>(.*?)</(?:ul|ol)>', main_content, re.DOTALL | re.IGNORECASE)
            list_items = []
            for lst in lists[:5]:  # Limit to first 5 lists
                items = re.findall(r'<li[^>]*>(.*?)</li>', lst, re.DOTALL | re.IGNORECASE)
                for item in items[:10]:  # Limit items per list
                    clean_item = re.sub(r'<.*?>', '', item).strip()
                    if clean_item:
                        list_items.append(clean_item)

            # Extract links with context
            links = []
            link_pattern = r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>'
            for link_match in re.finditer(link_pattern, html, re.IGNORECASE):
                href = link_match.group(1)
                link_text = re.sub(r'<.*?>', '', link_match.group(2)).strip()
                if href and not href.startswith('#'):
                    full_url = urljoin(url, href)
                    if link_text and len(link_text) > 3:
                        links.append((full_url, link_text))

            # Build structured markdown document
            markdown = f"""# Research Document: {title}

**URL:** {url}  
**Crawled:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Domain:** {urlparse(url).netloc}

## Executive Summary

{description if description else "No description available."}

## Document Structure

"""
            # Add table of contents from headings
            if headings:
                for level, heading in headings[:15]:  # Limit to 15 headings
                    indent = "  " * (level - 1)
                    markdown += f"{indent}- {heading}\n"
            else:
                markdown += "No clear structure detected.\n"

            markdown += "\n## Main Content\n\n"

            # Add content sections based on headings
            current_section = ""
            for i, (level, heading) in enumerate(headings[:10]):
                markdown += f"\n{'#' * (level + 1)} {heading}\n\n"
                
                # Try to find relevant paragraphs after this heading
                relevant_paras = []
                for para in clean_paragraphs:
                    if len(relevant_paras) < 3:  # Max 3 paragraphs per section
                        relevant_paras.append(para)
                
                for para in relevant_paras:
                    markdown += f"{para}\n\n"

            # If no headings, just add paragraphs
            if not headings and clean_paragraphs:
                markdown += "### Content Overview\n\n"
                for para in clean_paragraphs[:10]:
                    markdown += f"{para}\n\n"

            # Add key points from lists
            if list_items:
                markdown += "\n## Key Points\n\n"
                for item in list_items[:15]:
                    markdown += f"- {item}\n"

            # Add navigation structure
            markdown += "\n## Site Navigation\n\n"
            nav_links = [(link, text) for link, text in links if any(
                keyword in text.lower() for keyword in 
                ['home', 'about', 'docs', 'documentation', 'guide', 'tutorial', 
                 'api', 'reference', 'getting started', 'overview']
            )]
            
            if nav_links:
                for link, text in nav_links[:10]:
                    markdown += f"- [{text}]({link})\n"
            else:
                markdown += "No navigation structure detected.\n"

            # Add related resources
            markdown += "\n## Related Resources\n\n"
            resource_links = [(link, text) for link, text in links if any(
                keyword in link.lower() or keyword in text.lower() for keyword in 
                ['github', 'gitlab', 'download', 'npm', 'pypi', 'maven', 
                 'docker', 'example', 'demo', 'playground']
            )]
            
            if resource_links:
                for link, text in resource_links[:10]:
                    markdown += f"- [{text}]({link})\n"

            # Add metadata section
            markdown += f"\n## Document Metadata\n\n"
            markdown += f"- **Source URL:** {url}\n"
            markdown += f"- **Title:** {title}\n"
            markdown += f"- **Word Count:** ~{len(main_content.split())}\n"
            markdown += f"- **Links Found:** {len(links)}\n"
            markdown += f"- **Sections Identified:** {len(headings)}\n"

            print(
                f"{Fore.GREEN}Successfully created research document for {url}{Style.RESET_ALL}"
            )
            return markdown

    except Exception as e:
        print(f"{Fore.RED}Error in research crawler: {str(e)}{Style.RESET_ALL}")
        return f"""# Research Document: Error

**URL:** {url}  
**Error:** {str(e)}  
**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Error Details

An error occurred while attempting to crawl and analyze the specified URL. This could be due to:

- Network connectivity issues
- Access restrictions on the target website
- Invalid or malformed URL
- Server-side errors

Please verify the URL and try again.
"""


async def crawl_url(url, output_file, max_pages=100, deep_crawl=None):
    """Crawl a URL using crawl4ai and save the results to a file."""
    global WINDOWS_BROWSER_PATH

    try:
        from crawl4ai import AsyncWebCrawler
        from playwright.async_api import async_playwright

        print(f"{Fore.CYAN}Crawling {url} with crawl4ai...{Style.RESET_ALL}")

        # Make sure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        crawler_options = {
            "url": url,
            "max_pages": max_pages,
        }

        if deep_crawl:
            crawler_options["deep_crawl"] = deep_crawl

        # If we're in WSL, skip Windows browser attempts and go straight to fallback
        if "microsoft-standard" in os.uname().release.lower():
            print(
                f"{Fore.YELLOW}WSL detected. Using simple crawler for reliability...{Style.RESET_ALL}"
            )
            
            # Use the fallback simple crawler which is more reliable in WSL
            result = fallback_simple_crawler(url)

            # Save the result to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)

            print(
                f"{Fore.GREEN}Crawl successful with fallback crawler. Output saved to {output_file}{Style.RESET_ALL}"
            )
            return True

        # Try normal crawling process with AsyncWebCrawler
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(**crawler_options)

                # Save the result to the output file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.markdown)  # type: ignore

                print(
                    f"{Fore.GREEN}Crawl successful. Output saved to {output_file}{Style.RESET_ALL}"
                )
                return True
        except Exception as e:
            print(f"{Fore.RED}Error with AsyncWebCrawler: {str(e)}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}Falling back to simple crawler method...{Style.RESET_ALL}"
            )

            # Use the fallback simple crawler as last resort
            result = fallback_simple_crawler(url)

            # Save the result to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)

            print(
                f"{Fore.GREEN}Crawl successful with fallback crawler. Output saved to {output_file}{Style.RESET_ALL}"
            )
            return True

    except Exception as e:
        print(f"{Fore.RED}Error crawling {url}: {str(e)}{Style.RESET_ALL}")
        # Print more detailed error information
        import traceback

        traceback.print_exc()

        # Last resort - try the simple crawler
        try:
            print(
                f"{Fore.YELLOW}Trying simple crawler as last resort...{Style.RESET_ALL}"
            )
            result = fallback_simple_crawler(url)

            # Save the result to the output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)

            print(
                f"{Fore.GREEN}Crawl successful with simple crawler. Output saved to {output_file}{Style.RESET_ALL}"
            )
            return True
        except Exception as simple_error:
            print(
                f"{Fore.RED}Simple crawler also failed: {str(simple_error)}{Style.RESET_ALL}"
            )
            return False


def run_crawler(config):
    """Run the crawler for a given configuration."""
    try:
        # Check if crawl4ai is installed
        if not check_crawl4ai_installed():
            return False

        # Get the URL and output file from config
        url = config.get("url")
        if not url:
            print(f"{Fore.RED}No URL specified in the config.{Style.RESET_ALL}")
            return False

        # Get or create the output file path
        output_file = config.get(
            "outputFileName",
            f"crawl_result_{url.replace('://', '_').replace('/', '_')}.md",
        )
        if not os.path.isabs(output_file):
            output_file = os.path.join(os.getcwd(), output_file)

        # Get max pages option
        max_pages = config.get("maxPagesToCrawl", 100)

        # Get deep crawl option (if specified)
        deep_crawl = config.get("deepCrawl")

        # Get PDF generation option
        generate_pdf = config.get("generatePDF", False)

        # Run the crawler asynchronously
        asyncio.run(crawl_url(url, output_file, max_pages, deep_crawl))
        
        # Generate PDF if requested
        if generate_pdf and os.path.exists(output_file):
            try:
                from ccontext.research_pdf_generator import convert_markdown_to_pdf
                pdf_file = output_file.replace('.md', '.pdf').replace('.json', '.pdf')
                convert_markdown_to_pdf(output_file, pdf_file)
                print(f"{Fore.GREEN}PDF generated: {pdf_file}{Style.RESET_ALL}")
            except Exception as pdf_error:
                print(f"{Fore.YELLOW}Could not generate PDF: {str(pdf_error)}{Style.RESET_ALL}")
        
        return True

    except Exception as e:
        print(f"{Fore.RED}Error running crawler: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Main function to be called when the script is run directly."""
    parser = argparse.ArgumentParser(description="Run the crawl4ai crawler.")
    parser.add_argument("--url", help="URL to crawl")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--max-pages", type=int, help="Maximum pages to crawl", default=100
    )
    parser.add_argument(
        "--deep-crawl", help="Deep crawl strategy (bfs, dfs, bestfirst)"
    )
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument(
        "--pdf", action="store_true", help="Generate PDF from crawled content"
    )

    args = parser.parse_args()

    if args.config and os.path.exists(args.config):
        # Load configuration from file
        with open(args.config, "r") as f:
            config_data = json.load(f)

        if isinstance(config_data, list):
            # Multiple configurations
            for config in config_data:
                thread = threading.Thread(target=run_crawler, args=(config,))
                thread.start()
        else:
            # Single configuration
            run_crawler(config_data)
    elif args.url:
        # Create configuration from command line arguments
        config = {
            "url": args.url,
            "outputFileName": args.output
            or f"crawl_result_{args.url.replace('://', '_').replace('/', '_')}.md",
            "maxPagesToCrawl": args.max_pages,
            "generatePDF": args.pdf
        }

        if args.deep_crawl:
            config["deepCrawl"] = args.deep_crawl

        run_crawler(config)
    else:
        print(f"{Fore.RED}No URL or config file specified.{Style.RESET_ALL}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
