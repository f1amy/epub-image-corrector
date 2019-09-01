#!/usr/bin/env python3

import argparse
#import os
from zipfile import ZipFile
from pathlib import Path
from tempfile import TemporaryDirectory

from wand.image import Image


def file_or_dir(string):
    path = Path(string)

    if path.is_dir():
        return string
    elif path.is_file():
        print(path.suffix)
        if path.suffix == '.epub':
            return string
        else:
            raise argparse.ArgumentTypeError(f"{path} is not a .epub file")
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


if (not Path('color-profiles/CMYK.icc').is_file()
        or not Path('color-profiles/sRGB.icc').is_file()):
    raise FileNotFoundError('CMYK.icc are not found '
                            'inside color-profiles directory.')

parser = argparse.ArgumentParser(
    description='Fix images with wrong color space '
                'and profiles inside .epub files.')
parser.add_argument('path', nargs=1, type=file_or_dir,
                    help='path to .epub file or directory for image fixing')
parser.add_argument('-r', '--recursive', action='store_true',
                    help='recurse into subdirectories')

args = parser.parse_args()
print(args)

path = Path(args.path[0])

if path.is_file():
    print('file')
    with TemporaryDirectory() as tmpdir:
        print(tmpdir)
        with ZipFile(path, 'a') as epub:
            epub.printdir()
            epub.extractall(tmpdir)
        extepub = Path(tmpdir)
        for file in extepub.glob('OEBPS/images/*.jpeg'): #OEBPS/images/*.(jpg|jpeg|png) not working
            print(file)
            with Image(filename=file) as img:
                if img.profiles['ICC'] == None and img.colorspace == 'cmyk':
                    print('cmyk and no profiles')
                    print(f"fixing: {file}")
                    with open('color-profiles/USWebCoatedSWOP.icc', 'rb') as icc:
                        img.profiles['ICC'] = icc.read()
                    img.save(filename=str(file))
        with ZipFile(path, 'w') as epub:
            for file in extepub.glob('**/*'):
                print(file.relative_to(extepub))
                epub.write(file, arcname=file.relative_to(extepub))

elif path.is_dir():
    print('directory')
    print(f"recursive={args.recursive}")
