import urllib.request
import urllib.parse
import re
import json

def search_libgen(query):
    print(f"Searching Libgen for: {query}")
    url = f"https://libgen.is/search.php?req={urllib.parse.quote(query)}&res=25&view=simple&phrase=1&column=def"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Find all MD5 hashes in the HTML (Libgen uses MD5 for download links)
        # The table rows contain md5 hashes in the href to book details
        md5s = re.findall(r'href=[\'"]book/index\.php\?md5=([a-fA-F0-9]{32})[\'"]', html)
        
        # Make unique
        md5s = list(dict.fromkeys(md5s))
        
        if not md5s:
            print("No results found on Libgen.")
            return
            
        print(f"Found {len(md5s)} results. Fetching metadata for top 3...")
        
        # Get metadata from JSON API
        api_url = f"https://libgen.is/json.php?ids={','.join(md5s[:3])}&fields=id,title,author,year,extension,md5,language"
        api_req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        metadata = json.loads(urllib.request.urlopen(api_req).read().decode('utf-8'))
        
        for book in metadata:
            print(f"\nTitle: {book.get('title')}")
            print(f"Author: {book.get('author')}")
            print(f"Year: {book.get('year')} | Language: {book.get('language')} | Ext: {book.get('extension')}")
            print(f"Download link: http://library.lol/main/{book.get('md5')}")
            
    except Exception as e:
        print(f"Error searching libgen: {e}")

if __name__ == "__main__":
    search_libgen("Numerology Johari")
    print("-" * 50)
    search_libgen("Carmen Astrologicum")
    print("-" * 50)
    search_libgen("Di Tian Sui")
    print("-" * 50)
    search_libgen("Essence of Heavenly Marrow")
    print("-" * 50)
    search_libgen("San Ming Tong Hui")
