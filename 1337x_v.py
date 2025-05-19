#!/usr/bin/env python3
import sys
import time
from qbittorrentapi import Client
from py1337x import Py1337x
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# qBittorrent WebUI credentials
QB_USERNAME = "admin"
QB_PASSWORD = "admin123"
QB_HOST = "http://localhost:8080"

torrents = Py1337x()

console = Console()

def get_torrent_info(name, page=1, max_results_per_page=15, retries=3, delay=2):
    for attempt in range(retries):
        try:
            results = torrents.search(name, sort_by="seeders", page=page)
            if not results or not hasattr(results, 'items') or not results.items:
                return []
            items = results.items[:max_results_per_page]
            return [
                {
                    "name": t.name,
                    "size": t.size,
                    "seeders": t.seeders,
                    "magnet": t.torrent_id  
                }
                for t in items
            ]
        except Exception as e:
            console.print(f"[red]Attempt {attempt+1}/{retries} failed: {e}[/red]")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                console.print("[red]Error fetching torrents from 1337x. Check your network or try a different API.[/red]")
                return []

def get_magnet_link(torrent_id):
    try:
        info = torrents.info(torrent_id=torrent_id)
        return info.magnet_link
    except Exception as e:
        console.print(f"[red]Error retrieving magnet link: {e}[/red]")
        return None

def add_to_qbittorrent(magnet_link):
    try:
        qb = Client(host=QB_HOST, username=QB_USERNAME, password=QB_PASSWORD)
        qb.auth_log_in()
        qb.torrents_add(urls=magnet_link)
        console.print("[green]Torrent added to qBittorrent![/green]")
    except Exception as e:
        console.print(f"[red]Failed to add torrent to qBittorrent: {e}[/red]")
        sys.exit(1)

def display_torrents(torrents):
    table = Table(title="Available Torrents", title_style="bold cyan")
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Name", style="white")
    table.add_column("Size", style="green")
    table.add_column("Seeders", style="yellow", justify="center")

    for idx, torrent in enumerate(torrents, 1):
        table.add_row(
            str(idx),
            torrent["name"],
            torrent["size"],
            str(torrent["seeders"])
        )

    console.print(table)

def main():
    name = Prompt.ask("Enter torrent name", console=console)
    page = 1
    all_torrents = []

    while True:
        new_torrents = get_torrent_info(name, page=page)
        if not new_torrents:
            if not all_torrents:
                console.print("[red]No torrents found.[/red]")
                sys.exit(1)
            console.print("[yellow]No more results available.[/yellow]")

        all_torrents.extend(new_torrents)
        display_torrents(all_torrents)

        console.print("\n[bold]Options:[/bold]")
        console.print("- Enter a number to select a torrent")
        console.print("- 'm' to see more results")
        console.print("- 'q' to quit")
        choice = Prompt.ask("Your choice", console=console)

        if choice.lower() == 'q':
            console.print("[yellow]Exiting...[/yellow]")
            sys.exit(0)
        elif choice.lower() == 'm':
            page += 1
            continue
        else:
            try:
                choice = int(choice)
                if not (1 <= choice <= len(all_torrents)):
                    console.print("[red]Invalid choice. Please select a number within the range.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]Invalid input. Please enter a number, 'm', or 'q'.[/red]")
                continue

    magnet_link = get_magnet_link(all_torrents[choice - 1]["magnet"])
    if not magnet_link:
        console.print("[red]Failed to retrieve magnet link.[/red]")
        sys.exit(1)

    add_to_qbittorrent(magnet_link)

if __name__ == "__main__":
    main()