# Country IP Lists

IPv4 and IPv6 CIDR lists for every country, refreshed every six hours from RIPEstat's `country-resource-list` API.

## Usage

The Iran compatibility file remains available at:

```text
iran_ipv4.txt
```

Every country also has raw files in the repository root, using its lowercase two-letter ISO code:

```text
ir_ipv4.txt
de_ipv4.txt
us_ipv4.txt
de_ipv6.txt
```

After GitHub Pages is enabled, the browser endpoint accepts query parameters:

```text
https://eslamifar.github.io/countryIP/?country=IR&version=4
```

For scripts, use the raw text file instead of parsing the web page:

```bash
curl -fsSL https://raw.githubusercontent.com/eslamifar/countryIP/main/de_ipv4.txt
```

Country codes and prefix counts are listed in `docs/data/manifest.json`.

## Generate locally

Python 3.11+ is sufficient; there are no third-party dependencies.

```bash
python -m unittest discover -v
python scripts/generate.py
```

The GitHub Actions workflow regenerates and commits the lists every six hours. Data reflects registered country resources and is not geolocation; actual routing or user location may differ.

## License

Code is released under the MIT License. Generated records are retrieved from RIPEstat; the source endpoint is recorded in the manifest.
