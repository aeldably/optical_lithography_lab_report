import os
import shutil
from pathlib import Path

# Define base paths
base = Path.cwd()
raw_img = base / "Images"
raw_prof = base / "Profilometer_Data"

# Desired structure
dirs = [
    base / "data/images/calibration",
    base / "data/images/3p2x",
    base / "data/images/50x",
    base / "data/profilometer/raw",
    base / "data/profilometer/processed",
    base / "notebooks",
    base / "scripts",
    base / "results/figures",
    base / "results/tables"
]

# Create directories
for d in dirs:
    d.mkdir(parents=True, exist_ok=True)

# Move calibration images (Lp/mm patterns)
for pattern in ["100Lpmm_*.jpg", "25Lpmm_*.jpg"]:
    for img in raw_img.glob(pattern):
        shutil.move(str(img), str(base / "data/images/calibration"))

# Move 3.2× magnification images
for img in raw_img.glob("*3p2x.*"):
    shutil.move(str(img), str(base / "data/images/3p2x"))

# Move 50× magnification images
for img in raw_img.glob("*50x*.jpg"):
    shutil.move(str(img), str(base / "data/images/50x"))

# Move profilometer raw files
for prof in raw_prof.glob("*"):
    shutil.move(str(prof), str(base / "data/profilometer/raw"))

print("Folder structure created and raw files organized.")
