'''
Eccentric injections with stand.hdf
'''
import argparse
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import numpy as np
from datetime import datetime
import pycbc
import pycbc.psd
import h5py
import sys
from pycbc.detector import Detector
from pycbc.distributions import sky_location
import pycbc.coordinates as co

parser = argparse.ArgumentParser(description='Compute matches between non-ecc injections and non-ecc template bank')
parser.add_argument('-t', '--templates', type=str, required=True, dest='tbank_filename', help='filename of the template bank')
parser.add_argument('-p', '--psd', type=str, required=True, dest='psd_filename',help='filename of psd')
parser.add_argument('-b', '--batch', type=int, required=True, dest='batch_num')
parser.add_argument('-l', '--location_num', type=int, required=True, dest='loc_sample_num')
parser.add_argument('-o', '--pol_num', type=int, required=True, dest='pol_sample_num')
args = parser.parse_args()

start = datetime.now()
print ("Start time: %s" % start)



def GenWaveforms (mass1, mass2, apx, ecc, lan, inc, f_low=30., freq_step=4):
    hptilde,hctilde = get_fd_waveform(approximant=apx,
                           mass1=mass1,
                           mass2=mass2,
                           eccentricity = ecc,
                           long_asc_nodes = lan,
                           inclination = inc,
                           f_lower=f_low,
                           delta_f=1.0/freq_step)
    return [hptilde, hctilde]

# Generate injections
# Mass range: 1.1-1.6
# f_low = 30 (default)
# apx = "TaylorF2" (default)

# Construct the eccentric injection parameter spaec
masses2 = masses1 = np.linspace(1.1, 1.6, num=10)
my_inj_inc = np.linspace(0., np.pi, num=5)
my_inj_ecc = np.linspace(0., 0,4, num=5)
my_inj_long_asc_nodes = np.linspace(0., 2*np.pi, num=5)





# Grab non-eccentric template bank, COMMENT OUT FOR NOW

f_necc = h5py.File(args.tbank_filename, 'r')
necc_mass1 = f_necc['mass1'][:]
total_len = len(necc_mass1)
start_index = int(2*args.batch_num)
end_index = start_index + 2
if (end_index > total_len):
    end_index = total_len

necc_mass1 = necc_mass1[start_index:end_index]
necc_mass2 = f_necc['mass2'][start_index:end_index]
necc_apx = f_necc['approximant'][start_index:end_index]
ecc_ecc = np.zeros(len(necc_mass1))
ecc_lan = np.zeros(len(necc_mass1))
ecc_inc = np.zeros(len(necc_mass1))

f_necc.close()

my_time = 1000000000
d = Detector('H1')

def GetUniformSky (sample_number):
    uniform_sky_distribution = sky_location.UniformSky()
    solid_angle_samples = uniform_sky_distribution.rvs(sample_number)
    sample_ra = solid_angle_samples['ra']
    sample_dec = solid_angle_samples['dec']
    return [sample_ra, sample_dec]

location_sample_number = args.loc_sample_num
polarization_number = args.pol_sample_num
sky_location_samples = GetUniformSky(location_sample_number)
sample_ras = sky_location_samples[0]
sample_decs = sky_location_samples[1]
sample_pols = np.linspace(0,2*np.pi, num=polarization_number)



"""
GetMatch
Input: template0 injection waveform (restricted to one polarization)
       template1 template waveform (restricted to one polarization)
       psd_file string (default to "H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt")
       f_low float
Output: match between these two waveforms, float
"""

def GetMatch (waveform0p, waveform0c, waveform1p, waveform1c, detector_c, detector_p, psd_file, f_low=30.,freq_step=4):
	flen = max(len(waveform0p), len(waveform0c), len(waveform1p), len(waveform1c))
	waveform0p.resize(flen)
	waveform0c.resize(flen)
	waveform1p.resize(flen)
	waveform1c.resize(flen)
	waveform0_detector = detector_p * waveform0p + detector_c *waveform0c
	waveform1_detector = detector_p * waveform1p + detector_c *waveform1c
	# grab and use the psd file
	my_psd = pycbc.psd.read.from_txt(filename = psd_file, length = flen, delta_f = 1.0/4, low_freq_cutoff = f_low, is_asd_file = False)
	m,i = match(waveform0_detector, waveform1_detector, psd = my_psd, low_frequency_cutoff = f_low)
	return m

"""
GetGlobalMatch
Input: i_waveform0, j_waveform0 int double index of the injection waveform (restricted to one polarization)
       tp_apx list of strs
       tp_m1, tp_m2, tp_ecc, tp_lan, temp_inc np.array of float
       searching_radius float (only iterate through templates within a closed ball of mchirp of the injection;
                               given as a percentage of mchirp of the injection)
       f_low float threshold frequency
Output: maximum match in the bank for the given injection waveform0, float
"""

