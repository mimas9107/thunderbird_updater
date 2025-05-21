#!/usr/bin/env python3
import os
import re
import requests
from bs4 import BeautifulSoup

THUNDERBIRD_DIR = "/opt/thunderbird/"
THUNDERBIRD_BIN = os.path.join(THUNDERBIRD_DIR, "thunderbird")
BASE_URL = "https://download-origin.cdn.mozilla.net/pub/thunderbird/releases/"
#LINUX64_PATH = "linux-x86_64/en-US/"
LINUX64_PATH="linux-x86_64/zh-TW/"

def version_str_to_tuple(version: str) -> tuple:
    """Clean and convert version string to tuple."""
    version = version.strip().lower().replace("thunderbird", "")
    version = re.sub(r"[^\d.]", "", version)
    return tuple(map(int, version.split(".")))


def get_stable_versions(url: str) -> list[str]:
    """Get stable version directories from Thunderbird release index."""
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    dirs = [a.text for a in soup.find_all('a', href=True)]
    stable = [v for v in dirs if re.fullmatch(r"\d+(\.\d+)*\/", v)]
    return stable


def get_latest_version(versions: list[str]) -> str:
    """Return the latest version (as string) from a list of version strings."""
    return max(versions, key=version_str_to_tuple).strip("/")


def get_local_version() -> str:
    if not os.path.exists(THUNDERBIRD_BIN):
        return "0.0.0"
    stream = os.popen(f"{THUNDERBIRD_BIN} --version")
    version_output = stream.read().strip()
    return version_output


def should_update(local_version: str, latest_version: str) -> bool:
    return version_str_to_tuple(local_version) < version_str_to_tuple(latest_version)


def download_and_extract(version: str):
    #tarball = f"thunderbird-{version}.tar.bz2"
    tarball=f"thunderbird-{version}.tar.xz"
    download_url = f"{BASE_URL}{version}/{LINUX64_PATH}{tarball}"
    print(f"Downloading: {download_url}")

    res = requests.get(download_url, stream=True)
    if res.status_code == 200:
        with open(tarball, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        print("\nDownload complete. Extracting...")
        os.system(f"sudo tar Jxvf {tarball}")
        os.remove(tarball)

        if os.path.exists("thunderbird"):
            print(f"Replacing old Thunderbird in {THUNDERBIRD_DIR}...")
            os.system(f"sudo rm -rf {THUNDERBIRD_DIR}")
            os.system(f"sudo mv thunderbird {THUNDERBIRD_DIR}")
        else:
            print("Extraction failed: 'thunderbird' folder not found")
    else:
        print(f"Failed to download from {download_url}. HTTP {res.status_code}")


if __name__ == "__main__":
    stable_versions = get_stable_versions(BASE_URL)
    latest_version = get_latest_version(stable_versions)
    local_version = get_local_version()

    print(f"Local Thunderbird version: {local_version}")
    print(f"Latest Thunderbird version: {latest_version}")

    if should_update(local_version, latest_version):
        print("Updating Thunderbird...")
        download_and_extract(latest_version)
    else:
        print("Thunderbird is up to date. No action taken.")

