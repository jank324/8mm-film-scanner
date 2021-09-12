import glob
import os


directory = "/Volumes/PortableSSD/kreta_after_repair/"

files = glob.glob(os.path.join(directory, "frame-*.dng"))

for i, f in enumerate(sorted(files)):
    new_name = f"frame-{i:05d}.dng"
    new_path = os.path.join(directory, new_name)
    os.rename(f, new_path)
