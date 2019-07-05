Universe = vanilla
Executable = main_ecc_general.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/ecc_inj_ecc_$(Process).err
Output = /work/siqi.ni/out/ecc_inj_ecc_$(Process).out

Log = /work/siqi.ni/logs/ecc_inj_ecc_$(Process).log

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output_ecc0.txt
transfer_output_files = ecc_inj_output_ecc0.txt
WhenToTransferOutput = ON_EXIT

Arguments = 0
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output_ecc1.txt
transfer_output_files = ecc_inj_output_ecc1.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output_ecc2.txt
transfer_output_files = ecc_inj_output_ecc2.txt
WhenToTransferOutput = ON_EXIT

Arguments = 2
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output_ecc3.txt
transfer_output_files = ecc_inj_output_ecc3.txt
WhenToTransferOutput = ON_EXIT

Arguments = 3
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output_ecc4.txt
transfer_output_files = ecc_inj_output_ecc4.txt
WhenToTransferOutput = ON_EXIT

Arguments = 4
RequestCpus = 5
RequestMemory = 5000
Queue 1
