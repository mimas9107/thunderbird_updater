#!/usr/bin/env python3
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import requests
from packaging import version


MOZILLA_FTP_BASE = "https://releases.mozilla.org/pub/thunderbird/releases"
DEFAULT_INSTALL_PATH = "/opt/thunderbird"
DEFAULT_CACHE_DIR = "./download_cache"


def get_local_version(install_path: str = DEFAULT_INSTALL_PATH) -> Optional[str]:
    """取得本機已安裝的 Thunderbird 版本"""
    version_file = Path(install_path) / "thunderbird" / "updater.ini"
    if not version_file.exists():
        return None

    try:
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(version_file)
        return cfg.get("App", "Version", fallback=None)
    except Exception:
        pass

    thunderbird_bin = Path(install_path) / "thunderbird" / "thunderbird"
    if thunderbird_bin.exists():
        result = subprocess.run(
            [str(thunderbird_bin), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        match = re.search(r"Thunderbird\s+(\d+\.\d+(?:\.\d+)?)", result.stdout or result.stderr)
        if match:
            return match.group(1)
    return None


def fetch_latest_version(channel: str = "release") -> Optional[str]:
    """從 Mozilla FTP 取得最新版本號"""
    url = f"{MOZILLA_FTP_BASE}/"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching version list: {e}", file=sys.stderr)
        return None

    version_pattern = re.compile(r'href="/pub/thunderbird/releases/(\d+(?:\.\d+)+(?:esr)?)/"')
    versions = version_pattern.findall(resp.text)

    if not versions:
        return None

    def parse_ver(v: str) -> version.Version:
        clean = re.sub(r'esr$', '', v)
        clean = re.sub(r'b\d+$', '', clean)
        return version.parse(clean)

    if channel == "esr":
        valid_versions = [v for v in versions if "esr" in v]
    elif channel == "release":
        valid_versions = [v for v in versions if "esr" not in v and "b" not in v]
    else:
        valid_versions = versions

    if not valid_versions:
        return None

    valid_versions.sort(key=parse_ver, reverse=True)
    return valid_versions[0]


def get_download_url(tb_version: str, lang: str = "en-US") -> Optional[str]:
    """取得指定版本的下載 URL"""
    url = f"{MOZILLA_FTP_BASE}/{tb_version}/linux-x86_64/"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error checking version directory: {e}", file=sys.stderr)
        return None

    tarball_pattern = re.compile(r'href="(/pub/thunderbird/releases/' + re.escape(tb_version) + r'/linux-x86_64/[^"]+thunderbird-' + re.escape(tb_version) + r'\.tar\.[a-z]+)"')
    match = tarball_pattern.search(resp.text)

    if match:
        return f"https://releases.mozilla.org{match.group(1)}"

    lang_url = f"{url}{lang}/"
    try:
        resp = requests.get(lang_url, timeout=30)
        if resp.status_code == 200:
            tarball_pattern = re.compile(r'href="(/pub/thunderbird/releases/' + re.escape(tb_version) + r'/linux-x86_64/[^"]+thunderbird-' + re.escape(tb_version) + r'\.tar\.[a-z]+)"')
            match = tarball_pattern.search(resp.text)
            if match:
                return f"https://releases.mozilla.org{match.group(1)}"
    except requests.RequestException:
        pass

    return None


def check_for_update(install_path: str = DEFAULT_INSTALL_PATH, channel: str = "release") -> Tuple[Optional[str], Optional[str]]:
    """檢查是否有更新，回傳 (最新版本, 下載URL)"""
    local_ver = get_local_version(install_path)
    latest_ver = fetch_latest_version(channel)

    if not latest_ver:
        return None, None

    needs_update = True
    if local_ver:
        try:
            needs_update = version.parse(latest_ver) > version.parse(local_ver)
        except Exception:
            needs_update = True

    download_url = get_download_url(latest_ver) if needs_update else None
    return (latest_ver, download_url) if needs_update else (None, None)


def get_cache_path(version: str, cache_dir: str) -> str:
    """取得 cache 檔案路徑"""
    return os.path.join(cache_dir, f"thunderbird-{version}.tar.xz")


def verify_cache_integrity(cache_path: str, url: str) -> bool:
    """驗證 cache 檔案完整性"""
    if not os.path.exists(cache_path):
        return False

    local_size = os.path.getsize(cache_path)
    if local_size == 0:
        return False

    try:
        resp = requests.head(url, timeout=30)
        server_size = int(resp.headers.get('content-length', 0))
        if server_size > 0 and local_size != server_size:
            print(f"Cache size mismatch: local={local_size}, server={server_size}")
            os.remove(cache_path)
            return False
    except Exception as e:
        print(f"Warning: Could not verify cache: {e}")

    try:
        result = subprocess.run(
            ["tar", "-Jtf", cache_path],
            capture_output=True,
            timeout=30,
            check=True
        )
    except Exception:
        print("Cache archive corrupted, removing...")
        os.remove(cache_path)
        return False

    return True


def check_cache(version: str, url: str, cache_dir: str) -> Optional[str]:
    """檢查 cache 目錄是否有完整檔案"""
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
        return None

    cache_path = get_cache_path(version, cache_dir)
    if verify_cache_integrity(cache_path, url):
        print(f"Using cached: {cache_path}")
        return cache_path
    return None


def download(url: str, version: str, cache_dir: str = DEFAULT_CACHE_DIR, no_cache: bool = False) -> Optional[str]:
    """下載檔案，回傳下載後的檔案路徑"""
    os.makedirs(cache_dir, exist_ok=True)

    cache_path = get_cache_path(version, cache_dir)
    if not no_cache and verify_cache_integrity(cache_path, url):
        print(f"Using cached: {cache_path}")
        return cache_path

    filename = os.path.basename(url)
    filepath = os.path.join(cache_dir, filename)

    print(f"Downloading: {url}")
    try:
        with requests.get(url, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get('content-length', 0))
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            print(f"\rProgress: {pct}%", end='', flush=True)
        print(f"\nDownloaded: {filename}")

        if verify_cache_integrity(filepath, url):
            return filepath
        else:
            print("Downloaded file verification failed", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        if os.path.exists(filepath):
            os.remove(filepath)
        return None


def install(archive_path: str, target_dir: str = DEFAULT_INSTALL_PATH) -> bool:
    """解壓並安裝 Thunderbird"""
    if not os.path.exists(archive_path):
        print(f"Archive not found: {archive_path}", file=sys.stderr)
        return False

    use_sudo = not target_dir.startswith("/tmp") and not target_dir.startswith("/home")
    archive_name = os.path.basename(archive_path)
    print(f"Extracting {archive_name}...")

    extract_dir = os.path.dirname(archive_path)

    sudo = ["sudo"] if use_sudo else []

    try:
        if archive_name.endswith(".xz"):
            subprocess.run(sudo + ["tar", "-Jxvf", archive_path], cwd=extract_dir, check=True)
        elif archive_name.endswith(".bz2"):
            subprocess.run(sudo + ["tar", "-jxvf", archive_path], cwd=extract_dir, check=True)
        elif archive_name.endswith(".gz"):
            subprocess.run(sudo + ["tar", "-zxvf", archive_path], cwd=extract_dir, check=True)
        else:
            print(f"Unknown archive format: {archive_name}", file=sys.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        return False

    extracted_folder = os.path.join(extract_dir, "thunderbird")
    if not os.path.exists(extracted_folder):
        print(f"Extracted folder not found: {extracted_folder}", file=sys.stderr)
        return False

    if os.path.exists(target_dir):
        print(f"Removing old installation: {target_dir}")
        subprocess.run(sudo + ["rm", "-rf", target_dir], check=True)

    print(f"Moving to {target_dir}")
    subprocess.run(sudo + ["mv", extracted_folder, target_dir], check=True)

    os.remove(archive_path)
    print(f"Thunderbird {target_dir} installed successfully!")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Thunderbird Updater")
    parser.add_argument("--install-path", default=DEFAULT_INSTALL_PATH,
                        help=f"Thunderbird installation path (default: {DEFAULT_INSTALL_PATH})")
    parser.add_argument("--channel", choices=["release", "esr"], default="release",
                        help="Update channel (default: release)")
    parser.add_argument("--force", action="store_true",
                        help="Force update without checking version")
    parser.add_argument("--download-only", action="store_true",
                        help="Only download, skip installation")
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR,
                        help=f"Cache directory (default: {DEFAULT_CACHE_DIR})")
    parser.add_argument("--no-cache", action="store_true",
                        help="Skip cache, always download fresh")
    args = parser.parse_args()

    print(f"Checking for updates (channel: {args.channel})...")

    if args.force:
        latest_ver = fetch_latest_version(args.channel)
        download_url = get_download_url(latest_ver) if latest_ver else None
    else:
        latest_ver, download_url = check_for_update(args.install_path, args.channel)

    if not latest_ver:
        print("Unable to fetch latest version.")
        sys.exit(1)

    local_ver = get_local_version(args.install_path)

    if not download_url:
        print(f"Already up-to-date: {local_ver}")
        sys.exit(0)

    print(f"Local version:  {local_ver or 'Not installed'}")
    print(f"Latest version: {latest_ver}")
    print(f"Download URL: {download_url}")

    archive_path = download(download_url, latest_ver, args.cache_dir, args.no_cache)
    if not archive_path:
        print("Download failed!")
        sys.exit(1)

    if args.download_only:
        print(f"Downloaded to: {archive_path}")
        sys.exit(0)

    if install(archive_path, args.install_path):
        sys.exit(0)
    else:
        print("Installation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()