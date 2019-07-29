#!/bin/bash

tar -xzf env.tar.gz

module load python/2.7
virtualenv env
source env/bin/activate

python consistency.py --templates 'bank0723_atlas2_new.hdf' \
--psd 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt' \
--batch ${1} \
--mass_min 5.0 \
--mass_max 50.0 \
--mass_num 10 \
--ecc_min 0.0 \
--ecc_max 0.2 \
--ecc_num 10 \
--lan_min 0.0 \
--lan_max 6.28318530718 \
--lan_num 10 \
--inc_min 0.0 \
--inc_max 3.14159265359 \
--inc_num 10 \
--radius 0.05 

deactivate

rm env.tar.gz
rm -rf env
