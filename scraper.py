import re, hashlib
from utils.config import Config
from utils.download import download
from urllib.parse import urlparse
from configparser import ConfigParser
from bs4 import BeautifulSoup


visited_urls = set()  # Set to keep track of URLs that have already been visited
#fingerprints = set()# Set to keep track of page content fingerprints
global_tokenMap = {}  # set to keep track the frequency of words
page_length = {}      # set to keep track the length of words in each unique page
content_length_threshold = 1048576*1024 # 1GB


def isascii(c):
    return c <= u"\u007f"

# previous tokenize from assignment 1
def tokenize(content):
    tokens = []
    line = content.split()
    for token in line:
        cur = []
        for idx in range(len(token)):
            if token[idx].isalnum() and isascii(token[idx]):  # Test current character's type, it should be Ascii printable character and alphanumeric character.
                cur.append(token[idx])
                if idx == len(token) - 1 and len(cur) > 0: # if there is no special situations in the whole word
                    tokens.append(''.join(cur).lower()) # join the character in the list together and change all of them to lower case so that they can be utilized to count the frequency
                    cur = [] # Reset the cur value that can be used in the next loop.
            else:   #To find out special situations, for example, whether the token has illegal characters
                if len(cur) > 0:
                    tokens.append(''.join(cur).lower())
                    cur = []
    return tokens

def computeWordFrequencies(tokens, tokenMap):
    for token in tokens:
        if token in tokenMap.keys():
            tokenMap[token] += 1
        else:
            tokenMap[token] = 1
            
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, resp)]



def extract_next_links(url, resp):
    if resp.raw_response == None:
        return []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a') if link.get('href') == True]
    #links = []
    #for link in soup.find_all('a'):
        #href = link.get('href')
        #if href:
            #links.append(href)
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

        if re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False  # return just False

        if not re.match(r".*\.ics\.uci\.edu.*|.*\.cs\.uci\.edu.*|.*\.informatics\.uci\.edu.*|.*\.stat\.uci\.edu.*", str(parsed.hostname)):
            return False
        
        visited_urls.add(parsed.netloc)
        if resp.status == 200 and len(resp.raw_response.content) == 0:
            return False

        # Check if page has no content or too much content
        if len(resp.raw_response.content) == 0 or len(resp.raw_response.content) > content_length_threshold:
            return False
        
        processed_contnet = BeautifulSoup(resp.raw_response.content, features='lxml').get_text()
        all_tokens = tokenize(content=processed_contnet)
        page_length[url] = len(all_tokens)
        computeWordFrequencies(tokens=all_tokens, tokenMap=global_tokenMap)
        for word in global_tokenMap:
            if word in stopwords:
                global_tokenMap.pop(word)
        # keep the data  and  generate extra log than can be used for the report
        visited_urls_file = open('visited_urls_file', 'w')
        visited_urls_file.write(str(visited_urls))
        visited_urls_file.close()

        global_tokenMap_file = open('global_tokenMap_file', 'w')
        global_tokenMap_file.write(str(global_tokenMap))
        global_tokenMap_file.close()

        page_length_file = open('page_length_file', 'w')
        page_length_file.write(str(page_length))
        page_length_file.close()

        scraper_log = open('scraper_log.log', 'w')
        scraper_log.write("The number of pages visited: " + str(len(visited_urls)) + "\n")    #still need make sure & double check

        temp = sorted(page_length.items(), key=lambda x: -x[1])
        scraper_log.write("The page with most words: " + str(temp[0]) + "\n")

        temp = sorted(global_tokenMap.items(), key=lambda x: -x[1])
        scraper_log.write("The first 50 frequent words: " + str(temp[0:50]) + "\n")              #still need to work on handling stop words

        subdomain_num = len([1 for item in visited_urls if 'ics.uci.edu' in item])
        scraper_log.write("The number of subdomains of ics.uci.edu: " + str(subdomain_num) + "\n")    #this may be changed since we can use Regular Expression
        scraper_log.write("\n")
        scraper_log.write("The domains in alphabetical order are as follows \n")
        z = {}
        #visited_urls_dict = {subdomain:0 for subdomain in url for page in page_length if subdomain not in page else subdomain:visited_urls_dict[subdomain] + 1}
        for subdomain in visited_urls:
            z[subdomain] = 0
            for page in page_length:
                if subdomain in page:
                    z[subdomain] = z[subdomain] + 1
        scraper.log.write(sorted(z.items(),lambda x: x[0]))
        scraper_log.close()
        return True
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise
