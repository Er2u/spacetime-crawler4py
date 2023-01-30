import re, hashlib
from utils.config import Config
from utils.download import download
from urllib.parse import urlparse
from configparser import ConfigParser
from bs4 import BeautifulSoup


visited_urls = set()  # Set to keep track of URLs that have already been visited
fingerprints = set()  # Set to keep track of page content fingerprints
content_length_threshold = 1048576*1024 # 1GB


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, resp)]


def extract_next_links(url, resp):
    if resp.raw_response == None:
        return []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            links.append(href)
    return links


def is_valid(url,resp):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        # Check if URL has already been visited
        if url in visited_urls:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        
        # Filter out urls that are not with uci domain
        return not re.match(r".*\.ics\.uci\.edu|.*\.cs\.uci\.edu|.*\.informatics\.uci\.edu|.*\.stat\.uci\.edu", parsed.hostname)
    
        content_hash = hashlib.sha256(resp.raw_response.content).hexdigest()
        # Check if page has already been visited (using fingerprinting)
        if parsed.netloc in visited_content_hashes:
            return False
        # Check if URL is dead (status code is 200)
        if resp.status == 200:
            return False
        # Check if page has no content or too much content
        if len(resp.raw_response.content) == 0 or len(resp.raw_response.content) > content_length_threshold:
            return False
        # Add visited urls
        visited_urls.add(parsed.netloc)
        # Add visited content hash
        visited_content_hashes.add(content_hash)
        return True
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise
