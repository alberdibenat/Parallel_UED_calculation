# Parallel_UED_calculation
Calculation of random UED data points inside the pre-defined parameter range by using the SRF Photoinjector Astra model. The calculation is paralellized to be run in a multi-core server.  

The project runs by executing "Surrogated_model_production_FBL_SC.py". Inside this file one chooses the number of cores that wants to use and the ranges for the machine parameters that will be used for the random data point generation. This then calls "runAstra_surrogated_FBL_SC_nopandas.py" which runs the generator first (already updated to produce the expected intrinsic emittance of 0.56mm-mrad/mm(rms)) and then the SRF Photoinjector mode stored in Astra_files. There are two models, one for upstream the aperture which includes SC forces, and one downstream the aperture which neglects SC forces. In the aperture located in between these two model ranges the phase-space is filtered and then refilled using "Distribution_refill.py". The later code is not properly optimized.  

The initial parameters will be stored in "X_values_xxx.txt" and the results at the target position of 7.64m will be stored in "Y_values_xxx.txt". The calculation is made in batches of 1000 runs, after which the output files are updated.

**Disclaimer**: This code is design to be run with python 2.x and not with python 3.x, as the later is not available in the linux server where the code runs. The code also needs to be run without pandas, which would have made many tasks easier and faster.
