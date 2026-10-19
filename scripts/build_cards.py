#!/usr/bin/env python3
"""
Auto-builds static multi-staff mobile contact pages, .vcf files, and Keystatic CMS
from Keystatic JSON files located in content/cards/*.json.
"""
import base64
import html
import json
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = ROOT / "content" / "cards"
PUBLIC_DIR = ROOT / "public"
PUBLIC_VCF_DIR = PUBLIC_DIR / "vcf"
PUBLIC_VCF_DIR.mkdir(parents=True, exist_ok=True)
DIST_DIR = ROOT / "dist"
TEMPLATE_FILE = ROOT / "scripts" / "card_template.html"


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
    slug = card.get("slug", "")
    custom_vcf_photo = PUBLIC_DIR / "images" / f"{slug}-vcf.jpg"
    if card.get("photoVcf"):
        photo_rel = card["photoVcf"].lstrip("/")
    elif custom_vcf_photo.exists():
        photo_rel = f"images/{slug}-vcf.jpg"
    elif card.get("photoCutout"):
        photo_rel = card["photoCutout"].lstrip("/")
    else:
        photo_rel = "images/nicky-stokes-vcf.jpg"

    photo_path = PUBLIC_DIR / photo_rel.replace("images/", "images/").replace("public/", "")

    if not photo_path.exists():
        photo_path = ROOT / photo_rel
    if photo_path.exists():
        b64_photo = base64.b64encode(photo_path.read_bytes()).decode("ascii")
        photo_line = f"PHOTO;ENCODING=b;TYPE=JPEG:{b64_photo}"
        lines.append(fold_vcard_line(photo_line))

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def render_card_html(template: str, card: dict) -> str:
    slug = card["slug"]
    full_name = html.escape(card["fullName"])
    first_name = html.escape(card["firstName"])
    last_name = html.escape(card["lastName"])
    job_title = html.escape(card["jobTitle"])
    company = html.escape(card["company"])
    mobile = html.escape(card["mobile"])
    mobile_dial = html.escape(card.get("mobileDial", card["mobile"].replace(" ", "")))
    email = html.escape(card["email"])
    website = card.get("website", "https://www.isd-tech.com")
    website_label = html.escape(card.get("websiteLabel", "isd-tech.com"))
    linkedin = card.get("linkedin", "https://www.linkedin.com/company/integrated-security-design-ltd/")
    linkedin_label = html.escape(card.get("linkedinLabel", "ISD Tech on LinkedIn"))

    addr = card.get("address", {})
    building = addr.get("building", "")
    street = addr.get("street", "")
    city = addr.get("city", "")
    postcode = addr.get("postcode", "")
    maps_query = addr.get("mapsQuery", f"{company}, {street}, {city}, {postcode}".replace(" ", "+"))
    address_lines = []
    if building:
        address_lines.append(html.escape(building))
    street_city_postcode = ", ".join(filter(None, [street, city, postcode]))
    if street_city_postcode:
        address_lines.append(html.escape(street_city_postcode))
    address_html = "<br />\n            ".join(address_lines)

    # Photo resolution
    photo_cutout = card.get("photoCutout", "/images/nicky-stokes-cutout.png")
    if not photo_cutout.startswith("/"):
        photo_cutout = "/" + photo_cutout
    photo_cutout_src = f"/public{photo_cutout}" if not photo_cutout.startswith("/public") else photo_cutout

    # VCF link
    vcf_path = f"/public/vcf/{slug}.vcf"
    vcf_download = f"{first_name}-{last_name}.vcf"

    card_url = card.get("cardUrl", f"https://cards.isd-tech.com/{slug}")
    display_url = card.get("displayUrl", card_url.replace("https://", "").replace("http://", "").rstrip("/"))

    # QR code: use custom image if it exists in public/images, otherwise high-res API
    qr_custom_path = PUBLIC_DIR / "images" / f"{slug}-qr.png"
    if qr_custom_path.exists():
        qr_img_src = f"/public/images/{slug}-qr.png"
    elif slug == "nstokes" and (PUBLIC_DIR / "images" / "nicky-qr.png").exists():
        qr_img_src = "/public/images/nicky-qr.png"
    else:
        encoded_url = urllib.parse.quote(card_url, safe="")
        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=620x620&amp;margin=10&amp;color=012250&amp;bgcolor=ffffff&amp;data={encoded_url}"

    replacements = {
        "__FULL_NAME__": full_name,
        "__FIRST_NAME__": first_name,
        "__LAST_NAME__": last_name,
        "__JOB_TITLE__": job_title,
        "__COMPANY__": company,
        "__MOBILE__": mobile,
        "__MOBILE_DIAL__": mobile_dial,
        "__EMAIL__": email,
        "__WEBSITE__": website,
        "__WEBSITE_LABEL__": website_label,
        "__LINKEDIN__": linkedin,
        "__LINKEDIN_LABEL__": linkedin_label,
        "__ADDRESS_HTML__": address_html,
        "__MAPS_QUERY__": maps_query,
        "__PHOTO_CUTOUT__": photo_cutout_src,
        "__VCF_PATH__": vcf_path,
        "__VCF_DOWNLOAD__": vcf_download,
        "__CARD_URL__": card_url,
        "__QR_IMG_SRC__": qr_img_src,
        "__DISPLAY_URL__": display_url,
    }

    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def make_redirect_page(target_url: str, title: str = "Redirecting...") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0; url={target_url}" />
  <link rel="canonical" href="{target_url}" />
  <script>window.location.replace("{target_url}");</script>
  <title>{html.escape(title)}</title>
