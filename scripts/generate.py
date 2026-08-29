#!/usr/bin/env python3
"""Build per-country IP prefix files from the five official RIR statistics."""

from __future__ import annotations

import argparse
import ipaddress
import json
import shutil
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SOURCES = {
    "afrinic": "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest",
    "apnic": "https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest",
    "arin": "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    "lacnic": "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",
    "ripencc": "https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-extended-latest",
}


def parse_records(lines):
    """Return {country: {4: networks, 6: networks}} from delegated-stat lines."""
    result = defaultdict(lambda: {4: set(), 6: set()})
    for raw in lines:
        if not raw or raw.startswith(("#", "2|")):
            continue
        parts = raw.strip().split("|")
        if len(parts) < 7:
            continue
        _, country, resource_type, start, value, _, status = parts[:7]
        country = country.upper()
        if len(country) != 2 or not country.isalpha() or status not in {"allocated", "assigned"}:
            continue
        try:
            if resource_type == "ipv4":
                first = ipaddress.IPv4Address(start)
                last = ipaddress.IPv4Address(int(first) + int(value) - 1)
                result[country][4].update(ipaddress.summarize_address_range(first, last))
            elif resource_type == "ipv6":
                result[country][6].add(ipaddress.IPv6Network(f"{start}/{value}", strict=False))
        except (ValueError, ipaddress.AddressValueError):
            continue
    return result


def download(url: str) -> list[str]:
    request = urllib.request.Request(url, headers={"User-Agent": "country-ip-lists/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace").splitlines()


def merge(target, incoming):
    for country, versions in incoming.items():
        target[country][4].update(versions[4])
        target[country][6].update(versions[6])


def write_list(path: Path, networks) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(networks, key=lambda network: (int(network.network_address), network.prefixlen))
    path.write_text("".join(f"{network}\n" for network in ordered), encoding="ascii")


def build(output: Path) -> None:
    records = defaultdict(lambda: {4: set(), 6: set()})
    for url in SOURCES.values():
        merge(records, parse_records(download(url)))

    data_dir = output / "data"
    if data_dir.exists():
        shutil.rmtree(data_dir)
    manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "sources": SOURCES, "countries": {}}
    for country in sorted(records):
        lower = country.lower()
        write_list(data_dir / "ipv4" / f"{lower}.txt", records[country][4])
        write_list(data_dir / "ipv6" / f"{lower}.txt", records[country][6])
        manifest["countries"][country] = {
            "ipv4_prefixes": len(records[country][4]),
            "ipv6_prefixes": len(records[country][6]),
        }
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(data_dir / "ipv4" / "ir.txt", Path("iran_ipv4.txt"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("docs"))
    build(parser.parse_args().output)

