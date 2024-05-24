import requests

name = input("enter the torrent name : ")
# limit = int(input("enter no of torrents to get : "))
limit = 10
url = f"https://search.decentrala.org/api.php?q={name}&p=0&t=3"

# Send a GET request to the API endpoint
response = requests.get(url)

def get_magnet_link(link):
    link = link.strip()
    # print(link)
    if link.startswith('magnet'):
        return link
    else:
        try:
            search = f'https://search.decentrala.org/{link}'
            # response = requests.head(search)
            r = requests.head(search, allow_redirects=False)
            r.raise_for_status()
            if 300 < r.status_code < 400:
                url = r.headers.get('Location', search)
            return url
            # return page_url
        except requests.RequestException as e:
            print(f"Error: {e}")
            return link

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    # print(data)
    for i in data[:limit]:
        name = i.get('name')
        seeders = i.get('seeders')
        leechers = i.get('leechers')
        magnet = i.get('magnet')
        size = i.get('size')
        source = i.get('source')

        magnet = get_magnet_link(magnet)

        print(f"\n===========")
        print(f"\nName: {name} '\nSeeders: ' {seeders} '\nLeechers: ' {leechers} '\nMagnet: ' {magnet} \n'size: '{size}")
        print(f"===========")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")


