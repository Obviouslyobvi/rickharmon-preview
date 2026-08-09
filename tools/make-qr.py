#!/usr/bin/env python3
"""Generate the Rick Harmon contact QR code (vCard) and matching .vcf file.

Run from the repo root:

    pip install segno pyzbar opencv-python-headless pillow
    apt-get install -y libzbar0
    python3 tools/make-qr.py

Writes assets/qr.png and assets/rick-harmon.vcf, then audits both:

  * round trip -- the PNG is decoded by two independent engines (zbar, which is
    what most phone scanner apps are built on, and OpenCV) and must come back
    byte-for-byte identical to the vCard it was built from.
  * robustness -- the PNG is decoded again under 29 degradations that stand in
    for real-world scanning (small on screen, off-angle, blurred, compressed,
    low contrast, shadowed, misprinted, partly obscured) and must clear a
    minimum pass rate.
  * display width -- every value a phone shows in a single-line field is checked
    against FIELD_WINDOW, because a value longer than the box gets scrolled and
    the user sees only its tail.

Exits non-zero if any audit fails.
"""

import pathlib
import sys

import cv2
import numpy as np
import segno
from PIL import Image
from pyzbar.pyzbar import decode as zbar_decode

ROOT = pathlib.Path(__file__).resolve().parent.parent
PNG = ROOT / "assets" / "qr.png"
VCF = ROOT / "assets" / "rick-harmon.vcf"

# Contact apps render company in a single-line box roughly this wide. A longer
# value is not corrupted, but it scrolls to its end and the front of the string
# is hidden -- which is how "The Suburban Group Mortgage Bankers" came out
# looking like "ban Group Mortgage Bankers" on a real phone.
FIELD_WINDOW = 26

# ORG is a structured field: the components are organization name, then
# organizational unit. Splitting on that boundary is what the spec asks for, and
# it also means each component lands in its own box -- iOS maps them to Company
# and Department -- so neither one overflows and gets visually clipped.
ORG_NAME = "The Suburban Group"
ORG_UNIT = "Mortgage Bankers"

# vCard 3.0 is the widest-supported version across iOS Camera, Google Lens and
# the third-party scanners people actually have installed. Lines are joined with
# CRLF because RFC 6350 (and 2426 before it) require it -- bare LF is what trips
# up the stricter parsers and leaves fields blank or mangled.
LINES = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    "N:Harmon;Rick;;;",
    "FN:Rick Harmon",
    f"ORG:{ORG_NAME};{ORG_UNIT}",
    "TEL;TYPE=WORK,VOICE:+18007792552",
    "TEL;TYPE=WORK,FAX:+17145722611",
    "EMAIL;TYPE=WORK,INTERNET:Rharmon@closeprobate.com",
    "EMAIL;TYPE=WORK,INTERNET:Team@tsgmortgage.com",
    "URL:https://TSGMortgage.com",
    "ADR;TYPE=WORK:;;P. O. Box 9308;Brea;CA;92822-9308;United States",
    "END:VCARD",
]
VCARD = "\r\n".join(LINES) + "\r\n"

# Values a phone drops into a single-line field, and so worth width-checking.
# The street address is exempt: contact apps lay the address out over several
# lines, so it does not scroll the way a one-line box does.
DISPLAY_VALUES = {
    "full name": "Rick Harmon",
    "company": ORG_NAME,
    "department": ORG_UNIT,
    "work phone": "+18007792552",
    "work fax": "+17145722611",
    "email 1": "Rharmon@closeprobate.com",
    "email 2": "Team@tsgmortgage.com",
    "url": "https://TSGMortgage.com",
}

MIN_ROBUSTNESS = 0.90


def build():
    VCF.write_text(VCARD, encoding="utf-8", newline="")

    # error='M' recovers ~15% damage, versus the 'L' the original image used --
    # worth it for a code that gets photographed at an angle or printed small.
    # border=4 is the quiet zone the spec asks for; the original had a dark 1px
    # frame sitting in the middle of its quiet zone.
    qr = segno.make(VCARD, error="M", mode="byte")
    qr.save(PNG, scale=10, border=4, dark="#000000", light="#ffffff")
    return qr


def read_zbar(img):
    found = zbar_decode(Image.fromarray(img))
    return found[0].data.decode() if found else None


def read_opencv(img):
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return text or None


def check_round_trip(img):
    print("round trip")
    ok = True
    for name, reader in (("zbar", read_zbar), ("opencv", read_opencv)):
        got = reader(img)
        good = got == VCARD
        ok &= good
        print(f"  {name:8} {'exact match' if good else 'MISMATCH'}")
        if not good:
            print(f"           expected {VCARD!r}")
            print(f"           got      {got!r}")
    return ok


