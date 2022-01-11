import sys
import numpy as np
import random
from runAstra_surrogated_FBL_SC_nopandas import runAstraFunction_FBL_SC_surrogated 
from datetime import datetime
import multiprocessing as mp
from multiprocessing import cpu_count
import time


n_block = 100
for i in range(n_block):
	n_iterations = 1000
	#Create initial value for 100 calculations
	random.seed(datetime.now())
	#Bounds for: q_bunch [nC], rms_time [ns], rms_laser [mm], phase_gun, amplitude_gun, amplitude_solenoid [T], phase_b1, amplitude_b1, phase_b2, amplitude_b2, phase_b3, amplitude_b3
	bounds = [(0.5e-3,5.0e-3),(1e-3,10e-3),(0.5,2.0),(-10.0,10.0),(16.0,25.0),(0.05,0.075),(-180.0,180.0),(0.0,10.0),(-180.0,180.0),(0.0,10.0),(-180.0,180.0),(0.0,10.0)]
	#run_numbers = random.sample(range(1, 1000000), n_iterations)
	run_numbers = range(0, n_iterations)
	all_X = [(random.random()*(bounds[0][1]-bounds[0][0])+bounds[0][0],random.random()*(bounds[1][1]-bounds[1][0])+bounds[1][0],
	    0.5,random.random()*(bounds[3][1]-bounds[3][0])+bounds[3][0],
	    20.0,random.random()*(bounds[5][1]-bounds[5][0])+bounds[5][0],
	    random.random()*(bounds[6][1]-bounds[6][0])+bounds[6][0],random.random()*(bounds[7][1]-bounds[7][0])+bounds[7][0],
	    random.random()*(bounds[8][1]-bounds[8][0])+bounds[8][0],random.random()*(bounds[9][1]-bounds[9][0])+bounds[9][0],
	    random.random()*(bounds[10][1]-bounds[10][0])+bounds[10][0],random.random()*(bounds[11][1]-bounds[11][0])+bounds[11][0],
	    run_numbers[i]) for i in range(n_iterations)] 
	
	#pool = Pool(cpu_count()) 
	    
	def wrapper_function(args):
	    return runAstraFunction_FBL_SC_surrogated(*args)
	
	
	
	##iterable = [1, 2, 3, 4, 5]
	pool = mp.Pool(50)
	##a = "hi"
	##b = "there"
	##parameters = [(a,b,str(iterable[i])) for i in range(len(iterable))]
	
	
	results = pool.map(wrapper_function, all_X)
	pool.close()
	#print(results)
		
	
	all_X = np.asarray(all_X)
	all_Y = np.asarray(results)
	
	
	In_filename = 'X_values_FBL_SC_aperture_updated.txt'
	Out_filename = 'Y_values_FBL_SC_aperture_updated.txt'
	
	with open(In_filename,'a') as infile:
	    Input = np.savetxt(infile, all_X[:,:12], delimiter=',')
	    infile.close()
	
	with open(Out_filename,'a') as outfile:
	    Output = np.savetxt(outfile, all_Y, delimiter=',')
	    outfile.close()

