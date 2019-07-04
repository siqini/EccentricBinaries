"""
Eccentric injections with non-eccentric template bank
"""
import argparse
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pycbc
import pycbc.psd
import h5py
import sys
from pycbc.detector import Detector

import EccStudy

parser = argparse.ArgumentParser(description='Compute matches between eccentric injections and non-ecc template bank')
parser.add_argument('-t', '--templates', type=str, required=True, dest='tbank_filename', help='filename of the template bank')
parser.add_argument('-p', '--psd', type=str, required=True, dest='psd_filename',help='filename of psd')
parser.add_argument('-s', '--radius', type=float, required=False, dest='searcing_radius', help='searching radius', default = 0.05)
parser.add_argument('-b', '--batchnum', type=int, required=True, dest='batch_num', help = 'batch number')
parser.add_argument('-l', '--ecc_lb', type=float, required=True,
dest='ecc_lower_bound', help='eccentricity lower bound')
parser.add_argument('-u', '--ecc_ub', type=float, required=True,
dest='ecc_upper_bound', help='eccentricity upper bound')
parser.add_argument('-f', '--fileind', type=int, required=True, dest='file_ind', help='filename index')
parser.add_argument('-m', '--masses_num', type=int, required=False, dest='mass_num', default=10)
parser.add_argument('-i', '--inclination_num', type=int, required=False, dest='inc_num', default=10)
parser.add_argument('-e', '--eccentricity_num', type=int, required=False, dest='ecc_num', default=10)
parser.add_argument('-a', '--long_asc_nodes_num', type=int, required=False, dest='lan_num', default=10)
args = parser.parse_args()

start = datetime.now()
print ("Start time: %s" % start)

my_txt_files = ['ecc_inj_output0.txt', 'ecc_inj_output1.txt', 'ecc_inj_output2.txt', 'ecc_inj_output3.txt', 'ecc_inj_output4.txt']



# Construct the injection parameter space
mass_num = args.mass_num
inc_num = args.inc_num
ecc_num = args.ecc_num
long_asc_nodes_num = args.lan_num
inj_mass1 = inj_mass2 = np.linspace(1.1,1.6,num=mass_num)
inj_inc = np.linspace(0.,np.pi,num=inc_num)
inj_ecc = np.linspace(0.,0.4, num=ecc_num)
inj_long_asc_nodes = np.linspace(0., 2*np.pi, num=long_asc_nodes_num)

# Grab the non-eccentric template bank
f_necc = h5py.File(args.tbank_filename, 'r')
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


# Select fitting factors for plotting
# Fix some eccentricity, and then contour plot fitting factor against m1*m2
#eccentricity_lower_bound = 0.
#eccentricity_upper_bound = 0.04
axis_data_pt_counter = (mass_num**2)*inc_num*lan_num*loc_num*pol_num*2
fitting_factors = []
m1s = []
m2s = []

for m1_ind in [args.batch_num*2, (args.batch_num*2)+1]:
	for ecc_ind in range(0,ecc_num):
		if (inj_ecc[ecc_ind] <= args.ecc_upper_bound) and (inj_ecc[ecc_ind] >= args.ecc_lower_bound):
			for m2_ind in (0,mass_num):
				for inc_ind in range(0,inc_num):
					for lan_ind in range(0,long_asc_nodes_num):
						for loc_ind in range(0,location_sample_num):
							for pol_ind in range(0,polarization_num):
								fitting_factors.append(mass1_index=m1_ind,
								mass2_index=m2_ind,
								inc_index=inc_ind,
								ecc_index=ecc_ind,
								lan_index=lan_ind,
								sky_loc_index=loc_ind,
								pol_index=pol_ind,
								tp_m1=necc_mass1,
								tp_m2=necc_mass2,
								tp_ecc=np.zeros(len(necc_mass1)),
								tp_lan=np.zeros(len(necc_mass1)),
								tp_inc=np.zeros(len(necc_mass1)),
								tp_apx=necc_apx,
								searching_radius=args.searching_radius,
								psd_file=args.psd_filename)
								m1s.append(inj_mass1[m1_ind])
								m2s.append(inj_mass2[m2_ind])

# Convert plotted lists into arrays
arr_fitting_factors = np.asarray(fitting_factors)
arr_m1 = np.asarray(m1s)
arr_m2 = np.asarray(m2s)

# Save into file
arr_fitting_factors = np.reshape(arr_fitting_factors, (len(arr_fitting_factors),1))
arr_m1 = np.reshape(arr_m1, (len(arr_m1),1))
arr_m2 = np.reshape(arr_m2, (len(arr_m2),1))
my_arr = np.hstack((arr_m1, arr_m2, arr_fitting_factors))

with open(my_txt_files[args.file_ind], "ab") as f:
	np.savetxt(f, X=my_arr, delimiter=',')
f.close()

# Compute runtime
end = datetime.now()
total_runtime = end-start
print ("End time: %s" % end)
print ("Runtime: %s" % total_runtime)