def GetFittingFactor (mass1_index, mass2_index, inc_index, ecc_index, lan_index, sky_loc_index, pol_index, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc,tp_apx, searching_radius, psd_file, inj_mass1, inj_mass2, inj_ecc, inj_lan, inj_inc, my_ras, my_decs,my_pols, my_detector, time, f_low=30., freq_step=4):
	inj_m1 = inj_mass1[mass1_index]
	inj_m2 = inj_mass2[mass2_index]
	inj_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(inj_m1, inj_m2)
    # Generate this injection waveforms (p and c)
	inj_waveforms = GenWaveforms(mass1=inj_m1, mass2=inj_m2, apx="EccentricFD", ecc=inj_ecc[ecc_index], lan=inj_lan[lan_index], inc=inj_inc[inc_index], f_low=f_low, freq_step=freq_step)
	inj_p = inj_waveforms[0]
	inj_c = inj_waveforms[1]
	# Get the antenna pattern at the Hanford detector
	ra = my_ras[sky_loc_index]
	dec = my_decs[sky_loc_index]
	pol_angle = my_pols[pol_index]
	fp, fc = my_detector.antenna_pattern(ra, dec, pol_angle, time)
	local_matches = np.zeros(len(tp_m1))
	# iterate through the given template bank
	for k in range(0,len(tp_m1)):
		this_tp_m1 = tp_m1[k]
		this_tp_m2 = tp_m2[k]
		this_tp_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(this_tp_m1, this_tp_m2)
		diff_mchirp = abs(inj_mchirp - this_tp_mchirp)
		percent_diff = diff_mchirp/inj_mchirp
		if (percent_diff > searching_radius):
			local_matches[k]=0.
		else:
			one_relevant_temps = GenWaveforms(mass1 = this_tp_m1, mass2 = this_tp_m2, apx = tp_apx[k], ecc = tp_ecc[k], lan=tp_lan[k], inc=tp_inc[k], f_low = f_low, freq_step = freq_step)
			one_rel_temp_p = one_relevant_temps[0]
			one_rel_temp_c = one_relevant_temps[1]
			# compute the match
			this_local_match = GetMatch(waveform0p = inj_p, waveform0c = inj_c, waveform1p = one_rel_temp_p, waveform1c = one_rel_temp_c, detector_c = fc, detector_p = fp, psd_file=psd_file)
			local_matches[k] = this_local_match
	fitting_factor = np.amax(local_matches)
	return fitting_factor


inj_counter = 0
# iterate through all injections
print ("inj_num, inj_mass1, inj_mass2, inj_inclination, inj_eccentricity, inj_lan, inj_ra, inj_dec, inj_pol, fitting_factor")
for i in range(0,len(masses1)): 
    for j in range(0,len(masses2)):
        for inc_ind in range(0,len(my_inj_inc)):
            for ecc_ind in range(0,len(my_inj_ecc)):
                for lan_ind in range(0,len(my_inj_long_asc_nodes)):
                    for loc_ind in range(0, len(sample_ras)):
                        for pol_ind in range(0, len(sample_pols)):
                            inj_counter += 1
                            this_ff = GetFittingFactor(mass1_ind = i,
                                                                mass2_ind = j,
                                                                inc_index = inc_ind,
                                                                ecc_index = ecc_ind,
                                                                lan_index = lan_ind,
                                                                sky_loc_index = loc_ind, 
                                                                pol_index = pol_ind,
                                                                tp_m1 = necc_mass1,
                                                                tp_m2 = necc_mass2,
                                                                tp_ecc = ecc_ecc,
                                                                tp_lan = ecc_lan,
                                                                tp_inc = ecc_inc,
                                                                tp_apx = necc_apx,
                                                                searching_radius = 0.05,
                                                                psd_file = args.psd_filename,
                                                                inj_mass1 = masses1,
                                                                inj_mass2 = masses2,
                                                                inj_ecc = my_inj_ecc,
                                                                inj_lan = my_inj_long_asc_nodes,
                                                                inj_inc = my_inj_inc,
                                                                my_ras = sample_ras,
                                                                my_decs = sample_decs,
                                                                my_pols = sample_pols,
                                                                my_detector = d,
                                                                time = my_time)
                            this_inj_mass1 = masses1[i]
                            this_inj_mass2 = masses2[j]
                            this_inj_inc = my_inj_inc[inc_ind]
                            this_inj_ecc = my_inj_ecc[ecc_ind]
                            this_inj_lan = my_inj_long_asc_nodes[lan_ind]
                            this_inj_ra = sample_ras[loc_ind]
                            this_inj_dec = sample_decs[loc_ind]
                            this_inj_pol = sample_pols[pol_ind]
                            print ("%d, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (inj_counter, this_inj_mass1, this_inj_mass2, this_inj_inc, this_inj_ecc, this_inj_lan, this_inj_ra, this_inj_dec, this_inj_pol, this_ff))
    


end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)
