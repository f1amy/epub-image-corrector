# Epub image corrector

A Python script that is correcting wrong colors of images inside ePub files with CMYK color space and without color profiles.

## About

Someday when I was starting reading an .epub eBook it got wrong colors for like 75% of pages.

The investigation concludes that the publisher is messed up when compiling content into an eBook with images color space and color profiles.

The problem is that most ePub readers (that are probably browsers) can't properly display an CMYK image without color profile (but Microsoft Edge can).

Fixing ePubs manually would be very long, also when you don't know which of them corrupted. That's where this scripts comes in.

## Usage

```bash
$ ./epub-image-corrector.py --help
usage: epub-image-corrector.py [-h] [-r] [-f] profile path

Correct images inside ePub files with CMYK color space and without color
profiles.

positional arguments:
  profile          Path to .icc CMYK profile.
  path             Path to .epub file or directory that contains ePub files.

optional arguments:
  -h, --help       show this help message and exit
  -r, --recursive  Recursive into subdirectories.
  -f, --force      Force replace color profile for CMYK color space images.
```

## Requirements

For legal reasons, a color profile isn't included out of the box.
Thus, in order to work, you must download it yourself. I tested some of these:

* JapanColor2001Coated.icc
* Photoshop5DefaultCMYK.icc
* USWebCoatedSWOP.icc
* UncoatedFOGRA29.icc

The best experience I had was with `USWebCoatedSWOP.icc` profile.

It doesn't mean that you'll have the same experience with your files, so it is worth to try other profiles.

You could download some profiles from Adobe ([link for win](https://www.adobe.com/support/downloads/iccprofiles/iccprofiles_win.html)) or color.org ([link](http://www.color.org/registry/index.xalter)).

Also you will need a Python interpreter installed on your system, instructions can be found [here](https://www.python.org/downloads/).

In addition to interpreter you must also install dependencies using this command:

```bash
pip3 install -r requirements.txt
```

The script is tested on Python 3.6.8 and should work on both Linux and Windows.

## Examples

### For single file

```bash
./epub-image-corrector.py /profiles/some-profile.icc /books/comics/some-comic.epub
```

### For single file force replace profile

```bash
./epub-image-corrector.py /profiles/some-profile.icc /books/study/some-book.epub -f
```

### For a directory

```bash
./epub-image-corrector.py /profiles/some-profile.icc /books/journals
```

### For a directory recursive

```bash
./epub-image-corrector.py /profiles/some-profile.icc /books -r
```
