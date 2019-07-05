#!/usr/bin/env python

import pytest
import os
import subprocess
import yaml
from netCDF4 import Dataset
import numpy as np
import pyexodiff

# Exception class to throw exception for pytest
class pyexodiffException(Exception):
    pass

# Run the current file using pytest
pytest.main(['-v', '-rsx', '--tb=line', 'run_tests.py'])

# Find all 'tests' yml files that contain the test specifications
tests_files = []
for root, dirs, files in os.walk("test/", topdown=False):
    for name in files:
        if name == 'tests':
            tests_files.append(os.path.join(root, name))

# Read yaml data from tests files
tests = {}
for test in tests_files:
    with open(test, 'r') as file:
        testcfg = yaml.safe_load(file)

        # Extract the filepath
        filepath, filename = os.path.split(test)

        for key, values in testcfg.items():
            # Make keys unique by prepending the filepath
            fullpathkey = os.path.join(filepath, key)
            tests[fullpathkey] = values
            tests[fullpathkey]['filepath'] = filepath

            # Add default relative tolerance if not specified in tests file
            if 'rtol' not in tests[fullpathkey].keys():
                tests[fullpathkey]['rtol'] = 1.0e-6

            # Add default absolute tolerance if not specified in tests file
            if 'atol' not in tests[fullpathkey].keys():
                tests[fullpathkey]['atol'] = 1.0e-6

# Run all tests found during search
@pytest.mark.parametrize('key', tests)
def test_pyexodiff(key):
    ''' Run all pyexodiff tests '''

    # If the file key isn't specified, skip test
    if 'file1' not in tests[key].keys():
        pytest.skip(key + ': Skipped as file1 not specified')

    if 'file2' not in tests[key].keys():
        pytest.skip(key + ': Skipped as file2 not specified')

    else:
        output = exodiff_test(key)

        # If there is no expected error in tests, then we expect the files to be identical
        if 'expected_error' not in tests[key].keys():
            assert('pyexodiff: files are identical' in output)

        else:
            # Check the output to make sure that the expected error is given
            assert(tests[key]['expected_error'] in output)
            assert('pyexodiff: files are different' in output)

    return

def exodiff_test(key):
    ''' Compare Exodus II file with gold file '''

    filepath = tests[key]['filepath']
    file1 = tests[key]['file1']
    file2 = tests[key]['file2']
    rtol = tests[key]['rtol']
    atol = tests[key]['atol']
    f1 = os.path.join(filepath, file1)
    f2 = os.path.join(filepath, file2)

    try:
        output = subprocess.check_output(['./pyexodiff.py', '--atol', str(atol), '--rtol', str(rtol), f1, f2]).decode('utf-8')

    except subprocess.CalledProcessError:
        raise pyexodiffException('pyexodiff failed to run')

    return output


# Unit tests of specific functionality
def test_variableOrder():

    # Read in example data
    rootgrp = Dataset('test/unit/varnames.nc', 'r')

    varnames1 = rootgrp.variables['varnames1']
    varnames2 = rootgrp.variables['varnames2']

    varmap = pyexodiff.variableOrder(varnames1, varnames2)

    assert varmap == [3, 4, 1, 2]

    # Close the netCDF4 file
    rootgrp.close()

    return

# Unit tests of specific functionality
def test_charListtoString():

    # Read in example data
    rootgrp = Dataset('test/unit/varnames.nc', 'r')

    varnames1 = rootgrp.variables['varnames1']
    varnames2 = rootgrp.variables['varnames2']

    stringlist1 = pyexodiff.charListtoString(varnames1)
    assert stringlist1 == ['variable1', 'variable2', 'variable3', 'variable4']

    stringlist2 = pyexodiff.charListtoString(varnames2)
    assert stringlist2 == ['variable3', 'variable4', 'variable1', 'variable2']

    # Close the netCDF4 file
    rootgrp.close()

    return
