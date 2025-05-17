import requests
import subprocess
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

# Download directory
DOWNLOAD_DIR = os.path.expanduser("~/storage/downloads")
# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_torrent_info(name, limit=15):
    url = f"https://ly.owo.si/api.php?q={name}&p=0&t=3"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()[:limit]
    except requests.RequestException as e:
        console.print(f"[red]Error fetching torrent info: {e}[/red]")
        return []

def get_magnet_link(link):
    link = link.strip()
    if link.startswith("magnet"):
        return link
    try:
        search = f"https://ly.owo.si/{link}"
        response = requests.head(search, allow_redirects=False, timeout=5)
        response.raise_for_status()
        if 300 < response.status_code < 400:
            return response.headers.get("Location", search)
        return search
    except requests.RequestException as e:
        console.print(f"[red]Error resolving magnet link: {e}[/red]")
        return link

def display_torrents(torrents):
    table = Table(title="Available Torrents")
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Name", style="white")
    table.add_column("Size", style="green")
    table.add_column("Seeders", style="yellow", justify="center")

    for idx, torrent in enumerate(torrents, start=1):
        table.add_row(
            str(idx),
            torrent["name"],
            torrent["size"],
            str(torrent["seeders"])
        )

    console.print(table)

def select_torrent(torrents):
    display_torrents(torrents)
    while True:
        choice = Prompt.ask(
            "Enter the number of the torrent to add",
            console=console
        )
        try:
            choice = int(choice)
            if 1 <= choice <= len(torrents):
                return torrents[choice - 1]
            console.print("[red]Invalid choice. Please enter a number within the range.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")

def start_torrent_download(magnet_link):
    try:
        console.print(f"[yellow]Starting download with aria2c: {magnet_link[:50]}...[/yellow]")
        subprocess.run(
            [
                "aria2c",
                "--dir", DOWNLOAD_DIR,
                "--log", os.path.join(DOWNLOAD_DIR, "aria2.log"),
                "--log-level=info",
                "--max-connection-per-server=4",
                "--split=4",
                "--min-split-size=5M",
                "--seed-time=0",
                magnet_link
            ],
            check=True
        )
        console.print(f"[green]Download completed! Files saved to {DOWNLOAD_DIR}[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to start download: {e}[/red]")
        console.print(f"Check aria2c logs at {os.path.join(DOWNLOAD_DIR, 'aria2.log')}")
        console.print("Ensure aria2 is installed: pkg install aria2")
        console.print(f"Try running manually: aria2c --dir={DOWNLOAD_DIR} \"{magnet_link}\"")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[red]'aria2c' command not found. Ensure aria2 is installed.[/red]")
        console.print("Run 'pkg install aria2' and try again.")
        sys.exit(1)

def main():
    name = Prompt.ask("Enter the torrent name", console=console)
    torrents = get_torrent_info(name)
    if not torrents:
        console.print("[red]No torrents found.[/red]")
        sys.exit(1)

    selected_torrent = select_torrent(torrents)
    magnet_link = get_magnet_link(selected_torrent["magnet"])
    start_torrent_download(magnet_link)

if __name__ == "__main__":
    main()