#!/bin/bash

tar -xzf env.tar.gz

module load python/2.7
virtualenv env
source env/bin/activate

python eccentric_injections.py -t 1 -p 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt' -s 0.05 -b ${1} -l 0.0 -u 0.1

deactivate

rm env.tar.gz
rm -rf env
