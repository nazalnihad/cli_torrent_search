import requests
import subprocess
import os
from qbittorrent import Client

def get_torrent_info(name, limit=15):
    url = f"https://librey.org/api.php?q={name}&p=0&t=3"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[:limit]
    except requests.RequestException as e:
        print(f"Error: {e}")
        return []

def get_magnet_link(link):
    link = link.strip()
    if link.startswith('magnet'):
        return link
    else:
        try:
            search = f'https://librey.org/{link}'
            r = requests.head(search, allow_redirects=False)
            r.raise_for_status()
            if 300 < r.status_code < 400:
                url = r.headers.get('Location', search)
            return url
        except requests.RequestException as e:
            print(f"Error: {e}")
            return link

def select_torrent(torrents):
    print("Select a torrent:")
    for idx, torrent in enumerate(torrents, start=1):
        print(f"{idx}. {torrent['name']} {torrent['size']} {torrent['seeders']} ")
    while True:
        try:
            choice = int(input("Enter the number corresponding to the torrent you want to add: "))
            if 1 <= choice <= len(torrents):
                return torrents[choice - 1]
            else:
                print("Invalid choice. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def start_qbittorrent():
    # Specify the path to the qBittorrent executable
    qbittorrent_path = 'C:/Program Files/qBittorrent/qbittorrent.exe'
    subprocess.Popen([qbittorrent_path])

def add_to_qbittorrent(magnet_link):
    qb = Client('http://localhost:8080/')
    qb.login('admin', '123456')  # your qBittorrent username and password
    qb.download_from_link(magnet_link)

def main():
    name = input("Enter the torrent name: ")
    torrents = get_torrent_info(name)
    if torrents:
        selected_torrent = select_torrent(torrents)
        magnet_link = get_magnet_link(selected_torrent['magnet'])
        start_qbittorrent()
        add_to_qbittorrent(magnet_link)
        print("Torrent added to qBittorrent.")
    else:
        print("No torrents found.")

if __name__ == "__main__":
    main()
