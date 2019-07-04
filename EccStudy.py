import pycbc
from pycbc.waveform import get_fd_waveform
import numpy as np
import pycbc.coordinates as co
from pycbc.distributions import sky_location
import pycbc.psd
from pycbc.filter.matchedfilter import match

"""
function GenWaveforms
	Input: mass1 (float)
	       mass2 (float)
	       apx (string) a frequency-domain approximant
	       ecc (float) eccentricity [0,1]
	       lan (float) longitude of ascending nodes axis (in rad)
               inc (float) inclination (in rad)
               f_low (float) lower cutoff frequency (in Hz)
               freq_step (int) 1/delta_f, frequency step used to generate the waveform
	Output: [plus polarization waveform, cross polarization waveform] (a list of FrequencySeries)
"""
def GenWaveforms (mass1, mass2, apx, ecc, lan, inc, f_low, freq_step):
    hptilde, hctilde = get_fd_waveform (approximant = apx,
                        mass1 = mass1,
                        mass2 = mass2,
                        eccentricity = ecc,
                        inclination = inc,
			long_asc_nodes = lan,
                        f_lower = f_low,
                        delta_f = 1.0/freq_step)
    return [hptilde, hctilde]

"""
function EinheitlicheHimmel
	Input: sample_number (int)
	Output: [sample right ascensions, sample declinations] both arrays have n=sample_number entries of float, so you get that number of equatorial coordinates in radians
"""

def EinheitlicheHimmel (sample_number):
    uniform_sky_distribution = sky_location.UniformSky()
    solid_angle_samples = uniform_sky_distribution.rvs(sample_number)
    sample_ra = solid_angle_samples['ra']
    sample_dec = solid_angle_samples['dec']
    return [sample_ra, sample_dec]

"""
function GetMatch
	Input: waveform0p, waveform0c, waveform1p, waveform1c frequency-domain waveforms (FrequencySeries). 0 and 1 are indices for the two waveforms being compared, and p and c indicate plus/cross polarizations
	       detector_c, detector_p antenna patterns for some predetermined sky location and orientation at some detector. The observed waveforms at the detector will be a linear combo of p and c waveforms with detector_p and detector_c as expansion coefficients
	       psd_file (string)
	       f_low (float) lower cutoff frequency (in Hz)
	       freq_step (int) 1/delta_f
	Output: match between the two waveforms as observed by the detector (float)
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
function GetFittingFactor
	Input: mass1_index, mass2_index, inc_index, ecc_index, lan_index, sky_loc_index, pol_index injection parameter indices, all ints
	       tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc, tp_apx template bank parameters, all numpy arrays of the same length
               searching_radius (float) we only compute matches between two waveforms with a mchirp percentage difference smaller than this searching radius, otherwise it's gonna take forever and we do love our computers
	       f_low (float) lower cutoff frequency (in Hz)
	       freq_step (int) 1/delta_f
	Output: fitting factor (float) maximum match for the injection when recovered by the given template bank
"""

def GetFittingFactor (mass1_index, mass2_index, inc_index, ecc_index, lan_index, sky_loc_index, pol_index, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc,tp_apx, searching_radius, psd_file, inj_mass1, inj_mass2, inj_ecc, inj_lan, inj_inc, my_ras, my_decs,my_pols, my_detector, time, f_low=30., freq_step=4):
	inj_m1 = inj_mass1[mass1_index]
	inj_m2 = inj_mass2[mass2_index]
	inj_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(inj_m1, inj_m2)
	inj_waveforms = GenWaveforms(inj_m1, inj_m2, apx="EccentricFD", ecc=inj_ecc[ecc_index], lan=inj_lan[lan_index], inc=inj_inc[inc_index], f_low=f_low, freq_step=freq_step)
	inj_p = inj_waveforms[0]
	inj_c = inj_waveforms[1]
	# Get the antenna pattern at the Hanford detector
	ra = my_ras[sky_loc_index]
	dec = my_decs[sky_loc_index]
	pol_angle = my_pols[pol_index]
	fp, fc = my_detector.antenna_pattern(ra, dec, pol_angle, time)
	local_matches = np.zeros(len(tp_m1))
	relevant_temp_counter = 0
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
			relevant_temp_counter += 1
			one_relevant_temps = GenWaveforms(mass1 = this_tp_m1, mass2 = this_tp_m2, apx = tp_apx[k], ecc = tp_ecc[k], lan=tp_lan[k], inc=tp_inc[k], f_low = f_low, freq_step = freq_step)
			one_rel_temp_p = one_relevant_temps[0]
			one_rel_temp_c = one_relevant_temps[1]
			# compute the match
			this_local_match = GetMatch(waveform0p = inj_p, waveform0c = inj_c, waveform1p = one_rel_temp_p, waveform1c = one_rel_temp_c, detector_c = fc, detector_p = fp, psd_file=psd_file)
			local_matches[k] = this_local_match
	fitting_factor = np.amax(local_matches)
	print ("Injection mass1: %s" % inj_m1)
	print ("Injection mass2: %s" % inj_m2)
	print ("Injection inclination: %s" % inj_inc[inc_index])
	print ("Injection eccentricity: %s" % inj_ecc[ecc_index])
	print ("Injection long asc nodes: %s" % inj_long_asc_nodes[lan_index])
	print ("Injection RA: %s" % ra)
	print ("Injection Dec: %s" % dec)
	print ("Injection polarization angle: %s" % pol_angle)
	print ("Fitting factor: %s" % fitting_factor)
	return fitting_factor
