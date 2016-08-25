import glob
import os
import subprocess
import tempfile
import time

import cStringIO
from wand.color import Color
from wand.image import Image

PATH = './test_assets/*.pdf'


def temp_name():
    """ returns a temporary file-name """
    tmpfile = tempfile.NamedTemporaryFile(prefix="tess_")
    return tmpfile.name


def convert_to_txt(tmp_file_prefix):
    tess_out = ''
    for png in sorted(glob.glob('%s*.png' % tmp_file_prefix)):
        tesseract_command = ['tesseract', png, png[:-4], '-l', 'eng']
        tess_out = subprocess.check_output(
            tesseract_command,
            stderr=subprocess.STDOUT
        )
    return tess_out


def convert_blob_to_text(blob):
    """Do Tesseract work, but use a blob as input instead of a file."""
    tesseract_command = ['tesseract', 'stdin', 'stdout', '-l', 'eng']
    p = subprocess.Popen(
        tesseract_command,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return p.communicate(input=blob)[0]


def convert_file_to_txt(path):
    tesseract_command = ['tesseract', path, 'stdout', '-l', 'eng']
    p = subprocess.Popen(
        tesseract_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return p.communicate()[0]


def convert_to_pngs(command):
    subprocess.check_output(command,
                            stderr=subprocess.STDOUT)


def avg(l):
    """Make the average of a list"""
    return sum(l) / len(l)


def subprocess_approach():
    # Basic approach using subprocess and writing things to disk.
    methods = {
        'current': ['convert',
                    '-depth', '4',
                    '-density', '300',
                    '-background', 'white', '+matte'],
        'grayscale': ['convert',
                      '-depth', '4',
                      '-density', '300',
                      '-background', 'white', '+matte',
                      '-colorspace', 'Gray'],
        'smaller': ['convert',
                    '-depth', '4',
                    '-density', '200',
                    '-background', 'white', '+matte'],
    }
    for method_name, command in methods.items():
        print("\n\nAttempting method: %s" % method_name)
        image_cpu_timing = []
        tess_cpu_timing = []
        image_wall_timing = []
        tess_wall_timing = []
        for path in sorted(glob.glob(PATH)):
            out_name = temp_name()
            print("  Doing: %s" % path)
            print("    Using temp dir: %s" % out_name)

            try:
                print("    Doing image conversion.")
                full_command = command + [path, '%s-%%03d.png' % out_name]
                t1_cpu = time.clock()
                t1_wall = time.time()
                convert_to_pngs(full_command)
                image_cpu_timing.append(time.clock() - t1_cpu)
                image_wall_timing.append(time.time() - t1_wall)

                print("    Doing tesseract command.")
                t1_cpu = time.clock()
                t1_wall = time.time()
                convert_to_txt(out_name)
                tess_cpu_timing.append(time.clock() - t1_cpu)
                tess_wall_timing.append(time.time() - t1_wall)
            finally:
                # Remove tmp_file and the text file
                for f in glob.glob('%s*' % out_name):
                    try:
                        os.remove(f)
                    except OSError:
                        pass

        print(u"  Sys, Real")
        print(u"  Average image conversion was %s, %s" % (
            avg(image_cpu_timing),
            avg(image_wall_timing),
        ))
        print(u"   Average tess conversion was %s, %s" % (
            avg(tess_cpu_timing),
            avg(tess_wall_timing),
        ))
        print(u"         Total image time was: %s, %s" % (
            sum(image_cpu_timing), sum(image_wall_timing)
        ))
        print(u"          Total tess time was: %s, %s" % (
            sum(tess_cpu_timing), sum(tess_wall_timing)
        ))
        print(u"               Grand total was %s, %s" % (
            sum(image_cpu_timing) + sum(tess_cpu_timing),
            sum(image_wall_timing) + sum(tess_wall_timing),
        ))


def wand_approach():
    # New Approach using Wand to create files
    # Install libmagickwand-dev!
    image_cpu_timing = []
    tess_cpu_timing = []
    image_wall_timing = []
    tess_wall_timing = []
    for path in sorted(glob.glob(PATH)):
        print("  Doing: %s" % path)
        all_pages = Image(filename=path, resolution=150)

        for i, img in enumerate(all_pages.sequence):
            t1_cpu = time.clock()
            t1_wall = time.time()
            with Image(img) as img_out:
                img_out.format = 'png'
                img_out.background_color = Color('white')
                img_out.alpha_channel = 'remove'
                img_out.depth = 4
                img_out.type = "grayscale"
                img_out.resolution = 150
                #img_out.save(filename='%s-%03d.png' % (path[:-4], i))
                img_bin = img_out.make_blob('png')
            image_cpu_timing.append(time.clock() - t1_cpu)
            image_wall_timing.append(time.time() - t1_wall)

            # Do Tesseract on the binary data
            t1_cpu = time.clock()
            t1_wall = time.time()
            txt = convert_blob_to_text(img_bin)
            tess_cpu_timing.append(time.clock() - t1_cpu)
            tess_wall_timing.append(time.time() - t1_wall)

    print(u"  Sys, Real")
    print(u"  Average image conversion was %s, %s" % (
        avg(image_cpu_timing),
        avg(image_wall_timing),
    ))
    print(u"   Average tess conversion was %s, %s" % (
        avg(tess_cpu_timing),
        avg(tess_wall_timing),
    ))
    print(u"         Total image time was: %s, %s" % (
        sum(image_cpu_timing), sum(image_wall_timing)
    ))
    print(u"          Total tess time was: %s, %s" % (
        sum(tess_cpu_timing), sum(tess_wall_timing)
    ))
    print(u"               Grand total was %s, %s" % (
        sum(image_cpu_timing) + sum(tess_cpu_timing),
        sum(image_wall_timing) + sum(tess_wall_timing),
    ))


def multipage_tiff_approach():
    """Theory: Initializing Tesseract for every page takes time.
    Hypothesis: Using a multi-page tiff will allow it only to be initialized
    once, saving time.
    """
    image_cpu_timing = []
    tess_cpu_timing = []
    image_wall_timing = []
    tess_wall_timing = []
    for path in sorted(glob.glob(PATH)):
        print("  Doing: %s" % path)
        all_pages = Image(filename=path, resolution=300)
        tiff_out = Image()
        t1_cpu = time.clock()
        t1_wall = time.time()
        for i, img in enumerate(all_pages.sequence):
            with Image(img) as img_out:
                img_out.background_color = Color('white')
                img_out.alpha_channel = 'remove'
                img_out.depth = 4
                img_out.type = "grayscale"
                tiff_out.sequence.append(img_out)
        tiff_bin = cStringIO.StringIO()
        tiff_out.format = 'tiff'
        tiff_out.save(file=tiff_bin)
        image_cpu_timing.append(time.clock() - t1_cpu)
        image_wall_timing.append(time.time() - t1_wall)

        # Do Tesseract on the binary data
        t1_cpu = time.clock()
        t1_wall = time.time()
        txt = convert_blob_to_text(tiff_bin.getvalue())
        tess_cpu_timing.append(time.clock() - t1_cpu)
        tess_wall_timing.append(time.time() - t1_wall)

    print(u"  Sys, Real")
    print(u"  Average image conversion was %s, %s" % (
        avg(image_cpu_timing),
        avg(image_wall_timing),
    ))
    print(u"   Average tess conversion was %s, %s" % (
        avg(tess_cpu_timing),
        avg(tess_wall_timing),
    ))
    print(u"         Total image time was: %s, %s" % (
        sum(image_cpu_timing), sum(image_wall_timing)
    ))
    print(u"          Total tess time was: %s, %s" % (
        sum(tess_cpu_timing), sum(tess_wall_timing)
    ))
    print(u"               Grand total was %s, %s" % (
        sum(image_cpu_timing) + sum(tess_cpu_timing),
        sum(image_wall_timing) + sum(tess_wall_timing),
    ))

subprocess_approach()
wand_approach()
multipage_tiff_approach()