</head>
<body style="font-family: -apple-system, sans-serif; text-align: center; padding: 40px; background: #012250; color: #ffffff;">
  <p>Redirecting to <a href="{target_url}" style="color: #01c3ff; font-weight: bold;">{html.escape(target_url)}</a>...</p>
</body>
</html>
"""


def build_keystatic():
    keystatic_dir = ROOT / "keystatic"
    if not (keystatic_dir / "index.html").exists():
        print("Keystatic source not found, skipping Keystatic build.")
        return

    print("Building Keystatic CMS SPA with Vite...")
    cmd = [
        "npx",
        "vite",
        "build",
        "keystatic",
        "--outDir",
        "../dist/keystatic",
        "--base",
        "/keystatic/",
        "--emptyOutDir",
    ]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print("Keystatic build error:", res.stderr)
    else:
        print("Keystatic CMS built successfully to dist/keystatic/.")
        # Clean up any legacy physical cloud directory if present so Netlify SPA rewrite handles it cleanly
        cloud_dir = DIST_DIR / "keystatic" / "cloud"
        if cloud_dir.exists():
            shutil.rmtree(cloud_dir)

        # Also generate canonical dist/_redirects for Netlify
        redirects_content = """# Keystatic SPA client-side routing
/keystatic/*    /keystatic/index.html   200

# Legacy path redirects to /nstokes
/vcard/nicky    /nstokes                301
/nicky          /nstokes                301

# Root redirects to primary card /nstokes
/               /nstokes                302
"""
        (DIST_DIR / "_redirects").write_text(redirects_content, encoding="utf-8")


def main():
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    cards = []
    for card_file in sorted(CARDS_DIR.glob("*.json")):
        card = json.loads(card_file.read_text(encoding="utf-8"))
        slug = card["slug"]
        cards.append(card)

        # 1. Generate vCard (.vcf)
        vcf_content = generate_vcf(card)
        out_vcf = PUBLIC_VCF_DIR / f"{slug}.vcf"
        out_vcf.write_text(vcf_content, encoding="utf-8")
        print(f"Generated vCard: {out_vcf}")

        # Also write legacy vcf name if nstokes
        if slug == "nstokes":
            legacy_vcf = PUBLIC_VCF_DIR / "nicky-stokes.vcf"
            legacy_vcf.write_text(vcf_content, encoding="utf-8")

        # 2. Render Card HTML to dist/<slug>/index.html
        card_html = render_card_html(template, card)
        card_dist = DIST_DIR / slug
        card_dist.mkdir(parents=True, exist_ok=True)
        (card_dist / "index.html").write_text(card_html, encoding="utf-8")
        print(f"Generated Card Page: dist/{slug}/index.html")

        # If nstokes, also generate legacy root index.html in repo root
        if slug == "nstokes":
            (ROOT / "index.html").write_text(card_html, encoding="utf-8")

    # 3. Root redirect dist/index.html -> /nstokes
    primary_slug = "nstokes" if any(c["slug"] == "nstokes" for c in cards) else cards[0]["slug"]
    root_redirect = make_redirect_page(f"/{primary_slug}", "ISD Tech Digital Business Cards")
    (DIST_DIR / "index.html").write_text(root_redirect, encoding="utf-8")
    print(f"Generated Root Redirect: dist/index.html -> /{primary_slug}")

    # 4. Backward compatibility redirects
    for alias in ["nicky", "vcard/nicky"]:
        alias_dir = DIST_DIR / alias
        alias_dir.mkdir(parents=True, exist_ok=True)
        (alias_dir / "index.html").write_text(
            make_redirect_page("/nstokes", "Redirecting to Nicky Stokes Card..."),
            encoding="utf-8",
        )

    # 5. Copy public folder into dist
    if PUBLIC_DIR.exists():
        # Copy to dist/public
        dist_public = DIST_DIR / "public"
        if dist_public.exists():
            shutil.rmtree(dist_public)
        shutil.copytree(PUBLIC_DIR, dist_public)

        # Also copy public/* into dist root for clean /images and /vcf URLs
        for item in PUBLIC_DIR.iterdir():
            target = DIST_DIR / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        print("Copied public assets into dist/ and dist/public/.")

    # 6. Build Keystatic Admin SPA into dist/keystatic
    build_keystatic()

    print("Build complete! All cards and Keystatic CMS are packaged in dist/.")


if __name__ == "__main__":
    main()
