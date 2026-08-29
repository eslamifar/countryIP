# Country IP Lists

Daily IPv4 and IPv6 CIDR lists for every country, built directly from the official delegated statistics of AFRINIC, APNIC, ARIN, LACNIC, and RIPE NCC.

## Usage

The Iran compatibility file remains available at:

```text
iran_ipv4.txt
```

Every country also has a separate file using its lowercase two-letter ISO code:

```text
docs/data/ipv4/ir.txt
docs/data/ipv4/de.txt
docs/data/ipv4/us.txt
docs/data/ipv6/ir.txt
```

After GitHub Pages is enabled, the browser endpoint accepts query parameters:

```text
https://OWNER.github.io/REPOSITORY/?country=IR&version=4
```

For scripts, use the raw text file instead of parsing the web page:

```bash
curl -fsSL https://raw.githubusercontent.com/OWNER/REPOSITORY/main/docs/data/ipv4/de.txt
```

Country codes and prefix counts are listed in `docs/data/manifest.json`.

## Generate locally

Python 3.11+ is sufficient; there are no third-party dependencies.

```bash
python -m unittest discover -v
python scripts/generate.py
```

The GitHub Actions workflow regenerates and commits the lists every day. Data reflects RIR allocations/assignments and is not geolocation; actual routing or user location may differ.

## License

Code is released under the MIT License. The generated records originate from the five Regional Internet Registries listed in the manifest.
