import numpy as np
import random
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import pycbc
import pycbc.psd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--tnum', type=int, required=True, dest='template_number')
parser.add_argument('-s', '--seed', type=int, required=True, dest='random_seed')
args = parser.parse_args()

np.random.seed(args.random_seed)
def GenWaveforms (mass1, mass2, apx, ecc, lan, inc, f_low, freq_step):
    hptilde, hctilde = get_fd_waveform (approximant = apx,
                        mass1 = mass1,
                        mass2 = mass2,
                        eccentricity = ecc,
                        inclination = inc,
                        long_asc_nodes = lan,
                        f_lower = f_low,
                        delta_f = 1.0/freq_step)
    return hptilde

def GetMatch (waveform0p, waveform1p, psd_file, f_low=30.,freq_step=4):
	flen = max(len(waveform0p), len(waveform1p))
	waveform0p.resize(flen)
	waveform1p.resize(flen)
	# grab and use the psd file
	my_psd = pycbc.psd.read.from_txt(filename = psd_file, length = flen, delta_f = 1.0/4, low_freq_cutoff = f_low, is_asd_file = False)
	m,i = match(waveform0p, waveform1p, psd = my_psd, low_frequency_cutoff = f_low)
	return m

def GetFittingFactor (mass1, mass2, tp_m1, tp_m2, psd_file, f_low=30., freq_step=4):
    neighbor_counter = 0
    neighbor_matches = []
    this_waveform = GenWaveforms(mass1=mass1, mass2=mass2, apx='EccentricFD', ecc=0., lan=0., inc=0., f_low=f_low, freq_step=freq_step)
    for i in range(0,len(tp_m1)):
        m1_diff = abs(mass1 - tp_m1[i])
        m2_diff = abs(mass2 - tp_m2[i])
        if ((m1_diff <= 1.) and (m2_diff <= 1.)):
            neighbor_counter += 1
            neighbor_waveform = GenWaveforms(mass1=tp_m1[i], mass2=tp_m2[i], apx='EccentricFD', ecc=0., lan=0., inc=0., f_low=f_low, freq_step=freq_step)
            neighbor_match = GetMatch(waveform0p = this_waveform, waveform1p = neighbor_waveform, psd_file = psd_file)
            neighbor_matches.append(neighbor_match)
    if (neighbor_counter != 0):
        arr_neighbor_matches = np.asarray(neighbor_matches)
        ff = np.amax(arr_neighbor_matches)
    else:
        ff = 0
    return ff

my_tp_m1 = []
my_tp_m2 = []

print ("mass1, mass2")
k = 0
while k < args.template_number:    # get random parameters
    m1, m2 = np.random.uniform(low=20., high=30., size=2)
    fitting_factor = GetFittingFactor(mass1 = m1, mass2 = m2, tp_m1 = my_tp_m1, tp_m2 = my_tp_m2, psd_file ='H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt')
    if (fitting_factor < 0.97):
        k += 1
        my_tp_m1.append(m1)
        my_tp_m2.append(m2)
        print ("%f, %f" % (m1, m2))
    else: 
        continue

