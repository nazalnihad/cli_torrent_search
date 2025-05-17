import requests
from bs4 import BeautifulSoup

def set_query(search):
    return f"{search}"

def get_links(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        magnet_links = []
        for a_tag in soup.find_all('a'):
            # href = a_tag['href']
            print(a_tag.get('href'))
            # links.append(href)
            # if href.startswith('magnet:?'):
            #     magnet_links.append(href)
        # return links
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

# def get_magnet(links):
#     for link in links:
#         print(link)
        
# Example usage
url = 'https://1337x.to/search/extracurricular/1/'
get_links(url)
# get_magnet(magnet_links)
# print(len(magnet_links))
# for link in magnet_links:
#     print(link)
