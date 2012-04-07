import Image
from os.path import abspath, basename, dirname, isfile, join as pjoin
import numpy as np
import OpenGL
from psychopy import logging

try:
    import pytest
    usePytest=True
except:
    import nose
    usePytest=False

if usePytest:
    from pytest import skip as _skip
else:
    logging.warning("pytest was not found. This is the recommended tool for testing in PsychoPy (rather than nose)")
    from nose.plugins.skip import SkipTest as _skip


# define the path where to find testing data
# so tests could be ran from any location
TESTS_PATH = abspath(dirname(__file__))
TESTS_DATA_PATH = pjoin(TESTS_PATH, 'data')
TESTS_FONT = pjoin(TESTS_DATA_PATH, 'DejaVuSerif.ttf')

def compareScreenshot(fileName, win, crit=5.0):
    """Compare the current back buffer of the given window with the file

    Screenshots are stored and compared against the files under path
    kept in TESTS_DATA_PATH.  Thus specify relative path to that
    directory
    """
    #if we start this from a folder below run.py the data folder won't be found
    fileName = pjoin(TESTS_DATA_PATH, fileName)
    #get the frame from the window
    win.getMovieFrame(buffer='back')
    frame=win.movieFrames[-1]
    win.movieFrames=[]
    #if the file exists run a test, if not save the file
    if not isfile(fileName):
        frame.save(fileName, optimize=1)
        skip("Created %s" % basename(fileName))
    else:
        expected = Image.open(fileName)
        expDat = np.array(expected.getdata())
        imgDat = np.array(frame.getdata())
        rms = (((imgDat-expDat)**2).sum()/len(imgDat))**0.5
        logging.debug('PsychoPyTests: RMS=%.3g at threshold=%3.g'
                  % (rms, crit))
        if rms>=crit:
            filenameLocal = fileName.replace('.png','_local.png')
            frame.save(filenameLocal, optimize=1)
            logging.debug('PsychoPyTests: Saving local copy into %s' % filenameLocal)
        assert rms<crit, \
            "RMS=%.3g at threshold=%.3g. Local copy in %s" % (rms, crit, filenameLocal)

def skip(msg=""):
    """Helper function to allow skipping of tests from either pytest or nose.
    Call this in test code rather than pytest.skip or nose SkipTest
    """
    if usePytest:
        _skip(msg)
    else:
        raise _skip(msg)