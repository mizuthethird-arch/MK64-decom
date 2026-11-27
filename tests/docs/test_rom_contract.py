import hashlib
import re
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = SOURCE_ROOT / "docs" / "rom-contract.md"
ROM_PATH = SOURCE_ROOT / "rom" / "Mario Kart 64 (Europe) (Rev A).n64"

PINNED_SIZE = 12582912
PINNED_Z64_SHA1 = "f6b5f519dd57ea59e9f013cc64816e9d273b2329"
PINNED_LOCAL_SHA1 = "f18317bfd7fbcaea6cfbfcb9c4ae3c7c7d1d66c7"
PINNED_NAME = "MARIOKART64"
PINNED_CART_ID = "NKT"
PINNED_COUNTRY = "P"
PINNED_REVISION = 1
Z64_MAGIC = bytes.fromhex("80371240")
ROM_PRESENT = ROM_PATH.is_file()
ROM_ABSENT_REASON = "user-supplied ROM not present: this check reads the real image"


def swap_16(raw):
    swapped = bytearray(raw)
    swapped[0::2], swapped[1::2] = raw[1::2], raw[0::2]
    return bytes(swapped)


def header_field(z64, start, end):
    return z64[start:end].decode("ascii", "replace")


def contract_text():
    return CONTRACT_PATH.read_text(encoding="utf-8")


class ContractExistsTest(unittest.TestCase):
    def test_the_contract_is_written(self):
        self.assertTrue(CONTRACT_PATH.is_file(), f"{CONTRACT_PATH} must exist")


@unittest.skipUnless(ROM_PRESENT, ROM_ABSENT_REASON)
class PinnedImageTest(unittest.TestCase):
    def test_the_local_rom_is_the_pinned_size(self):
        self.assertEqual(ROM_PATH.stat().st_size, PINNED_SIZE)

    def test_the_local_rom_hashes_to_the_pinned_v64_sha1(self):
        self.assertEqual(hashlib.sha1(ROM_PATH.read_bytes()).hexdigest(), PINNED_LOCAL_SHA1)

    def test_the_local_rom_is_accepted_after_the_16_bit_byteswap(self):
        z64 = swap_16(ROM_PATH.read_bytes())
        self.assertEqual(hashlib.sha1(z64).hexdigest(), PINNED_Z64_SHA1)
        self.assertEqual(z64[:4], Z64_MAGIC)
        self.assertEqual(header_field(z64, 0x20, 0x34).rstrip("\x00 "), PINNED_NAME)
        self.assertEqual(header_field(z64, 0x3B, 0x3E), PINNED_CART_ID)
        self.assertEqual(header_field(z64, 0x3E, 0x3F), PINNED_COUNTRY)
        self.assertEqual(z64[0x3F], PINNED_REVISION)

    def test_the_local_rom_is_not_accepted_before_the_byteswap(self):
        raw = ROM_PATH.read_bytes()
        self.assertNotEqual(hashlib.sha1(raw).hexdigest(), PINNED_Z64_SHA1)
        self.assertNotEqual(raw[:4], Z64_MAGIC)

    def test_a_32_bit_byteswap_does_not_reach_the_pin(self):
        raw = ROM_PATH.read_bytes()
        word_swapped = b"".join(raw[i:i + 4][::-1] for i in range(0, len(raw), 4))
        self.assertNotEqual(hashlib.sha1(word_swapped).hexdigest(), PINNED_Z64_SHA1)
        self.assertNotEqual(word_swapped[:4], Z64_MAGIC)


class MismatchBehaviourTest(unittest.TestCase):
    def setUp(self):
        self.text = contract_text()

    def test_the_contract_describes_the_wrong_size_rejection(self):
        self.assertIn("wrong size", self.text.lower())
        self.assertIn("12,582,912", self.text)

    def test_the_contract_describes_the_wrong_sha1_rejection(self):
        self.assertIn("wrong sha1", self.text.lower())
        self.assertIn(PINNED_Z64_SHA1, self.text)

    def test_the_contract_says_the_importer_never_guesses(self):
        self.assertIn("never guess", self.text.lower())

    def test_the_contract_names_which_check_failed(self):
        for check in ("size", "sha1", "byte order"):
            self.assertIn(check, self.text.lower(), check)

    def test_the_contract_names_the_three_byte_orders(self):
        for order in ("z64", "v64", "32-bit"):
            self.assertIn(order, self.text.lower(), order)

    def test_the_contract_states_the_path_only_rule(self):
        self.assertIn("path", self.text.lower())
        self.assertIn("never copied", self.text.lower())
        self.assertIn("never renamed", self.text.lower())

    def test_the_contract_states_the_derived_image_is_never_committed(self):
        self.assertIn("derived", self.text.lower())
        self.assertIn("never committed", self.text.lower())

    def test_the_contract_declares_which_checks_are_prose_only(self):
        self.assertIn("prose", self.text.lower())

    def test_the_contract_carries_the_unverified_name_note(self):
        self.assertIn("unverified: awaiting cartridge check", self.text)
        self.assertIn("T0002", self.text)

    def test_the_contract_is_linked_from_the_rom_page(self):
        rom_page = (SOURCE_ROOT / "docs" / "rom.md").read_text(encoding="utf-8")
        self.assertIn("rom-contract.md", rom_page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
