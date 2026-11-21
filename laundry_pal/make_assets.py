"""One-off helper: crops the photographs out of the Figma reference screenshots
(reference/*.png) and saves them as separate files in assets/images.

Run it only if you want to regenerate the images:  python make_assets.py
You can also simply replace the files in assets/images with your own photos
(keep the same file names) - the app crops them to fit automatically.
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "reference")
OUT = os.path.join(BASE, "assets", "images")
os.makedirs(OUT, exist_ok=True)

# (reference file, crop box (left, top, right, bottom), output name)
CROPS = [
    ("02_-_Home.png", (21, 212, 132, 305), "service_laundry.jpg"),
    ("02_-_Home.png", (21, 318, 132, 411), "service_ironing.jpg"),
    ("02_-_Home.png", (21, 424, 132, 517), "service_dryclean.jpg"),
    ("03_-_Laundry_Providers.png", (33, 190, 164, 342), "provider_freshfold.jpg"),
    ("03_-_Laundry_Providers.png", (33, 378, 164, 530), "provider_sparkle.jpg"),
    ("03_-_Laundry_Providers.png", (33, 566, 164, 718), "provider_bluebasket.jpg"),
    ("04_-_Provider_Details.png", (20, 128, 410, 380), "provider_freshfold_hero.jpg"),
    ("Account.png", (178, 143, 252, 217), "profile_aarav.jpg"),
]

for ref, box, name in CROPS:
    im = Image.open(os.path.join(REF, ref)).convert("RGB").crop(box)
    im.save(os.path.join(OUT, name), quality=95)
    print("saved", name, im.size)
