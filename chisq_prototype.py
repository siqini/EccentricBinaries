import argparse 
from pycbc.waveform import get_td_waveform
import h5py
from pycbc.filter.matchedfilter import match 
import pycbc 
import pycbc.psd 
import numpy as np
import pycbc.noise 
import pycbc.types 
import pycbc.filter 
import pycbc.waveform
import pycbc.vetoes
import requests
import json
import sys
import pycbc.pnutils
import matplotlib.pyplot as plt

import rescaling
import best_match

parser = argparse.ArgumentParser()
parser.add_argument('--sxs_id', type =str, required = True)
parser.add_argument('--sim_path', type = str, required = True)
parser.add_argument('--total_mass', type = float, required = True)
parser.add_argument('--seed', type = int, required = True)
parser.add_argument('--tbank', type =str, required = True)
parser.add_argument('--radius', type=float, required = True)
parser.add_argument('--psd_file', type = str, required = False, default = 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt')
args = parser.parse_args()

sp, sc = rescaling.rescale(args.sim_path, args.total_mass)

# load template bank
f_bank = h5py.File(args.tbank, 'r')
bank_mass1 = f_bank['mass1'][:]
bank_mass2 = f_bank['mass2'][:]
bank_ecc = f_bank['eccentricity'][:]
bank_lan = f_bank['long_asc_nodes'][:]
bank_inc = f_bank['inclination'][:]
bank_apx = f_bank['approximant'][:]
f_bank.close()

# compute component masses of the injected waveform 
request = requests.get("https://data.black-holes.org/catalog.json", headers={'accept': 'application/citeproc+json'})
sxs_full_json = request.json()
sxs_catalog_json = sxs_full_json['simulations']
mass_ratio = sxs_catalog_json[args.sxs_id]['reference_mass_ratio']
sim_m2 = args.total_mass/(mass_ratio+1.)
sim_m1 = args.total_mass - sim_m2
print ('Component mass1 = %s' % sim_m1)
print ('Component mass2 = %s' % sim_m2)
f_low = 30.

# find the best match template and fitting factor
ff, best_match_m1, best_match_m2, best_match_ecc, best_match_lan, best_match_inc = best_match.GetBestMatch(comp_mass1=sim_m1, comp_mass2=sim_m2, waveform0=sp, tp_apx=bank_apx, tp_m1=bank_mass1, tp_m2=bank_mass2, tp_ecc=bank_ecc, tp_lan=bank_lan, tp_inc=bank_inc, radius = args.radius, f_low = f_low, psd_file = args.psd_file)
print ('Fitting factor = %s' % ff)
print ('Best match mass1 = %s' % best_match_m1)
print ('Best match mass2 = %s' % best_match_m2)

flen0 = len(sp)//2 + 1
delta_f0 = sp.delta_f

psd1 = pycbc.psd.read.from_txt(filename = args.psd_file, length = flen0, delta_f = delta_f0, low_freq_cutoff = f_low, is_asd_file = False)

snr = pycbc.filter.matched_filter(sp, sp, psd = psd1, low_frequency_cutoff = f_low)
snr = snr[len(snr)//4 : len(snr)*3//4]
peak = abs(snr).numpy().argmax()
snrp = snr[peak]
peak_time = snr.sample_times[peak]
snrp_norm = abs(snrp)

scalar = 10./snrp_norm 
rescaled_strains = np.array(sp)*scalar
sp_rescaled = pycbc.types.timeseries.TimeSeries(initial_array = rescaled_strains, delta_t = sp.delta_t)

snr_rescaled = pycbc.filter.matched_filter(sp_rescaled, sp_rescaled, psd = psd1, low_frequency_cutoff = f_low)
snr_rescaled = snr_rescaled[len(snr_rescaled)//4 : len(snr_rescaled)*3//4]
peak_rescaled = abs(snr_rescaled).numpy().argmax()
snrp_rescaled = snr_rescaled[peak_rescaled]
peak_time_rescaled = snr_rescaled.sample_times[peak_rescaled]
snrp_norm_rescaled = abs(snrp_rescaled)

print ('SNR of the rescaled signal: %s' % snrp_norm_rescaled)
sys.stdout.flush()

delta_t = sp_rescaled.delta_t 
duration = sp_rescaled.duration 
tsamples = int(duration/delta_t)
noise = pycbc.noise.noise_from_psd(tsamples, delta_t, psd1, seed = args.seed)

# generate the template filter 
hp, hc = get_td_waveform(approximant = 'EccentricTD', mass1 = best_match_m1, mass2 = best_match_m2, eccentricity = best_match_ecc, long_asc_nodes = best_match_lan, inclination = best_match_inc, f_lower = f_low, delta_t = delta_t)

signal_plus_noise = sp_rescaled + noise 
delta_f = signal_plus_noise.delta_f 

tlen1 = max(len(hp), len(signal_plus_noise))
hp.resize(tlen1)
signal_plus_noise.resize(tlen1)
flen = tlen1//2 + 1

psd2 = pycbc.psd.read.from_txt(filename = args.psd_file, length = flen, delta_f = delta_f, low_freq_cutoff = f_low, is_asd_file = False)

num_bins = int(0.72*pycbc.pnutils.get_freq('fSEOBNRv4Peak', best_match_m1, best_match_m2, 0., 0.)**0.7)

chisq = pycbc.vetoes.power_chisq(hp, signal_plus_noise, num_bins, psd2, low_frequency_cutoff=f_low)
chisq /= (num_bins * 2) - 2

fig = plt.figure()
plt.plot(chisq.sample_times, chisq)
plt.xlabel('time (s)')
plt.ylabel('$\Chi^2$')
plt.savefig('chisq_plt1.png')
