#!/bin/bash

tar -xzf env.tar.gz

module load python/2.7
virtualenv env
source env/bin/activate

python main_batch.py -t 'stand.hdf' -p 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt' -b ${1}

deactivate

rm env.tar.gz
rm -rf env
