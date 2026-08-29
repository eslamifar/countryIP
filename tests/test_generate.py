import ipaddress
import unittest

from scripts.generate import parse_records


class ParseRecordsTest(unittest.TestCase):
    def test_ipv4_range_is_converted_to_minimal_cidrs(self):
        rows = ["ripencc|IR|ipv4|5.22.0.0|1024|20200101|allocated"]
        parsed = parse_records(rows)
        self.assertEqual(parsed["IR"][4], {ipaddress.ip_network("5.22.0.0/22")})

    def test_ignores_summary_and_available_rows(self):
        rows = [
            "2|ripencc|20260829|0|0|0|0",
            "arin|US|ipv4|192.0.2.0|256|20200101|available",
        ]
        self.assertEqual(dict(parse_records(rows)), {})


if __name__ == "__main__":
    unittest.main()

