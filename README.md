# pyExodiff - pure python exodiff

[![Build Status](https://travis-ci.com/cpgr/pyexodiff.svg?branch=master)](https://travis-ci.com/cpgr/pyexodiff)

`pyexodiff` compares two [Exodus II](https://github.com/gsjaardema/seacas) files to determine
whether they are identical. It is intended as a python replacement of the [Exodiff](https://github.com/gsjaardema/seacas) utility, allowing two Exodus II files to be compared without the need to install SEACAS.

## Setup

`pyexodiff` requires the following python packages to be installed:

- numpy
- netCDF4

These may typically already installed, but if not, can be installed using `pip`,
```bash
pip install numpy
```

An additional python package, `pytest`, is required to run the test script. Again, this can be installed using
```bash
pip install pytest
```

## Usage

`pyexodiff` can be used as a standalone utility to compare two Exoduss II files on the commandline using

```bash
./pyexodiff.py file1 file2
```

`pyexodiff` can also be used as a module in a python script using

```python
from pyexodiff import exodiff
```
for example. In this case, the `pyexodiff` repository should be added to the `PYTHONPATH`
environment variable
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/pyexodiff
```


## Commandline options



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
