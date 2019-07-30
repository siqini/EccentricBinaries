#!/bin/bash

python consistency_int.py --templates 'bank0729_atlas1_new.hdf' \
--psd 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt' \
--mass_min 5.0 \
--mass_max 50.0 \
--mass_num 5 \
--ecc_min 0.0 \
--ecc_max 0.2 \
--ecc_num 5 \
--lan_min 0.0 \
--lan_max 6.28318530718 \
--lan_num 5 \
--inc_min 0.0 \
--inc_max 3.14159265359 \
--inc_num 5 \
--radius 0.01 

deactivate


