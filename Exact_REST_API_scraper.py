from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup, Tag


# =========================
# CONFIG
# =========================
# Output is always written to metadata/exact/ next to this script.
METADATA_DIR: Path = Path(__file__).resolve().parent / "metadata" / "exact"
TIMEOUT_SECONDS: int = 30
KEEP_COLUMNS: List[str] = ["Name", "Type", "Description"]  # case-insensitive match
# =========================


def derive_output_path(url: str) -> Path:
    """Extract the endpoint name from the URL's `name` query parameter
    and return the corresponding metadata/exact/<name>.csv path."""
    qs = parse_qs(urlparse(url).query)
    names = qs.get("name", [])
    if not names or not names[0]:
        raise ValueError(
            f"URL has no 'name' query parameter — cannot derive output filename: {url}"
        )
    return METADATA_DIR / f"{names[0]}.csv"


@dataclass
class ParsedCell:
    text: str
    alts: List[str]


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse_cell(cell: Tag) -> ParsedCell:
    alts: List[str] = []
    for img in cell.select("img[alt]"):
        alts.append(normalize_space(img.get("alt", "")))
    text = normalize_space(cell.get_text(" ", strip=True))
    # Remove common sort-arrow artifacts if they appear in header
    text = normalize_space(re.sub(r"[↑↓]+", "", text))
    return ParsedCell(text=text, alts=alts)


def expand_row_cells(tr: Tag) -> List[Tag]:
    expanded: List[Tag] = []
    for c in tr.find_all(["th", "td"], recursive=False):
        colspan = c.get("colspan")
        n = int(colspan) if colspan and str(colspan).isdigit() else 1
        expanded.extend([c] * max(n, 1))
    return expanded


def find_properties_table(soup: BeautifulSoup) -> Tag:
    candidates: List[Tuple[int, Tag]] = []
    for table in soup.find_all("table"):
        header_cells: List[str] = []
        thead = table.find("thead")
        if thead:
            header_cells = [normalize_space(x.get_text(" ", strip=True)) for x in thead.find_all(["th", "td"])]
        else:
            first_tr = table.find("tr")
            if first_tr:
                header_cells = [normalize_space(x.get_text(" ", strip=True)) for x in first_tr.find_all(["th", "td"])]

        if not header_cells:
            continue

        header_join = " | ".join(header_cells).lower()
        if "name" in header_join and "mandatory" in header_join and "description" in header_join:
            score = sum(tok in header_join for tok in ["value type", "value", "webhook"])
            candidates.append((score, table))

    if not candidates:
        raise RuntimeError("Could not locate the Properties table (layout may have changed).")

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def build_headers(header_tr: Tag) -> List[str]:
    """
    Keep *all* columns. If a header is blank/icon-only, create a stable placeholder.
    """
    header_cells = expand_row_cells(header_tr)
    parsed = [parse_cell(th) for th in header_cells]

    headers: List[str] = []
    for i, p in enumerate(parsed, start=1):
        h = p.text

        # If header text is empty, try to name it from icon alt text (if any)
        if not h and p.alts:
            # Example alts might include "Image: Mandatory" etc.
            # Make it a safe column name:
            alt = p.alts[0]
            alt = re.sub(r"^image:\s*", "", alt, flags=re.IGNORECASE)
            alt = normalize_space(alt).lower().replace(" ", "_")
            h = f"__{alt}" if alt else ""

        # If still empty, assign placeholder name
        if not h:
            h = f"__col_{i:02d}"

        # Ensure uniqueness (rare but can happen)
        base = h
        k = 2
        while h in headers:
            h = f"{base}_{k}"
            k += 1

        headers.append(h)

    return headers


def scrape_properties(url: str, timeout: int) -> Tuple[List[str], List[dict]]:
    headers_req = {
        "User-Agent": "Mozilla/5.0 (compatible; ExactDocsTableScraper/1.1)",
        "Accept": "text/html,application/xhtml+xml",
    }
    resp = requests.get(url, headers=headers_req, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    table = find_properties_table(soup)

    header_tr = table.find("tr")
    if header_tr is None:
        raise RuntimeError("Properties table has no rows.")
    headers = build_headers(header_tr)

    rows: List[dict] = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue

        expanded_tds = expand_row_cells(tr)
        parsed = [parse_cell(td) for td in expanded_tds]

        # Pad/truncate to header length WITHOUT shifting
        values = [p.text for p in parsed]
        if len(values) < len(headers):
            values += [""] * (len(headers) - len(values))
        elif len(values) > len(headers):
            values = values[: len(headers)]

        row = {headers[i]: values[i] for i in range(len(headers))}
        rows.append(row)

    # ── Keep only the columns we care about (case-insensitive) ──
    keep_lower = {c.lower() for c in KEEP_COLUMNS}
    final_headers = [h for h in headers if h.lower() in keep_lower]
    rows = [{k: v for k, v in row.items() if k.lower() in keep_lower} for row in rows]

    return final_headers, rows


def write_csv(path: Path, headers: List[str], rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Scrape an Exact Online REST API endpoint details page into a "
            "metadata CSV. The output filename is derived from the URL's "
            "`name` query parameter and written to metadata/exact/."
        )
    )
    parser.add_argument(
        "url",
        help=(
            "Endpoint details page URL, e.g. "
            "https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx"
            "?name=SubscriptionSubscriptionLines"
        ),
    )
    args = parser.parse_args()

    out_path = derive_output_path(args.url)
    headers, rows = scrape_properties(args.url, timeout=TIMEOUT_SECONDS)
    write_csv(out_path, headers, rows)
    print(f"OK: wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()