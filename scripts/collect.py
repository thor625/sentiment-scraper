#!/usr/bin/env python3
import sys
import subprocess


def run(cmd: list[str]) -> int:
    """Run a command and echo it for quick debugging."""
    print("\n$ " + " ".join(cmd))
    return subprocess.run(cmd).returncode


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.collect <symbol-or-company>")
        sys.exit(1)

    symbol = sys.argv[1]

    quote_rc = run([sys.executable, "-m", "scripts.fetch_quote", symbol])
    news_rc  = run([sys.executable, "-m", "scripts.fetch_news_gdelt", symbol])

    print("\nSummary:")
    print("  fetch_quote exit code:", quote_rc)
    print("  fetch_news_gdelt exit code:", news_rc)

    # only fail if everything failed
    if quote_rc != 0 and news_rc != 0:
        sys.exit(1)
    print("\nDone. Now open:")
    print(f"  http://127.0.0.1:5000/report?symbol={symbol}")


if __name__ == "__main__":
    main()
