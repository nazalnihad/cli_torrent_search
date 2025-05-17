import requests
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console(force_stderr=False)

# Torrent client configuration
TORRENT_CLIENT_PACKAGE = "org.proninyaroslav.libretorrent"  # LibreTorrent package name
TORRENT_CLIENT_ACTIVITY = ".ui.addtorrent.AddTorrentActivity"  # Activity for magnet links
# TORRENT_CLIENT_PACKAGE = "org.proninyaroslav.libretorrent"  # LibreTorrent
# TORRENT_CLIENT_PACKAGE = "com.utorrent.client"  # uTorrent
# TORRENT_CLIENT_PACKAGE = "com.delphicoder.flud"  # Flud package name

def get_torrent_info(name, limit=15):
    """Fetch torrent information from API."""
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

def open_torrent_client(magnet_link):
    try:
        console.print(f"[yellow]Opening magnet link in {TORRENT_CLIENT_PACKAGE}: {magnet_link[:50]}...[/yellow]")
        subprocess.run(
            [
                "am", "start",
                "-a", "android.intent.action.VIEW",
                "-d", magnet_link,
                "-n", f"{TORRENT_CLIENT_PACKAGE}/{TORRENT_CLIENT_ACTIVITY}"
            ],
            check=True
        )
        console.print(f"[green]Magnet link sent to {TORRENT_CLIENT_PACKAGE}![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to open torrent client: {e}[/red]")
        console.print(f"Ensure {TORRENT_CLIENT_PACKAGE} is installed and supports magnet links.")
        console.print(f"Try running 'am start -a android.intent.action.VIEW -d \"{magnet_link}\" -n {TORRENT_CLIENT_PACKAGE}/{TORRENT_CLIENT_ACTIVITY}' manually to debug.")
        console.print("Alternative activities to try:")
        console.print("- org.proninyaroslav.libretorrent/.ui.main.MainActivity")
        console.print("- org.proninyaroslav.libretorrent/.ui.TorrentActivity")
        console.print("Check activities with: dumpsys package org.proninyaroslav.libretorrent | grep Activity")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[red]'am' command not found. Ensure Termux:API is installed.[/red]")
        console.print("Run 'pkg install termux-api' and try again.")
        sys.exit(1)

def main():
    name = Prompt.ask("Enter the torrent name", console=console)
    torrents = get_torrent_info(name)
    if not torrents:
        console.print("[red]No torrents found.[/red]")
        sys.exit(1)

    selected_torrent = select_torrent(torrents)
    magnet_link = get_magnet_link(selected_torrent["magnet"])
    open_torrent_client(magnet_link)

if __name__ == "__main__":
    main()