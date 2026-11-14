# news-image-01-e4 entry: copies the broadsheet front-page image summing up
# the world news of Friday 13 November 2026 to /output/entry.png.
# Python 3.13, standard library only. Deterministic: the same bytes on every run.
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_BYTES = 1048576
MAX_SIDE = 1024


def _png_dimensions(data):
    # Width and height live at fixed offsets in the PNG header (IHDR).
    return struct.unpack(">II", data[16:24])


def _jpeg_dimensions(data):
    # Walk JPEG markers until the first Start Of Frame segment.
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + length
    raise ValueError("no JPEG frame found")


def _check_image(path):
    # Self-check the competition's gate before finishing: a whole PNG or
    # JPEG, at most 1 MiB and at most 1024 by 1024 pixels.
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError("image exceeds 1 MiB")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = _png_dimensions(data)
    elif data[:3] == b"\xff\xd8\xff":
        width, height = _jpeg_dimensions(data)
    else:
        raise ValueError("not a PNG or JPEG")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("image exceeds 1024x1024")


def main():
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.png"
    shutil.copyfile(HERE / "entry.png", target)
    _check_image(target)
    # Verify the copy landed byte-for-byte; a partial write must fail loudly.
    if (HERE / "entry.png").read_bytes() != target.read_bytes():
        raise ValueError("output does not match source image")


if __name__ == "__main__":
    main()
