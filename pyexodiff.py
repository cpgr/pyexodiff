#!/usr/bin/env python

import numpy as np
from netCDF4 import Dataset
import argparse
import re

def get_parser():
    ''' Read commandline options and filenames '''

    parser = argparse.ArgumentParser(description='Compares two Exodus II files')
    parser.add_argument('file1')
    parser.add_argument('file2')
    parser.add_argument('--rtol', default = 1e-6, dest = 'rtol', type = float,
         help = 'Relative tolerance (default: %(default)s)')
    parser.add_argument('--atol', default = 1e-6, dest = 'atol', type = float,
         help = 'Absolute tolerance (default: %(default)s)')
    parser.add_argument('-q', '--quiet', default = False, dest = 'quiet', action = 'store_true',
         help = 'Quiet mode (only prints final message) (default: %(default)s)')

    return parser

def main():
    ''' Compare two Exodus II files and reports the differences '''

    # Parse commandline options
    parser = get_parser()
    args = parser.parse_args()

    # Compare the two Exodus II files
    diff = exodiff(args.file1, args.file2, args.rtol, args.atol)

    # If diff is not empty, then there are differences
    if diff['dimensions'] or diff['variables']['names'] or diff['variables']['values']:
        if not args.quiet:
            printDiff(diff)
        print('\npyexodiff: files are different')

    else:
        print('\npyexodiff: files are identical')

    return

def exodiff(f1, f2, rtol, atol):
    ''' Compare two Exodus II files and reports the differences

    parameters:
        file1: first Exodus II file
        file2: second Exodus II file
        rtol: Relative tolerance
        atol: Absolute tolerance

    return:
        dict of differences
    '''

    # Dict of differneces
    diff = {}
    diff['dimensions'] = {}
    diff['variables'] = {}
    diff['variables']['names'] = {}
    diff['variables']['values'] = {}

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
        string_lengths = ['len_name', 'len_line', 'len_string']

        for k, v in rootgrp1.dimensions.items():
            if k not in string_lengths:
                if v.size != rootgrp2.dimensions[k].size:
                    diff['dimensions'][k] = [v.size, rootgrp2.dimensions[k].size]

        # Now check the variable names (do this before comparing actual values to make
        # sure that all variable names, sideset names etc are present in both files)
        for k, v in rootgrp1.variables.items():
            if v[:].dtype.type is np.string_:
                # String arrays may be different lengths, but the names must be equal
                # when the individual characters are joined
                # Form an array of strings from array of characters
                s1 = charListtoString(v)

                # Form an array of strings from array of characters for the second file
                s2 = charListtoString(rootgrp2.variables[k])

                # Check if the arrays of strings are identical. If not, return early as
                # the files are clearly different
                if not np.array_equal(np.sort(s1), np.sort(s2)):
                    diff['variables']['names'][k] = np.array(list((set(s1)^set(s2))))
                    return diff

        # Now check the actual numerical values. First, though, we must allow for the possibility
        # that variable numbers are in a different order
        if 'name_elem_var' in rootgrp1.variables.keys():
            elem_var_map = variableOrder(rootgrp1.variables['name_elem_var'], rootgrp2.variables['name_elem_var'])

        if 'name_nod_var' in rootgrp1.variables.keys():
            node_var_map = variableOrder(rootgrp1.variables['name_nod_var'], rootgrp2.variables['name_nod_var'])

        if 'name_sset_var' in rootgrp1.variables.keys():
            ss_var_map = variableOrder(rootgrp1.variables['name_sset_var'], rootgrp2.variables['name_sset_var'])

        if 'name_nset_var' in rootgrp1.variables.keys():
            ns_var_map = variableOrder(rootgrp1.variables['name_nset_var'], rootgrp2.variables['name_nset_var'])

        for k, v in rootgrp1.variables.items():
            # If the values are floats, then use np.allclose to check if the arrays
            # are equivalent within the specified tolerances
            if v[:].dtype.type is not np.string_:

                # If the key is a variable value (vals_*_var*), then transform the var number
                # using the varmap to ensure that the correct variables are being compared
                k2 = k
                if k.startswith('vals_elem'):
                    var1 = re.search("var\d+", k).group()
                    k2 = re.sub("var\d+", 'var' + str(elem_var_map[int(var1.replace('var', ''))-1]), k)

                if k.startswith('vals_nod'):
                    var1 = re.search("var\d+", k).group()
                    k2 = re.sub("var\d+", 'var' + str(node_var_map[int(var1.replace('var', ''))-1]), k)

                if k.startswith('vals_sset'):
                    var1 = re.search("var\d+", k).group()
                    k2 = re.sub("var\d+", 'var' + str(ss_var_map[int(var1.replace('var', ''))-1]), k)

                if k.startswith('vals_nset'):
                    var1 = re.search("var\d+", k).group()
                    k2 = re.sub("var\d+", 'var' + str(ns_var_map[int(var1.replace('var', ''))-1]), k)

                if k2 in rootgrp2.variables.keys():
                    if not np.allclose(v[:], rootgrp2.variables[k2][:], rtol = rtol, atol = atol):
                        abs_diff = np.abs(v[:] - rootgrp2.variables[k2][:])
                        max_abs_diff = np.max(abs_diff)
                        max_abs_diff_pos = np.where(abs_diff == abs_diff.max())
                        rel_diff = np.abs(np.divide(v[:] - rootgrp2.variables[k2][:], v[:], where=v[:]!=0))
                        max_rel_diff = np.max(rel_diff)
                        max_rel_diff_pos = np.where(rel_diff == rel_diff.max())
                        diff['variables']['values'][k] = {}
                        diff['variables']['values'][k]['max_abs_diff'] = max_abs_diff
                        diff['variables']['values'][k]['max_abs_diff_pos'] = max_abs_diff_pos
                        diff['variables']['values'][k]['max_rel_diff'] = max_rel_diff
                        diff['variables']['values'][k]['max_rel_diff_pos'] = max_rel_diff_pos

    return diff

