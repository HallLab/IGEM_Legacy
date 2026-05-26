from os.path import dirname, join, realpath

from load.plink import plink1_xa
from numpy import dtype
from numpy.testing import assert_array_equal, assert_equal


def test_load_plink1_xa():

    datafiles = join(dirname(realpath(__file__)), "data_files")
    # file_prefix = join(datafiles, "data")
    file_prefix = join(datafiles, "chr11")
    bim = file_prefix + ".bim"
    bed = file_prefix + ".bed"
    fam = file_prefix + ".fam"

    G = plink1_xa(bed, bim, fam, verbose=False)
    G.values