def rotated(img, deg):
    """Rotate into a canvas big enough to hold the result.

    Rotating a square inside a fixed canvas slices the corners off, and the
    corners are where three of the four finder patterns live -- so the code
    stops being findable for reasons that have nothing to do with the angle.
    """
    h, w = img.shape
    m = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    cos, sin = abs(m[0, 0]), abs(m[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    m[0, 2] += nw / 2 - w / 2
    m[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(img, m, (nw, nh), borderValue=255, flags=cv2.INTER_CUBIC)


def degradations(img):
    """Stand-ins for the ways a code actually gets photographed.

    Yields (name, image, required). Non-required cases are reported but do not
    count against the pass rate -- they cover conditions this code is never
    shipped in, and exist to document the edge rather than to gate on it.
    """
    def small(src, px):
        return cv2.resize(src, (px, px), interpolation=cv2.INTER_AREA)

    base = small(img, 320)
    h, w = base.shape

    for px in (600, 450, 320, 260, 200, 160):
        yield f"scaled to {px}px", small(img, px), px >= 200

    # Rotate at full resolution first, then downscale -- the order a camera does
    # it in. Rotating an already-small image just measures interpolation loss.
    for deg in (5, 10, 15, 25, 40, 60):
        yield f"rotated {deg} deg", small(rotated(img, deg), 320), True

    for k in (3, 5, 7):
        yield f"blurred {k}x{k}", cv2.GaussianBlur(base, (k, k), 0), True

    for q in (60, 35, 15):
        _, enc = cv2.imencode(".jpg", base, [cv2.IMWRITE_JPEG_QUALITY, q])
        yield f"jpeg quality {q}", cv2.imdecode(enc, cv2.IMREAD_GRAYSCALE), True

    for lo, hi in ((60, 200), (90, 170)):
        yield (f"contrast {lo}-{hi}",
               np.interp(base, (0, 255), (lo, hi)).astype(np.uint8), True)

    # Ink spread on a press, and ink starved.
    for label, op in (("ink spread", cv2.erode), ("ink starved", cv2.dilate)):
        yield label, op(base, np.ones((2, 2), np.uint8), iterations=1), True

    # A shadow falling across the code.
    gradient = np.linspace(1.0, 0.45, w, dtype=np.float32)[None, :]
    yield "shadow across it", (base * gradient).astype(np.uint8), True

    noisy = base.astype(np.int16) + np.tile(
        np.array([-28, 24, -18, 30], np.int16), (h, w // 4)
    )
    yield "sensor noise", np.clip(noisy, 0, 255).astype(np.uint8), True

    skewed = cv2.warpPerspective(
        base,
        cv2.getPerspectiveTransform(
            np.float32([[0, 0], [w, 0], [w, h], [0, h]]),
            np.float32([[18, 10], [w - 6, 0], [w - 20, h - 8], [4, h]]),
        ),
        (w, h),
        borderValue=255,
    )
    yield "held at an angle", skewed, True

    # Physical damage -- a scuff or a thumb over part of the code. This is what
    # the error correction level is actually for.
    for pct in (5, 10):
        damaged = base.copy()
        side = int(w * (pct / 100) ** 0.5)
        damaged[h - side - 12:h - 12, w - side - 12:w - 12] = 255
        yield f"{pct}% obscured", damaged, True

    # Never shipped this way -- we always render dark-on-light -- but recorded
    # so the limit is visible rather than assumed.
    yield "inverted", 255 - base, False


def check_robustness(img):
    print("\nrobustness (decoded by either engine)")
    passed = cases = 0
    for name, variant, required in degradations(img):
        results = [read_zbar(variant), read_opencv(variant)]
        good = VCARD in results
        if required:
            cases += 1
            passed += good
        if good:
            engines = "+".join(
                e for e, r in zip(("zbar", "opencv"), results) if r == VCARD
            )
            note = "" if required else "  (not required)"
            print(f"  {name:22} ok    ({engines}){note}")
        else:
            verdict = "WRONG TEXT" if any(results) else "no read"
            note = "" if required else "  (not required)"
            print(f"  {name:22} {verdict}{note}")
    rate = passed / cases
    print(f"  => {passed}/{cases} required cases ({rate:.0%}), floor is {MIN_ROBUSTNESS:.0%}")
    return rate >= MIN_ROBUSTNESS


def check_display_widths():
    print(f"\ndisplay width (single-line fields, {FIELD_WINDOW}-char window)")
    ok = True
    for label, value in DISPLAY_VALUES.items():
        over = len(value) - FIELD_WINDOW
        ok &= over <= 0
        if over <= 0:
            print(f"  {label:12} {len(value):>3} chars  fits")
        else:
            print(f"  {label:12} {len(value):>3} chars  OVERFLOWS by {over}")
            print(f"  {'':12}     phone would show {value[-FIELD_WINDOW:]!r}")
    return ok


if __name__ == "__main__":
    qr = build()
    print(f"built {PNG.relative_to(ROOT)} and {VCF.relative_to(ROOT)}")
    print(
        f"version {qr.version} ({17 + 4 * qr.version}x{17 + 4 * qr.version} modules), "
        f"error correction {qr.error.upper()}, {len(VCARD)} bytes\n"
    )
    image = cv2.imread(str(PNG), cv2.IMREAD_GRAYSCALE)
    results = [check_round_trip(image), check_robustness(image), check_display_widths()]
    print("\n" + ("ALL CHECKS PASSED" if all(results) else "CHECKS FAILED"))
    sys.exit(0 if all(results) else 1)
