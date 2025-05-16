cli_torrent_search
A command-line tool to search torrents and add them to qBittorrent.
Features

Search torrents via API.
Add torrents to qBittorrent WebUI.
Linux: Rich terminal UI.
Windows: Simple text UI.

Prerequisites

qBittorrent with WebUI enabled.
Python 3.6+.

Setup
1. Install qBittorrent
Linux:
sudo pacman -S qbittorrent  # Arch
sudo apt install qbittorrent  # Ubuntu

Windows: Download from qbittorrent.org.
2. Configure qBittorrent WebUI

Open qBittorrent > Tools > Options > Web UI.
Enable WebUI, set port 8080, username (e.g., admin), password (e.g., admin123).
Optional: Enable Bypass localhost authentication.
Test: curl http://localhost:8080/api/v2/app/version.

3. Install Dependencies
Clone the repo:
git clone https://github.com/yourusername/cli_torrent_search.git
cd cli_torrent_search

Install Python packages:
python -m venv venv
source venv/bin/activate  # Linux: venv\Scripts\activate on Windows
pip install -r requirements.txt

requirements.txt:
requests==2.31.0
rich==13.7.1
qbittorrent==0.3.1

4. Configure Scripts
Linux:

Edit fetcher.py:QB_USERNAME = "admin"
QB_PASSWORD = "admin123"


Make torrent executable:chmod +x torrent
mv torrent ~/bin/



Windows:

Edit beat.py:qbittorrent_path = 'C:/Program Files/qBittorrent/qbittorrent.exe'
qb.login('admin', '123456')



Usage
Linux:
torrent
# OR
python fetcher.py

Windows:
python beat.py


Enter torrent name.
Select torrent.
Torrent is added to qBittorrent.

Screenshots

Linux UI: [path/to/linux_ui.png]
Windows UI: [path/to/windows_ui.png]

Troubleshooting

GUI not opening: Install qt5-wayland qt6-wayland (Linux) or check path (Windows).
WebUI fails: Verify port 8080 (ss -tuln | grep 8080), credentials, or enable localhost bypass.
No torrents: Test API (curl https://ly.owo.si/api.php?q=ubuntu&p=0&t=3).

Disclaimer
Use at your own risk. Ensure compliance with local laws. Not responsible for misuse.
License
MIT License.
