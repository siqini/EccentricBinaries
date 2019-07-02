import pycbc
from pycbc.waveform import get_fd_waveform
import numpy as np
import pycbc.coordinates as co
from pycbc.distributions import sky_location
import pycbc.psd
from pycbc.filter.matchedfilter import match

def GenWaveforms (mass1, mass2, apx, ecc, lan, inc, f_low, freq_step):
    hptilde, hctilde = get_fd_waveform (approximant = apx,
                        mass1 = mass1,
                        mass2 = mass2,
                        eccentricity = ecc,
                        inclination = inc,
			long_asc_nodes = lan,
                        f_lower = f_low,
                        delta_f = 1.0/freq_step)
    return [hptilde, hctile]

def EinheitlicheHimmel (sample_number):
    uniform_sky_distribution = sky_location.UniformSky()
    solid_angle_samples = uniform_sky_distribution.rvs(sample_number)
    sample_ra = solid_angle_samples['ra']
    sample_dec = solid_angle_samples['dec']
    return [sample_ra, sample_dec]

def GetMatch (waveform0p, waveform0c, waveform1p, waveform1c, detector_c, detector_p, psd_file='./H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt', f_low=30.,freq_step=4):
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

def GetFittingFactor (mass1_index, mass2_index, inc_index, ecc_index, lan_index, sky_loc_index, pol_index, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc,tp_apx, searching_radius, f_low=30., freq_step=4):
	inj_m1 = inj_mass1[mass1_index]
	inj_m2 = inj_mass2[mass2_index]
	inj_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(inj_m1, inj_m2)
	inj_waveforms = GenWaveforms(inj_m1, inj_m2, apx="EccentricFD", ecc=inj_ecc[ecc_index], lan=inj_long_asc_nodes[lan_index], inc=inj_inc[inc_index], f_low=f_low, freq_step=freq_step)
	inj_p = inj_waveforms[0]
	inj_c = inj_waveforms[1]
	# Get the antenna pattern at the Hanford detector
	ra = sample_ras[sky_loc_index]
	dec = sample_decs[sky_loc_index]
	pol_angle = sample_pols[pol_index]
	fp, fc = d.antenna_pattern(ra, dec, pol_angle, time)	
	local_matches = np.zeros(len(tp_m1))
	relevant_temp_counter = 0
	# iterate through the given template bank
	for k in range(0,len(tp_m1)):
		this_tp_m1 = tp_m1[k]
		this_tp_m2 = tp_m2[k]
		this_tp_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(this_tp_m1, this_tp_m2)
		diff_mchirp = abs(inj_mchirp - this_tp_mchirp)
		percent_diff = diff_mchirp/inj_mchirp
		if (percent_difference > searching_radius):
			local_matches[k]=0.
		else:
			relevant_temp_counter += 1
			one_relevant_temps = GenWaveforms(mass1 = this_tp_m1, mass2 = this_tp_m2, apx = tp_apx[k], ecc = tp_ecc[k], lan=tp_lan[k], inc=tp_inc[k], f_low = f_low, freq_step = freq_step)
			one_rel_temp_p = one_relevant_temps[0]
			one_rel_temp_c = one_relevant_temps[1]
			# compute the match				 
			this_local_match = GetMatch(waveform0p = inj_p, waveform0c = inj_c, waveform1p = one_rel_temp_p, waveform1c = one_rel_temp_c, detector_c = fc, detector_p = fp)
			local_matches[k] = this_local_match
	fitting_factor = np.amax(local_matches)
	print ("Injection mass1: %s" % inj_m1)
	sys.stdout.flush()
	print ("Injection mass2: %s" % inj_m2)
	sys.stdout.flush()
	print ("Injection inclination: %s" % inj_inc[inc_index])
	sys.stdout.flush()
	print ("Injection eccentricity: %s" % inj_ecc[ecc_index])
	sys.stdout.flush()
	print ("Injection long asc nodes: %s" % inj_long_asc_nodes[lan_index])
	sys.stdout.flush()
	print ("Injection RA: %s" % ra)
	sys.stdout.flush()
	print ("Injection Dec: %s" % dec)
	sys.stdout.flush()
	print ("Injection polarization angle: %s" % pol_angle)
	sys.stdout.flush()
	print ("Fitting factor: %s" % fitting_factor)
	sys.stdout.flush()			
	return fitting_factor
