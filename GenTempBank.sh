#!/bin/bash

tar -xzf env.tar.gz

module load python/2.7
virtualenv env
source env/bin/activate

python GenTempBank.py -n 20 -s ${1}

deactivate

rm env.tar.gz
rm -rf env