def printDiff(diff):
    ''' Print out the differences in the dict diff '''

    indent = '    '
    print('\npyexodiff: difference summary:\n')

    # Print out all differences in the dimensions dict
    if diff['dimensions']:
        print('Dimensions:')
        for k, v in diff['dimensions'].items():
            print('{}{} is different: file1 size is {}; file2 size is {}'.format(indent, k, v[0], v[1]))

    # Print out summary of differences in the variables dict
    if diff['variables']:
        print('Variables:')

        # If the difference is in the names, print out all the differences and return
        if diff['variables']['names']:
            for k, v in diff['variables']['names'].items():
                for vi in v:
                    print('{}{} is different: variable {} not in both files'.format(indent, k, vi))

            # If the variable names are different, there will be lots of values different,
            # so don't print them all
            return

        # If the difference is in the values, then print out the maximum differences
        if diff['variables']['values']:
            for k, v in diff['variables']['values'].items():
                print('{}{} is different: '.format(indent, k))
                print('{}max absolute diff {:.4e} at position {}'.format(indent*2, v['max_abs_diff'], v['max_abs_diff_pos'][0][0]))
                print('{}max relative diff {:.4e} at position {}'.format(indent*2, v['max_rel_diff'], v['max_rel_diff_pos'][0][0]))

    return

def variableOrder(var_names1, var_names2):
    '''
    Return a list of indices for the variable name in var_names2
    sorted in terms of var_names1
    '''

    vars1 = charListtoString(var_names1)
    vars2 = charListtoString(var_names2)

    # Add one for 1-based variable numbering
    varmap = [vars2.index(v) + 1 for v in vars1]

    return varmap

def charListtoString(charlist):
    '''
    Returns a list of strings from a given list of chars
    '''

    charlist.set_auto_mask(False)
    stringlist = [b"".join(c).decode("UTF-8", errors='ignore').lower() for c in charlist[:]]

    return stringlist

if __name__ == '__main__':
    main()
