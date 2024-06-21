import os
import subprocess
import json
import threading
from pathlib import Path
import argparse
from colorama import Fore, Style


# Load configuration data from config.json
def load_config_data(config_file):
    with open(config_file, "r") as file:
        return json.load(file)


# Function to write the gpt-crawler/config.ts file
def write_config_ts(config):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, "gpt-crawler", "config.ts")
    resourceExclusionsList = config.get("resourceExclusions")
    resource_exclusions_string = (
        f"resourceExclusions: {resourceExclusionsList}"
        if resourceExclusionsList is not None
        else ""
    )

    config_content = f"""
import {{ Config }} from "./src/config";

export const defaultConfig: Config = {{
  url: "{config['url']}",
  match: {json.dumps(config['match'], indent=2)},
  maxPagesToCrawl: {config['maxPagesToCrawl']},
  outputFileName: "{config['outputFileName']}",
  maxTokens: {config['maxTokens']},
  {resource_exclusions_string},
}};
"""

    with open(config_file_path, "w") as config_file:
        config_file.write(config_content)
        # print(f"{Fore.GREEN}Config written to {config_file_path}{Style.RESET_ALL}")


# Function to run npm start command
def run_npm_start():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gpt_crawler_dir = os.path.join(script_dir, "gpt-crawler")

    if not os.path.exists(gpt_crawler_dir):
        print(
            f"{Fore.RED}gpt-crawler directory not found at {gpt_crawler_dir}{Style.RESET_ALL}"
        )
        check_and_install_gpt_crawler()
        return False

    process = subprocess.Popen(
        ["npm", "start"],
        cwd=gpt_crawler_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Stream the output to stdout
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Stream the error to stdout
    while True:
        error = process.stderr.readline()
        if error == "" and process.poll() is not None:
            break
        if error:
            print(f"{Fore.RED}{error.strip()}{Style.RESET_ALL}")

    # Wait for the subprocess to finish
    process.wait()

    # Check for errors
    if process.returncode != 0:
        return False
    return True


# Function to check if gpt-crawler is installed and install if necessary
def check_and_install_gpt_crawler():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gpt_crawler_dir = os.path.join(script_dir, "gpt-crawler")

    if not Path(gpt_crawler_dir).exists():
        print(f"{Fore.CYAN}gpt-crawler not installed, installing now...{Style.RESET_ALL}")
        os.chdir(script_dir)

        print(f"{Fore.CYAN}Cloning gpt-crawler repository...{Style.RESET_ALL}")
        subprocess.run(["git", "clone", "https://github.com/builderio/gpt-crawler"])

        os.chdir("gpt-crawler")

        print(f"{Fore.CYAN}Installing npm dependencies...{Style.RESET_ALL}")
        subprocess.run(["npm", "install"])


# Function to run the crawler for a given configuration
def run_crawler(config):
    check_and_install_gpt_crawler()
    write_config_ts(config)

    print(f"{Fore.GREEN}Now fetching {Style.RESET_ALL} {config['url']}")

    if run_npm_start():
        print(
            f"{Fore.GREEN}Successfully ran crawler for URL {config['url']}{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.RED}Error running crawler for URL {config['url']}{Style.RESET_ALL}"
        )


# Main function
def main():
    parser = argparse.ArgumentParser(description="Run multiple crawlers in parallel.")
    parser.add_argument(
        "--crawl",
        action="store_true",
        default=True,
        help="Flag to enable crawling (default: True)",
    )
    args = parser.parse_args()

    if not args.crawl:
        print("Crawling is disabled. Exiting.")
        return

    check_and_install_gpt_crawler()

    # Load the config data
    config_data = load_config_data(
        "../config.json"
    )  # Adjust the path to your config.json file

    # Run the crawlers in parallel
    threads = []
    for config in config_data:
        thread = threading.Thread(target=run_crawler, args=(config,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All crawling tasks completed.")


if __name__ == "__main__":
    main()
