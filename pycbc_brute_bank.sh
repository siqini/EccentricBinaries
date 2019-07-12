#!/bin/bash
tar -xzf env.tar.gz

module load python/2.7
virtualenv env
source env/bin/activate




OMP_NUM_THREADS=1 python -m cProfile -o log `which pycbc_brute_bank` \
--verbose \
--output-file nospinbank.hdf \
--minimal-match 0.965 \
--tolerance .001 \
--buffer-length 4 \
--sample-rate 2048 \
--tau0-threshold 0.5 \
--approximant TaylorF2 \
--tau0-crawl 10 \
--tau0-start 250 \
--tau0-end 520 \
--psd-file H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt \
--params mass1 mass2 \
--min 1.1 1.1 \
--max 1.6 1.6 \
--seed 1 \
--low-frequency-cutoff 30.0

deactivate

rm env.tar.gz
rm -rf env


OMP_NUM_THREADS=1 python -m cProfile -o log `which pycbc_brute_bank` \
--verbose \
--output-file nospinbank.hdf \
--minimal-match 0.965 \
--tolerance .001 \
--buffer-length 4 \
--sample-rate 2048 \
--tau0-threshold 0.5 \
--approximant TaylorF2 \
--tau0-threshold 200 \
--psd-file H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt \
--params mass1 mass2 \
--min 1.1 1.1 \
--max 1.6 1.6 \
--seed 1 \
--low-frequency-cutoff 30.0