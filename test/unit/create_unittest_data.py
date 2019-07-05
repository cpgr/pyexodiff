#!/usr/bin/env python

import numpy as np
from netCDF4 import Dataset

# Create test netCDF4 file with two variable names, formatted like the Exodus II
# specification

rootgrp1 = Dataset('varnames.nc', 'w', format = 'NETCDF4')

varname1 = ['variable1', 'variable2', 'variable3', 'variable4']
varname2 = ['variable3', 'variable4', 'variable1', 'variable2']

rootgrp1.createDimension('num_vars', 4)
rootgrp1.createDimension('len_string', 30)

rootgrp1.createVariable('varnames1', 'S1', ('num_vars', 'len_string'))
rootgrp1.createVariable('varnames2', 'S1', ('num_vars', 'len_string'))

for i in range(len(varname1)):
    rootgrp1.variables['varnames1'][i, 0:len(varname1[i])] = [c for c in varname1[i]]

for i in range(len(varname2)):
    rootgrp1.variables['varnames2'][i, 0:len(varname2[i])] = [c for c in varname2[i]]

# Close the file
rootgrp1.close()
