#!/usr/bin/env python

import numpy as np
from netCDF4 import Dataset
import argparse

def get_parser():
    ''' Read commandline options and filenames '''

    parser = argparse.ArgumentParser(description='Compares two Exodus II files')
    parser.add_argument('file1')
    parser.add_argument('file2')
    parser.add_argument('--rtol', default = 1e-6, dest = 'rtol', type = float,
         help = 'Relative tolerance')
    parser.add_argument('--atol', default = 1e-6, dest = 'atol', type = float,
         help = 'Absolute tolerance')

    return parser

def main():
    ''' Compare two Exodus II files and reports the differences '''

    # Parse commandline options
    parser = get_parser()
    args = parser.parse_args()

    # Compare the two Exodus II files
    if exodiff(args.file1, args.file2, args.rtol, args.atol):
        print('exodiff: files are identical')

    return

def exodiff(f1, f2, rtol, atol):
    ''' Compare two Exodus II files and reports the differences

    parameters:
        file1: first Exodus II file
        file2: second Exodus II file
        rtol: Relative tolerance
        atol: Absolute tolerance

    return:
        True if files are the same, Exception otherwise
    '''

    # Open each of the files for reading
    with Dataset(f1, 'r') as rootgrp1, Dataset(f2, 'r') as rootgrp2:

        # Each Exodus II file has two parts that need to be checked.
        # 1) The dimensions (where arrays sizes are defined)
        # 2) The variables (where the arrays are contained)
        #
        # To determine if the Exodus II files are identical, both need to
        # be checked

        # Check that both files have identical dimensions for the important features
        # of the Exodus II file (such as model dimension, number of elements, etc).
        # Some of the values in this part of the file specify the length of strings.
        # We do not require that these are identical to declare that the two Exodus II
        # files are the same. The string length dimensions that we do not check are:
        string_lengths = ['len_name', 'len_line']

        for k, v in rootgrp1.dimensions.items():
            if k not in string_lengths:
                if v.size != rootgrp2.dimensions[k].size:
                    raise Exception('Exodus files are different')

        # If the dimensions are identical, then check the variables.
        # Check that both files have the identical keys
        if len(set(rootgrp1.variables.keys()) - set(rootgrp2.variables.keys())) != 0:
            raise Exception('Exodus files are different')

        for k, v in rootgrp1.variables.items():
            if v[:].dtype.type is np.string_:
                # String arrays may be different lengths, but the names must be equal
                # when the individual characters are joined
                # Form an array of strings from array of characters
                v.set_auto_mask(False)
                s1 = [b"".join(c).decode("UTF-8").lower() for c in v[:]]

                # Form an array of strings from array of characters for the second file
                arr2 = rootgrp2.variables[k]
                arr2.set_auto_mask(False)
                s2 = [b"".join(c).decode("UTF-8").lower() for c in arr2[:]]

                # Check if the arrays of strings are identical
                if not np.array_equal(np.sort(s1), np.sort(s2)):
                    raise Exception('Exodus files are different')
            else:
                # If the values are floats, then use np.allclose to check if the arrays
                # are equivalent within the specified tolerances
                if not np.allclose(v[:], rootgrp2.variables[k][:], rtol = rtol, atol = atol):
                    raise Exception('Exodus files are different')

    return True

if __name__ == '__main__':
    main()
