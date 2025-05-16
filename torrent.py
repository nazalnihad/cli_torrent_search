import requests
import subprocess
import os
from qbittorrent import Client
import time
import sys

def get_torrent_info(name, limit=15):
    url = f"https://ly.owo.si/api.php?q={name}&p=0&t=3"
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
            search = f'https://ly.owo.si/{link}'
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
            choice = int(input("Enter the number corresponding to the torrent : "))
            if 1 <= choice <= len(torrents):
                return torrents[choice - 1]
            else:
                print("Invalid choice. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def start_qbittorrent():
    try:
        subprocess.Popen(["qbittorrent"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("qBittorrent not found. Please install it using 'sudo pacman -S qbittorrent'.")

def add_to_qbittorrent(magnet_link):
    """Adds the magnet link to qBittorrent via WebUI API."""
    qb = Client('http://localhost:8080/')
    try:
        qb.login('admin', '123456')  # Change credentials if needed
        qb.download_from_link(magnet_link)
        print("Torrent added successfully.")
    except Exception as e:
        print(f"Failed to add torrent: {e}")
        print("Ensure qBittorrent WebUI is enabled and credentials are correct.")


def main():
    name = input("Enter the torrent name: ")
    torrents = get_torrent_info(name)
    if torrents:
        selected_torrent = select_torrent(torrents)
        magnet_link = get_magnet_link(selected_torrent['magnet'])
        start_qbittorrent()

    start_time = time.time()
    print("Waiting for qBittorrent WebUI...", end='', flush=True)

    while time.time() - start_time < 10:
        try:
            response = requests.get('http://localhost:8080/api/v2/app/version', timeout=1)
            if response.status_code == 200:
                print(" Connected!")
                add_to_qbittorrent(magnet_link)
                break
        except (requests.ConnectionError, requests.Timeout):
            print(".", end='', flush=True)  
        time.sleep(1)
    else:
        print("\nERROR: Failed to connect to qBittorrent WebUI within 10 seconds.")
        print("Please ensure:")
        print("1. qBittorrent is running")
        print("2. WebUI is enabled (Tools → Options → WebUI)")
        print("3. Port 8080 is not blocked by firewall")
        sys.exit(1)
    
if __name__ == "__main__":
    main()
