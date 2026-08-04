#!/usr/bin/env python3
"""Generate the Rick Harmon contact QR code (vCard) and matching .vcf file.

Run from the repo root:

    pip install segno
    python3 tools/make-qr.py

Writes assets/qr.png and assets/rick-harmon.vcf, then decodes the PNG back
and fails loudly if the round trip does not match the source vCard.
"""

import pathlib
import sys

import segno

ROOT = pathlib.Path(__file__).resolve().parent.parent
PNG = ROOT / "assets" / "qr.png"
VCF = ROOT / "assets" / "rick-harmon.vcf"

# vCard 3.0 is the widest-supported version across iOS Camera, Google Lens and
# the third-party scanners people actually have installed. Lines are joined with
# CRLF because RFC 6350 (and 2426 before it) require it -- bare LF is what trips
# up the stricter parsers and leaves fields blank or mangled.
LINES = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    "N:Harmon;Rick;;;",
    "FN:Rick Harmon",
    "ORG:The Suburban Group Mortgage Bankers",
    "TEL;TYPE=WORK,VOICE:+18007792552",
    "TEL;TYPE=WORK,FAX:+17145722611",
    "EMAIL;TYPE=WORK,INTERNET:Rharmon@closeprobate.com",
    "EMAIL;TYPE=WORK,INTERNET:Team@tsgmortgage.com",
    "URL:https://TSGMortgage.com",
    "ADR;TYPE=WORK:;;P. O. Box 9308;Brea;CA;92822-9308;United States",
    "END:VCARD",
]
VCARD = "\r\n".join(LINES) + "\r\n"


def build():
    VCF.write_text(VCARD, encoding="utf-8", newline="")

    # error='M' recovers ~15% damage, versus the 'L' the previous image used --
    # worth it for a code that gets photographed at an angle or printed small,
    # and it only grows the grid from 65 to 73 modules. border=4 is the quiet
    # zone the spec asks for; the previous image had a dark 1px frame sitting in
    # the middle of its quiet zone.
    qr = segno.make(VCARD, error="M", encoding="utf-8", mode="byte")
    qr.save(PNG, scale=10, border=4, dark="#000000", light="#ffffff")
    return qr


def verify():
    import cv2

    img = cv2.imread(str(PNG), cv2.IMREAD_GRAYSCALE)
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if decoded != VCARD:
        print("ROUND TRIP FAILED", file=sys.stderr)
        print(repr(decoded), file=sys.stderr)
        return False
    print(f"ok: {PNG.relative_to(ROOT)} decodes back to the exact vCard")
    return True


if __name__ == "__main__":
    qr = build()
    print(f"version {qr.version}, error correction {qr.error}, {len(VCARD)} bytes")
    sys.exit(0 if verify() else 1)
