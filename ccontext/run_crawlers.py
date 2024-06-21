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


# Function to run the crawler for a given configuration
def run_crawler(config):
    configJson = json.dumps(config, indent=2)
    print(f"{Fore.GREEN}Now fetching {Style.RESET_ALL}", config["url"])
    print(configJson)
    print('config["resourceExclusions"]', config.get("resourceExclusions"))
    resource_exclusions_string = (
        f"resourceExclusions: {config['resourceExclusions']}"
        if config.get("resourceExclusions") is not None
        else ""
    )
    try:
        # Write the config to config.ts
        with open("gpt-crawler/config.ts", "w") as config_file:
            config_content = f"""
import {{ Config }} from "./src/config";

export const defaultConfig: Config = {{
  url: "{config['url']}",
  match: {json.dumps(config['match'], indent=2)},
  maxPagesToCrawl: {config['maxPagesToCrawl']},
  outputFileName: "{config['outputFileName']}",
  maxTokens: {config['maxTokens']},
 {resource_exclusions_string}
}};
"""
            config_file.write(config_content)

        # Run the crawler with Popen to stream the output
        process = subprocess.Popen(
            ["npm", "start"],
            cwd="gpt-crawler",
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
            print(
                f"{Fore.RED}Error running crawler for URL {config['url']}{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.GREEN}Successfully ran crawler for URL {config['url']}{Style.RESET_ALL}"
            )

    except Exception as e:
        print(
            f"Exception occurred while running crawler for URL {config['url']}: {str(e)}"
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

    # Clone the repository if not already cloned
    if not Path("gpt-crawler").exists():
        subprocess.run(["git", "clone", "https://github.com/builderio/gpt-crawler"])

    # Change to the repository directory
    os.chdir("gpt-crawler")

    # Install npm dependencies
    subprocess.run(["npm", "install"])

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
