import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.generate import country_codes, fetch_country

class GeneratorTest(unittest.TestCase):
    def test_country_codes_come_from_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps({"countries": {"US": {}, "IR": {}}}))
            self.assertEqual(country_codes(path), ["IR", "US"])

    @patch("scripts.generate.urllib.request.urlopen")
    def test_fetch_country_reads_ripestat_resources(self, urlopen):
        payload = {"status": "ok", "data": {"resources": {"ipv4": ["5.22.0.0/17"], "ipv6": ["2001:db8::/32"]}}}
        with patch("scripts.generate.json.load", return_value=payload):
            self.assertEqual(fetch_country("IR"), ("IR", ["5.22.0.0/17"], ["2001:db8::/32"]))

if __name__ == "__main__":
    unittest.main()

