#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

from src.app import create_app, score_sentiment, resolve_symbol
from src.db import db
from src.models import SocialMention

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

FINNHUB_PROFILE_URL = "https://finnhub.io/api/v1/stock/profile2"

def get_company_name(symbol: str) -> str:
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return ""

    try:
        r = requests.get(
            FINNHUB_PROFILE_URL,
            params={"symbol": symbol, "token": api_key},
            timeout=10,
        )
        r.raise_for_status()
        return (r.json().get("name") or "").strip()
    except Exception:
        return ""

def parse_gdelt_datetime(s: str) -> datetime:
    """
    GDELT seendate example: 20260127T183000Z (UTC)
    """
    # Normalize just in case
    s = (s or "").strip()
    return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


def fetch_gdelt_articles(query: str, company: str = "", max_records: int = 250):
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "timespan": "1d",
        "maxrecords": str(max_records),
        "sort": "DateDesc",
    }

    headers = {
        "User-Agent": "CU-Boulder-Academic-Project/1.0 (sentiment scraper; contact: joelcomberiati@gmail.com)"
    }

    # Up to 2 attempts; wait if we get 429
    for attempt in range(2):
        r = requests.get(GDELT_DOC_URL, params=params, headers=headers, timeout=15)

        if r.status_code == 429:
            # GDELT asks for 1 request per 5 seconds
            time.sleep(6)
            continue

        content_type = (r.headers.get("Content-Type") or "").lower()
        if r.status_code != 200 or "json" not in content_type:
            preview = (r.text or "")[:200].replace("\n", " ")
            lower_preview = preview.lower()

            # If GDELT says the phrase is too short, retry with company-only query (most reliable)
            if "phrase is too short" in lower_preview and company and len(company) >= 4:
                safe_params = dict(params)
                safe_params["query"] = f'"{company}"'
                r2 = requests.get(GDELT_DOC_URL, params=safe_params, headers=headers, timeout=15)

                ct2 = (r2.headers.get("Content-Type") or "").lower()
                if r2.status_code == 200 and "json" in ct2:
                    return r2.json().get("articles", [])

                preview2 = (r2.text or "")[:200].replace("\n", " ")
                raise RuntimeError(
                    f"GDELT retry non-JSON: status={r2.status_code} content-type={ct2} preview={preview2}"
                )

            raise RuntimeError(
                f"GDELT non-JSON response: status={r.status_code} content-type={content_type} preview={preview}"
            )

        return r.json().get("articles", [])
    
    


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fetch_news_gdelt <ticker-or-company>")
        sys.exit(1)

    user_input = sys.argv[1]
    canonical = resolve_symbol(user_input)  # returns e.g., AAPL or AAPL.US
    canonical = canonical.split(".")[0]     # make it canonical like AAPL

    since = datetime.now(timezone.utc) - timedelta(days=1)

    company = get_company_name(canonical)

    # Build a permissive query that actually returns results
    terms = []

    company_term = (company or "").strip()
    if company_term:
        # broaden company term a bit
        for suffix in [" Inc", " Inc.", " Corporation", " Corp", " Corp.", " Ltd", " Ltd."]:
            company_term = company_term.replace(suffix, "")
        company_term = company_term.strip()
        if len(company_term) >= 4:
            terms.append(company_term)  # unquoted broad match

    if canonical:
        terms.append(canonical)  # ticker token

    # Build query with correct parentheses rules for GDELT
    if len(terms) >= 2:
        query = "(" + " OR ".join(terms) + ")"
    elif len(terms) == 1:   
        query = terms[0]
    else:
        raise RuntimeError("Could not build a GDELT query (no terms).")

    print("GDELT query:", query)

    print("since:", since.isoformat())

    skipped_dupe = 0
    skipped_time = 0
    app = create_app()
    with app.app_context():
        articles = fetch_gdelt_articles(query=query, company=company, max_records=50)
        print(f"GDELT returned {len(articles)} articles")
        for a in articles[:3]:
            print("sample:", a.get("seendate"), a.get("title"), a.get("url"))
        added = 0
        for a in articles:
            url = a.get("url")
            title = a.get("title") or ""
            seendate = a.get("seendate")  # e.g. 20260127153000

            if not url or not seendate:
                continue

            try:
                created_at = parse_gdelt_datetime(seendate)
            except Exception:
                continue

            if created_at < since:
                skipped_time += 1
                continue

            # Deduplicate by (platform, url)
            exists = SocialMention.query.filter_by(platform="news", url=url, symbol=canonical).first()
            if exists:
                skipped_dupe += 1
                continue

            text = title.strip()
            sent = score_sentiment(text)

            m = SocialMention(
                platform="news",
                source="gdelt",
                symbol=canonical,
                created_at=created_at.replace(tzinfo=None),  # store naive UTC like your other code
                text=text,
                url=url,
                sentiment=sent,
            )
            db.session.add(m)
            added += 1

        db.session.commit()
        print(f"Stored {added} news mentions for {canonical} (last 24h). "
            f"Skipped {skipped_dupe} duplicates, {skipped_time} older-than-24h.")

if __name__ == "__main__":
    main()