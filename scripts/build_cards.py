#!/usr/bin/env python3
"""
Auto-builds static mobile contact pages and .vcf files from Keystatic CMS JSON files
located in content/cards/*.json.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = ROOT / "content" / "cards"
PUBLIC_VCF_DIR = ROOT / "public" / "vcf"
PUBLIC_VCF_DIR.mkdir(parents=True, exist_ok=True)


def fold_vcard_line(line: str, width: int = 75) -> str:
    """Fold long lines per RFC 2426 / vCard 3.0 spec."""
    if len(line) <= width:
        return line
    chunks = [line[:width]]
    rest = line[width:]
    while rest:
        chunks.append(" " + rest[: width - 1])
        rest = rest[width - 1 :]
    return "\r\n".join(chunks)


def generate_vcf(card: dict) -> str:
    addr = card.get("address", {})
    building = addr.get("building", "Shield House, Ground Floor")
    street = addr.get("street", "294 High Street")
    city = addr.get("city", "Aldershot")
    postcode = addr.get("postcode", "GU12 4LT")
    country = addr.get("country", "United Kingdom")

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{card['lastName']};{card['firstName']};;;",
        f"FN:{card['fullName']}",
        f"ORG:{card['company']}",
        f"TITLE:{card['jobTitle']}",
        f"TEL;TYPE=CELL,VOICE,PREF:{card['mobile']}",
        f"EMAIL;TYPE=INTERNET,WORK,PREF:{card['email']}",
        f"URL;TYPE=WORK:{card['website']}",
        f"ADR;TYPE=WORK:;;{building}, {street};{city};;{postcode};{country}",
        f"X-SOCIALPROFILE;TYPE=linkedin:{card['linkedin']}",
        f"ITEM1.URL:{card['linkedin']}",
        "ITEM1.X-ABLabel:LinkedIn",
    ]

    # Embed portrait photo in vCard so iOS/Android automatically populate contact photo
    photo_rel = card.get("photoVcf", "/images/nicky-stokes-vcf.jpg").lstrip("/")
    photo_path = ROOT / "public" / photo_rel
    if photo_path.exists():
        b64_photo = base64.b64encode(photo_path.read_bytes()).decode("ascii")
        photo_line = f"PHOTO;ENCODING=b;TYPE=JPEG:{b64_photo}"
        lines.append(fold_vcard_line(photo_line))

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def main():
    for card_file in sorted(CARDS_DIR.glob("*.json")):
        card = json.loads(card_file.read_text(encoding="utf-8"))
        vcf_content = generate_vcf(card)
        slug = card["slug"]
        vcf_filename = f"{card['firstName'].lower()}-{card['lastName'].lower()}.vcf"
        out_vcf = PUBLIC_VCF_DIR / vcf_filename
        out_vcf.write_text(vcf_content, encoding="utf-8")
        print(f"Generated vCard ({len(vcf_content)} bytes): {out_vcf}")


if __name__ == "__main__":
    main()
