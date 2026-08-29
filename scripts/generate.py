#!/usr/bin/env python3
"""Build per-country prefix files with RIPEstat's country-resource-list API."""
from __future__ import annotations
import argparse
import json
import shutil
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

API = "https://stat.ripe.net/data/country-resource-list/data.json"
ALIASES = {"IR": "iran"}

def country_codes(manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return sorted(manifest["countries"])

def fetch_country(country: str) -> tuple[str, list[str], list[str]]:
    query = urllib.parse.urlencode({"resource": country, "v4_format": "prefix"})
    request = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": "countryIP/2.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.load(response)
    if payload.get("status") != "ok":
        raise RuntimeError(f"RIPEstat returned {payload.get('status')} for {country}")
    resources = payload["data"]["resources"]
    return country, sorted(set(resources.get("ipv4", []))), sorted(set(resources.get("ipv6", [])))

def write_list(path: Path, prefixes: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{prefix}\n" for prefix in prefixes), encoding="ascii")

def build(output: Path, workers: int = 6) -> None:
    codes = country_codes(output / "data" / "manifest.json")
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_country, code): code for code in codes}
        for future in as_completed(futures):
            country, ipv4, ipv6 = future.result()
            results[country] = {"ipv4": ipv4, "ipv6": ipv6}
    data_dir = output / "data"
    shutil.rmtree(data_dir / "ipv4", ignore_errors=True)
    shutil.rmtree(data_dir / "ipv6", ignore_errors=True)
    manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "source": API, "countries": {}}
    for country in codes:
        lower = country.lower()
        ipv4, ipv6 = results[country]["ipv4"], results[country]["ipv6"]
        write_list(data_dir / "ipv4" / f"{lower}.txt", ipv4)
        write_list(data_dir / "ipv6" / f"{lower}.txt", ipv6)
        write_list(Path(f"{lower}_ipv4.txt"), ipv4)
        write_list(Path(f"{lower}_ipv6.txt"), ipv6)
        manifest["countries"][country] = {"ipv4_prefixes": len(ipv4), "ipv6_prefixes": len(ipv6)}
    for code, name in ALIASES.items():
        shutil.copyfile(Path(f"{code.lower()}_ipv4.txt"), Path(f"{name}_ipv4.txt"))
        shutil.copyfile(Path(f"{code.lower()}_ipv6.txt"), Path(f"{name}_ipv6.txt"))
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("docs"))
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    build(args.output, args.workers)

