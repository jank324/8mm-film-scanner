import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from pidng.core import RPICAM2DNG
from tqdm import tqdm


def bayerjpg2dng(jpg_path: Path, delete: bool = False) -> None:
    """
    Convert a the file at `jpg_path` to a `.dng` file. Deletes the old file if `delete`
    is set to `True`.
    """
    d = RPICAM2DNG()
    d.convert(str(jpg_path))

    dng_path = jpg_path.parent / (jpg_path.name + ".dng")
    validate_file(dng_path, min_bytes=int(1e6))

    if delete:
        jpg_path.unlink()


def validate_file(path: Path, min_bytes: int = 1) -> None:
    """Check if file exists and has a file size larger than `min_bytes`."""
    is_valid = path.is_file() and path.stat().st_size > min_bytes
    if not is_valid:
        raise InvalidFileException(path)


class InvalidFileException(Exception):
    """Exception raised when a file was found to be invalid."""

    def __init__(self, filepath: Path) -> None:
        super().__init__(f'File "{filepath}" is invalid.')


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
    filepaths = list(directory.glob("frame-*.jpg"))

    with tqdm(total=len(filepaths)) as pbar:
        executor = ProcessPoolExecutor(max_workers=2)
        futures = [
            executor.submit(bayerjpg2dng, path, delete=args.delete)
            for path in filepaths
        ]
        for _ in as_completed(futures):
            pbar.update()


if __name__ == "__main__":
    main()
