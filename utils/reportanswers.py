#find out what we need to import to get answers for report
 def organizer(URL_array):
  words_per_page = {}
  for url in URL_array:
    total_words = soup.get_text() #don't know if it returns an array or if an entire string that needs splitting
    words_per_page[url] = total_words.length
  return words_per_page
highest = sorted(words_per_page.items(),lambda x: x[1], reverse = True)

x = open("file.txt","r")
stopwords = x.read()
freq = {}
for url in urlArray:
  urlwords = soup.get_text().split(" ")
  for word in urlwords:
    if word not in stopwords:
      if word in freq:
        freq[word] = freq[word] + 1
      else:
        freq[word] = 1
highest50 = sorted(freq.items(), lambda x: x[1], reverse = True)[0:49]

def uniquesubdomains():
  subdomains = {} #subdomains by value in dictionary
  regexexpression = "[/]+\S+\." #regex expression
  for url in urlarray: #loop through the all given urls
    x = re.findall(regexexpression,url) #finds matches and returns list
    subdomain = x[0].replace("//","")#grab first value and replace // with ""
    if subdomain in subdomains:#checks if the domain is already in the dict
      subdomains[subdomain] = subdomains[subdomain] + 1 #adds one
    else:
      subdomains[subdomain] = 1 #else sets it to one
  return sorted(subdomains.items(),lambda x: x[0]) #returns a sorted array alphabetically of each by item