# pyExodiff - pure python exodiff

![example workflow](https://github.com/cpgr/pyexodiff/actions/workflows/python-package-conda/badge.svg)

`pyexodiff` compares two [Exodus II](https://github.com/gsjaardema/seacas) files to determine
whether they are identical. It is intended as a python replacement of the [Exodiff](https://github.com/gsjaardema/seacas) utility, allowing two Exodus II files to be compared without the need to install SEACAS.

## Setup

`pyexodiff` requires the following python packages to be installed:

- numpy
- netCDF4
- argparse
- re

These can be installed using `pip` if they are not already installed
```bash
pip install numpy
```
for example.

Two additional python package are required to run the test script:

- pytest
- pyYAML

Again, these can be installed using
```bash
pip install pytest
```
for example.

## Usage

`pyexodiff` can be used as a standalone utility to compare two Exoduss II files on the commandline using

```bash
./pyexodiff.py file1 file2
```

If the two Exodus II files are identical, `pyexodiff` reports that they are the same:
```bash
$ pyexodiff.py test/simple_cube.e test/simple_cube.e

pyexodiff: files are identical
```

If the files are different, however, `pyexodiff` will report that they are not identical and will provide a brief summary of the differences.

For example, if the dimensions of the Exodus II files are different, then `pyexodiff` will report the difference:
```bash
$  pyexodiff.py test/simple_cube.e test/simple_cube_missing_prop.e

pyexodiff: difference summary:

Dimensions:
    num_elem_var is different: file1 size is 6; file2 size is 5
    num_sset_var is different: file1 size is 6; file2 size is 5
  Variables:
      name_elem_var is different: variable poro not in both files
      name_sset_var is different: variable poro not in both files

pyexodiff: files are different
```

If the variables of both files are not equal (to within the given tolerances), then `pyexodiff` will print out the maximum difference for each variable that is different as well as its position (node or element id):

```bash
$ pyexodiff.py test/simple_cube.e test/simple_cube_incorrect_coordx.e

pyexodiff: difference summary:

Variables:
    coordx is different:
      max absolute diff 1.0000e+00 at position 12
      max relative diff 6.6667e-01 at position 12

pyexodiff: files are different
```

`pyexodiff` can also be used as a module in a python script using

```python
from pyexodiff import exodiff

diff = exodiff(file1, file2, atol, rtol)
```
to return a dictionary of the differences.

In this case, the `pyexodiff` repository should be added to the `PYTHONPATH`
environment variable
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/pyexodiff
```

## Commandline options

Some parameters can be overwritten using the commandline options.

```bash
$ pyexodiff.py --help

usage: pyexodiff.py [-h] [--rtol RTOL] [--atol ATOL] file1 file2

Compares two Exodus II files

positional arguments:
  file1
  file2

optional arguments:
  -h, --help   show this help message and exit
  --rtol RTOL  Relative tolerance (default: 1e-06)
  --atol ATOL  Absolute tolerance (default: 1e-06)
  -q, --quiet  Quiet mode (only prints final message) (default: False)
```

## Test suite

`pyexodiff` includes a python script `run_tests.py` which uses the [pytest](https://pytest.org) framework to run the included tests. The test suite can be run using
```bash
./run_tests.py
```

New tests can be added anywhere within the `test` directory. The test harness recurses through this directory and all subdirectories looking for all instances of a `tests` file. This YAML file contains the details of each test in that directory.

The `tests` file syntax is basic YAML, and looks like:
```yml
simple_cube:
  file1: simple_cube.e
  file2: simple_cube.e
```
In this example, the test harness will run
```bash
pyexodiff simple_cube.e simple_cube.e
```
and determine whether the two files are identical.

The test harness can also test for expected error messages. For example, the following block in a `tests` file
```yml
simple_cube_missing_prop:
  file1: simple_cube.e
  file2: simple_cube_missing_prop.e
  expected_error: variable poro not in both files
```
will run
```bash
pyexodiff simple_cube.e simple_cube_missing_prop.e
```
and then check that the error message contains the string `variable poro not in both files`.

Each `tests` files can contain multiple individual tests. When pytest runs the test suite, the top-level label for each individual test in the `tests` file (for example, the labels `simple_cube` and `missing_specgrid` in the above examples) will be printed to the commandline, along with the status of each test run.

The test suite is run automatically on all pull requests to ensure that `pyexodiff` continues to work as expected.

## Contributors

`pyexodiff` has been developed by
- Chris Green, CSIRO ([cpgr](https://github.com/cpgr))

New contributions are welcome, using the pull request feature of GitHub.

## Feature requests/ bug reports

Any feature requests or bug reports should be made using the issues feature of GitHub. Pull requests are always welcome!
