# ISD Tech — Self-Hosted Digital Business Cards

Mobile-optimised digital business card platform for **Integrated Security Design Ltd (`isd-tech.com`)**, featuring 1-tap `.vcf` (Virtual Contact File) downloads with embedded portrait photos, instant QR code sharing, and **Keystatic CMS** so non-technical staff can easily update details or add new team members.

---

## Included Card: Nicky Stokes

- **Name:** Nicky Stokes
- **Job Title:** Managing Director
- **Company:** Integrated Security Design Ltd
- **Mobile:** `+44 7919 897800`
- **Email:** `nstokes@isd-tech.com`
- **Website:** [isd-tech.com](https://www.isd-tech.com)
- **LinkedIn:** [linkedin.com/in/nicky-stokes-2ba06510](https://www.linkedin.com/in/nicky-stokes-2ba06510/)
- **Office Address:** Integrated Security Design Ltd, Shield House, Ground Floor, 294 High Street, Aldershot, GU12 4LT
- **Portrait Cutout:** `public/images/nicky-stokes-cutout.png` (AI background-segmented cutout from original photo)
- **1-Tap vCard:** `public/vcf/nicky-stokes.vcf` (vCard 3.0 with embedded JPEG photo for iOS & Android Contacts)

---

## Project Structure

```text
isd-digital-cards/
├── index.html                        # Standalone mobile micro-site for Nicky Stokes
├── content/
│   └── cards/
│       └── nicky.json                # Structured contact record (managed by Keystatic CMS)
├── keystatic.config.ts               # Keystatic CMS schema for non-tech editing at /keystatic
├── public/
│   ├── images/
│   │   ├── nicky-stokes-cutout.png   # Transparent cutout portrait
│   │   ├── nicky-stokes-original.jpg # Cropped square original photo
│   │   ├── nicky-stokes-vcf.jpg      # Navy-backed portrait embedded inside the .vcf
│   │   └── nicky-qr.png              # QR code pointing to isd-tech.com/vcard/nicky
│   └── vcf/
│       └── nicky-stokes.vcf          # Pre-built vCard 3.0 file for 1-tap phone import
└── scripts/
    └── build_cards.py                # Auto-generates .vcf files from content/cards/*.json
```

---

## Updating Cards via Keystatic CMS (For Non-Tech Editors)

Keystatic stores each team member's card as a simple JSON file inside `content/cards/<slug>.json` and provides a clean web admin dashboard at `/keystatic`:

1. Non-technical staff sign in at `/keystatic` (using GitHub login or Keystatic Cloud free tier).
2. Select **Team Business Cards** → **Nicky Stokes** (or click **Create** to add a new team member).
3. Update fields (Job Title, Mobile Number, Email, LinkedIn, Office Address, or drag-and-drop a new photo) and click **Save**.
4. Keystatic commits the change directly to the GitHub repository, and the build script (`python3 scripts/build_cards.py`) regenerates both the webpage and the `.vcf` download file automatically.
