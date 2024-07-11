import requests
import json
from time import sleep

# Configure your personal access token here
ACCESS_TOKEN = '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'
HEADERS = {'Authorization': f'token {ACCESS_TOKEN}'}


def check_rate_limit():
    """Check the remaining rate limit for GitHub API requests."""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        rate_limit = response.json()['rate']['remaining']
        print("Remaining rate limit:", rate_limit)
        return rate_limit
    else:
        print("Failed to retrieve rate limit:", response.text)
        return 0


def robust_request(url):
    """Make a more robust HTTP GET request with retries for handling errors."""
    for attempt in range(5):  # Retry up to 5 times
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response
        elif response.status_code == 403 and 'rate limit' in response.text.lower():
            print("Rate limit hit, sleeping for 60 seconds...")
            sleep(60)  # Sleep for 60 seconds before retrying
        else:
            print(f"Error {response.status_code}: {response.text}, retrying in 10 seconds...")
            sleep(10)  # Sleep for 10 seconds before retrying
    print("Failed to fetch data after several attempts.")
    return None


def search_repositories(query, max_results=1000):
    """Search repositories on GitHub with pagination."""
    items = []
    page = 1
    while len(items) < max_results:
        if check_rate_limit() < 10:
            print("Low on rate limit, halting.")
            break
        url = f'https://api.github.com/search/repositories?q={query}&per_page=100&page={page}'
        response = robust_request(url)
        if response is None:
            break
        current_items = response.json()['items']
        if not current_items:
            break
        items.extend(current_items)
        if len(items) >= max_results:
            items = items[:max_results]
            break
        page += 1
    return items


def get_download_link(repo):
    """Get the download link for the repository."""
    download_link = f"https://api.github.com/repos/{repo['full_name']}/zipball/{repo['default_branch']}"
    return download_link


def main():
    query = 'machine learning'  # Change this to your search query
    repositories = search_repositories(query, max_results=1000)
    links = [get_download_link(repo) for repo in repositories]

    # Save links to a file
    with open('download_links.json', 'w') as file:
        json.dump(links, file, indent=2)
    print(f"Download links have been saved to 'download_links.json'. Total links: {len(links)}")


if __name__ == "__main__":
    main()
