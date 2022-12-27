import argparse
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

from pidng.core import RPICAM2DNG


def bayerjpg2dng(filepath: Path, delete: bool = False) -> None:
    """
    Convert a the file at `filepath` to a `.dng` file. Deletes the old file if `delete`
    is set to `True`.
    """
    print(f"Converting {filepath}")

    d = RPICAM2DNG()
    d.convert(str(filepath))

    if delete:
        filepath.unlink()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments to the Pi to DNG conversion utility. Returns the `args`
    object.
    """
    parser = argparse.ArgumentParser(
        description="Convert Raspberry Pi Bayer JPEGs to DNGs."
    )
    parser.add_argument("directory", help="Directory with the JPEG files")
    parser.add_argument("--delete", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    directory = Path(args.directory)
    filepaths = directory.glob("frame-*.jpg")

    executor = ThreadPoolExecutor()
    futures = [
        executor.submit(bayerjpg2dng, path, delete=args.delete) for path in filepaths
    ]
    wait(futures)


if __name__ == "__main__":
    main()
