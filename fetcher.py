import requests
import subprocess
import time
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import SpinnerColumn, Progress
from qbittorrent import Client

console = Console()

QB_HOST = "http://localhost:8080/"
QB_USERNAME = "admin"  # Change to your qBittorrent WebUI username
QB_PASSWORD = "admin123"  # Change to your qBittorrent WebUI password
WEBUI_TIMEOUT = 15  

def get_torrent_info(name, limit=15):
    url = f"https://ly.owo.si/api.php?q={name}&p=0&t=3"
    try:
        response = requests.get(url, timeout=20)
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
        response = requests.head(search, allow_redirects=False, timeout=20)
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

def start_qbittorrent():
    try:
        subprocess.Popen(
            ["qbittorrent"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        console.print("[yellow]Starting qBittorrent...[/yellow]")
    except FileNotFoundError:
        console.print(
            "[red]qBittorrent not found. Install it with 'sudo pacman -S qbittorrent'.[/red]"
        )
        sys.exit(1)

def add_to_qbittorrent(magnet_link):
    try:
        qb = Client(QB_HOST)
        qb.login(QB_USERNAME, QB_PASSWORD)
        qb.download_from_link(magnet_link)
        console.print("[green]Torrent added successfully![/green]")
    except Exception as e:
        console.print(f"[red]Failed to add torrent: {e}[/red]")
        console.print("Possible issues:")
        console.print(f"1. Invalid credentials (username: {QB_USERNAME}, password: {QB_PASSWORD})")
        console.print("2. WebUI not enabled or port 8080 blocked")
        console.print("3. qBittorrent version incompatible with python-qbittorrent")
        console.print("Run 'curl http://localhost:8080/api/v2/app/version' to test WebUI.")
        sys.exit(1)

def wait_for_webui():
    with Progress(
        SpinnerColumn(),
        "[progress.description]Waiting for qBittorrent WebUI...",
        console=console
    ) as progress:
        task = progress.add_task("", total=WEBUI_TIMEOUT)
        start_time = time.time()

        while time.time() - start_time < WEBUI_TIMEOUT:
            try:
                response = requests.get(
                    f"{QB_HOST}api/v2/app/version",
                    timeout=1
                )
                if response.status_code == 200 or response.status_code == 403:
                    progress.update(task, completed=WEBUI_TIMEOUT)
                    return True
                progress.advance(task, advance=1)
            except (requests.ConnectionError, requests.Timeout):
                progress.advance(task, advance=1)
            time.sleep(1)

    console.print(
        f"[red]ERROR: Failed to connect to qBittorrent WebUI within {WEBUI_TIMEOUT} seconds.[/red]"
    )
    console.print("Please ensure:")
    console.print("1. qBittorrent is running")
    console.print("2. WebUI is enabled (Tools → Options → WebUI)")
    console.print("3. Port 8080 is not blocked by firewall")
    console.print(
        f"4. Credentials (username: {QB_USERNAME}, password: {QB_PASSWORD}) are correct"
    )
    return False

def main():
    name = Prompt.ask("Enter the torrent name", console=console)
    torrents = get_torrent_info(name)
    if not torrents:
        console.print("[red]No torrents found.[/red]")
        sys.exit(1)

    selected_torrent = select_torrent(torrents)
    magnet_link = get_magnet_link(selected_torrent["magnet"])
    start_qbittorrent()

    if wait_for_webui():
        add_to_qbittorrent(magnet_link)

if __name__ == "__main__":
    main()
