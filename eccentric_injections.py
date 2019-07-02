"""
Eccentric injections
"""
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pycbc
import pycbc.psd
import h5py
import sys
from pycbc.detector import Detector

import EccStudy

sys.stout = open("ecc_inj_output.txt", 'w')

start = datetime.now()
print ("Start time: %s" % start)
sys.stdout.flush()

# Construct the injection parameter space
mass_num = 10
inc_num = 10
ecc_num = 10
long_asc_nodes_num = 10
inj_mass1 = inj_mass2 = np.linspace(1.1,1.6,num=mass_num)
inj_inc = np.linspace(0.,np.pi,num=inc_num)
inj_ecc = np.linspace(0.,0.4, num=ecc_num)
inj_long_asc_nodes = np.linspace(0., 2*np.pi, num=long_asc_nodes_num)

# Grab the non-eccentric template bank
f_necc = h5py.File('./stand.hdf', 'r')
necc_mass1 = f_necc['mass1'][:]
necc_mass2 = f_necc['mass2'][:]
necc_apx = f_necc['approximant'][:]

# Also fix a time.
time = 1000000000

#Grab my unit ball (uniform sky)
location_sample_number = 1000
polarization_num = 10
sky_location_samples = EccStudy.EinheitlicheHimmel(sample_number=location_sample_number)
sample_ras = sky_location_samples[0]
sample_decs = sky_location_samples[1]
sample_pols = np.linspace(0, 2*np.pi, num=polarization_num)

d = Detector("H1")

# Compute total injection number
total_inj_num = (mass_num**2)*inc_num*ecc_num*long_asc_nodes_num*location_sample_number*polarization_num
print ("Total injection number: %s" % total_inj_num)
sys.stdout.flush()

# Initate an array to store fitting factors
fitting_factors = np.ndarray(shape=(mass_num, mass_num, inc_num, ecc_num, long_asc_nodes_num, location_sample_num, polarization_num), dtype=float)

# Compute the fitting factors
for m1_ind in range(0,mass_num):
	for m2_ind in range(0,mass_num):
		for inc_ind in range(0,inc_num):
			for lan_ind in range(0,long_asc_nodes_num):
				for loc_ind in range(0,location_sample_num):
					for pol_ind in range(0,polarization_num):
						for ecc_ind in range(0,ecc_num):
							this_fit_fac = GetFittingFactor(mass1_index = m1_ind, mass2_index = m2_ind, inc_index = inc_ind, ecc_index = ecc_ind, lan_index = lan_ind, sky_loc_index = loc_ind, pol_index = pol_ind,tp_m1 = necc_mass1, tp_m2 = necc_mass2, tp_ecc = np.zeros(len(necc_mass1)), tp_lan = np.zeros(len(necc_mass1)), tp_inc = np.zeros(len(necc_mass1)), tp_apx = necc_apx, searching_radius = 0.05)
							fitting_factors[mass1_ind][mass2_ind][inc_ind][ecc_ind][lan_ind][loc_ind][pol_ind] = this_fit_fac

# Select fitting factors for plotting
# Fix some eccentricity, and then contour plot fitting factor against m1*m2
eccentricity_lower_bound = 0.
eccentricity_upper_bound = 0.04
axis_data_pt_counter = (mass_num**2)*inc_num*lan_num*loc_num*pol_num*2
plotted_fitting_factors = []
plotted_m1 = []
plotted_m2 = []
for i in range(0,ecc_num):
	if (inj_ecc[i]<= 0.04):
		 for m1_ind in range(0,mass_num):
			for m2_ind in range(0,mass_num):
				for inc_ind in range(0,inc_num):
					for lan_ind in range(0,long_asc_nodes_num):
						for loc_ind in range(0,location_sample_num):
							for pol_ind in range(0,polarization_num):
								plotted_fitting_factors.append(fitting_factors[m1_ind][m2_ind][inc_ind][ecc_ind][lan_ind][loc_ind][pol_ind])
								plotted_m1.append(inj_mass1[m1_ind])
								plotted_m2.append(inj_mass2[m2_ind])						
# Convert plotted lists into arrays
arr_plotted_fitting_factors = np.asarray(plotted_fitting_factors)
arr_plotted_m1 = np.asarray(plotted_m1)
arr_plotted_m2 = np.asarray(plotted_m2)

# Actually plot
plt.figure()
my_plot = plt.scatter(arr_plotted_m1, arr_plotted_m2, c=arr_plotted_fitting_factors, s=50, cmap = 'plasma')
plt.colorbar()
plt.xlabel('mass1 (solar mass)')
plt.ylabel('mass2 (solar mass)')
plt.show()

# Compute runtime
end = datetime.now()
total_runtime = end-start
print ("End time: %s" % end)
sys.stdout.flush()
print ("Runtime: %s" % total_runtime)
sys.stdout.flush()
