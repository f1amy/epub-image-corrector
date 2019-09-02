#!/usr/bin/env python3

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from timeit import default_timer as timer
from zipfile import ZipFile, is_zipfile

from progress.bar import Bar
from wand.image import Image


def file_or_dir(string: str) -> str:
    """
    Passes argument if it is a valid path to the .epub file or a directory.
    """
    path = Path(string)

    if path.is_dir():
        return string
    elif path.is_file():
        if path.suffix == '.epub':
            return string
        else:
            raise argparse.ArgumentTypeError(f"{string} is not a .epub file.")
    else:
        raise argparse.ArgumentTypeError(f"{string} is not a valid path.")


def profile(string: str) -> str:
    """
    Passes argument if it is a valid path to the .icc file.
    """
    path = Path(string)

    if path.is_file():
        if path.suffix == '.icc':
            return string
        else:
            raise FileNotFoundError(f"{string} is not a .icc file.")
    else:
        raise FileNotFoundError(
            f"{string} is not a valid path to an .icc file."
            f"\n{18 * ' '} Please specify a path to the .icc cmyk color "
            "profile with -p option.")


def process_file(path: Path) -> int:
    """
    Correct images inside .epub file.\n
    File is overwritten only if at least one image is corrected.\n
    Returns number of changed images inside file.
    """
    with TemporaryDirectory() as tmp_dir:
        root_dir = Path(tmp_dir)
        if not is_zipfile(path):
            print(f"error: {path.relative_to(root_dir)} "
                  "is not a zip file, skipping.")
            return

        time = timer()
        with ZipFile(path, 'a') as archive:
            archive.extractall(root_dir)
        print(f"zip extract: {timer() - time}")
        if (Path(f"{root_dir}/mimetype").read_text()
                != 'application/epub+zip'):
            print(f"error: {path.relative_to(root_dir)} "
                  "is not a application/epub+zip file, skipping.")
            return
        files_changed = 0
        image_extensions = ['jpg', 'jpeg', 'png']
        time = timer()
        for extension in image_extensions:
            for file in root_dir.glob(f"OEBPS/images/*.{extension}"):
                with Image(filename=file) as img:
                    if (img.profiles['ICC'] == None
                            and img.colorspace == 'cmyk'):
                        files_changed += 1
                        print(f"fixing: {file}")
                        with open(color_profile, 'rb') as profile:
                            img.profiles['ICC'] = profile.read()
                        img.save(filename=str(file))
        print(f"file correction: {timer() - time}")
        time = timer()
        if files_changed > 0:
            with ZipFile(path, 'w') as epub:
                for file in root_dir.rglob('*'):
                    epub.write(file, arcname=file.relative_to(root_dir))
        print(f"file write: {timer() - time}")
        return files_changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Correct images inside .epub files with CMYK color space '
                    'and without profiles.')
    parser.add_argument('path', type=file_or_dir,
                        help='Path to .epub file or directory for image correcting.')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Recursive into subdirectories.')
    parser.add_argument('-p', '--profile', type=profile, required=True,
                        help='Path to .icc cmyk profile, '
                        'defaults to cmyk.icc in current directory.')

    args = parser.parse_args()

    work_path = Path(args.path)
    color_profile = Path(args.profile)

    changed_images = 0
    files = 0
    time = timer()

    if work_path.is_file():
        changed_images = process_file(work_path)
        files = 1 if changed_images > 0 else 0
    else:
        work_files = list(work_path.glob(
            f"{'**/' if args.recursive else ''}*.epub"))

        bar = Bar('Processing files:', max=len(work_files))

        for file in work_files:
            bar.next()

            images_changed = process_file(file)
            changed_images += images_changed
            files += 1 if images_changed > 0 else 0

        bar.finish()

    elapsed_time = timer() - time

    print(f"Changed {changed_images} images inside {files} "
          f"{'files' if files > 1 else 'file'} in {'%.3f'%(elapsed_time)}s.")