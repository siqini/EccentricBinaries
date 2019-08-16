from pycbc.waveform import get_td_waveform 
from pycbc.filter.matchedfilter import match 
import pycbc.psd 
import numpy as np 
import pycbc.conversions

def GetMatch (waveform0, waveform1, psd_file, f_low):
    tlen = max(len(waveform0), len(waveform1))
    waveform0.resize(tlen)
    waveform1.resize(tlen)

    flen = tlen//2 +1 
    my_psd = pycbc.psd.read.from_txt(filename = psd_file, length = flen, delta_f = waveform0.delta_f, low_freq_cutoff = f_low, is_asd_file = False)
    m,i = match(waveform0, waveform1, psd = my_psd, low_frequency_cutoff = f_low)
    return m

def GetBestMatch (comp_mass1, comp_mass2, waveform0, tp_apx, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc, radius, f_low, psd_file):
    waveform0_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(comp_mass1, comp_mass2)
    matches = []
    for k in range(0, len(tp_m1)):
        template_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(tp_m1[k], tp_m2[k])
        diff = abs(waveform0_mchirp - template_mchirp)
        percentage_diff = diff/waveform0_mchirp
        if (percentage_diff > radius):
            matches.append(0.)
        else: 
            sp, sc = get_td_waveform(approximant = 'EccentricTD', mass1 = tp_m1[k], mass2 = tp_m2[k], eccentricity = tp_ecc[k], long_asc_nodes = tp_lan[k], inclination = tp_inc[k], f_lower = f_low, delta_t = waveform0.delta_t)
            matches.append(GetMatch(waveform0 = waveform0, waveform1 = sp, psd_file = psd_file, f_low = f_low))
    
    matches = np.asarray(matches)
    ff = np.amax(matches)
    ff_index = int(np.argmax(matches))
    best_match_m1 = tp_m1[ff_index]
    best_match_m2 = tp_m2[ff_index]
    best_match_ecc = tp_ecc[ff_index]
    best_match_lan = tp_lan[ff_index]
    best_match_inc = tp_inc[ff_index]
    return ff, best_match_m1, best_match_m2, best_match_ecc, best_match_lan, best_match_inc