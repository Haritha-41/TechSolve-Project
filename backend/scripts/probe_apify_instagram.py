import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Instagram Reel metadata returned by Apify.")
    parser.add_argument("urls", nargs="+", help="Instagram Reel URLs to inspect")
    parser.add_argument("--username", default=None, help="Optional profile username for actors that require it")
    args = parser.parse_args()

    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))
    load_dotenv(backend_dir / ".env")

    from app.extractors.apify_instagram import fetch_apify_reel_metadata

    for url in args.urls:
        result = {"url": url, "metadata": fetch_apify_reel_metadata(url, args.username)}
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
