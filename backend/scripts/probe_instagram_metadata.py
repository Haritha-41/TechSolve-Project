import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


FIELDS = (
    "id",
    "title",
    "channel",
    "uploader",
    "view_count",
    "play_count",
    "video_view_count",
    "like_count",
    "comment_count",
    "duration",
    "upload_date",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Instagram Reel metadata returned by yt-dlp.")
    parser.add_argument("urls", nargs="+", help="Instagram Reel/Post URLs to inspect")
    parser.add_argument(
        "--cookies",
        default="",
        help="Netscape cookies.txt path. Defaults to INSTAGRAM_COOKIES_FILE from backend/.env.",
    )
    args = parser.parse_args()

    backend_dir = Path(__file__).resolve().parents[1]
    load_dotenv(backend_dir / ".env")

    cookies_file = args.cookies or os.environ.get("INSTAGRAM_COOKIES_FILE", "")
    options = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "ignore_no_formats_error": True,
    }
    using_cookies = False
    if cookies_file and Path(cookies_file).expanduser().exists():
        options["cookiefile"] = cookies_file
        using_cookies = True
    elif cookies_file:
        print(f"Cookie file does not exist, probing without cookies: {cookies_file}", file=sys.stderr)

    had_error = False
    for url in args.urls:
        result = {"url": url, "using_cookies": using_cookies}
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
            result.update({field: info.get(field) for field in FIELDS})
        except DownloadError as exc:
            had_error = True
            result["error"] = str(exc)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
