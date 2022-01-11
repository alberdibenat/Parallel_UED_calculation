import os
import subprocess
import sys
import numpy as np
from Distribution_refill import refill_distribution


class CompletedProcess:
    def __init__(self,args,returncode,stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def check_returncode(self):
        if self.returncode != 0:
            err = subprocess.CalledProcessError(self.returncode,self.args,output = self.stdout)
            raise err
        return self.returncode


def run_process(*popenargs,**kwargs):
    input = kwargs.pop("input", None)
    check = kwargs.pop("handle",False)

    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        outs, errs = process.communicate(input)
    except:
        process.kill()
        process.wait()
        raise
    returncode = process.poll()
    if check and returncode:
        raise subprocess.CalledProcessError(returncode, popenargs, output=outs)
    return CompletedProcess(popenargs,returncode, stdout=outs, stderr=errs)



def runAstraFunction_FBL_SC_surrogated(q_bunch,rms_time,laser_size,phase_gun,amplitude_gun,amplitude_solenoid,phase_booster1,amplitude_booster1,phase_booster2, amplitude_booster2, phase_booster3, amplitude_booster3, run_number):


    origin = os.getcwd() #to save in which folder we are
    
    generator_template = 'Astra_files/generator_updated.template' #The generator template to copy
    generator_file = 'Astra_files/generator'+'{:06d}'.format(run_number) + '.in' #The changed generator file with our variables

    template_file_SC = 'Astra_files/3boosters_FBL_SC.template' #The template to copy
    input_file_SC = 'Astra_files/3boosters'+'{:06d}'.format(run_number) + '_FBL_SC.in' #The changed template file with our variables

    template_file_noSC = 'Astra_files/3boosters_FBL_noSC.template' #The template to copy
    input_file_noSC = 'Astra_files/3boosters' + '{:06d}'.format(run_number) + '_FBL_noSC.in' #The changed template file with our variables
    
    hnu = 2.32  #green light, eV
    MTE = 0.16  #mean transverse energy, eV (from the photoinjector guide, figure 7.10)
    electron_mass = 0.511e6 #eV
    #nEmitX = (laser_size*1e-3*np.sqrt(MTE/(3*electron_mass)))*1e6
    #nEmitY = nEmitX 

    #Copy the generator template file and introduce our parameters
    with open(generator_template, "r") as generator1:
        generator_contents = generator1.read()
        replaced_contents = generator_contents.replace('@Number@', str('{:06d}'.format(run_number)))
        replaced_contents = replaced_contents.replace('@Q_total@', str('{:.06f}'.format(q_bunch)))
        replaced_contents = replaced_contents.replace('@RMS_time@', str('{:.06f}'.format(rms_time)))
        replaced_contents = replaced_contents.replace('@LaserX@', str('{:.06f}'.format(laser_size)))
        replaced_contents = replaced_contents.replace('@LaserY@', str('{:.06f}'.format(laser_size)))
        #replaced_contents = replaced_contents.replace('@NEmitX@', str('{:.06f}'.format(nEmitX)))
        #replaced_contents = replaced_contents.replace('@NEmitY@', str('{:.06f}'.format(nEmitY)))
        generator1.close()

    with open(generator_file, "w") as generator2:
        generator2.write(replaced_contents)
        generator2.close()

        
    #Copy the template file and introduce our parameters
    with open(template_file_SC, "r") as file1:
        contents = file1.read()
        replaced_contents = contents.replace('@Number@', str('{:06d}'.format(run_number)))
        replaced_contents = replaced_contents.replace('@gun_phase@', str('%.5f'%phase_gun))
        replaced_contents = replaced_contents.replace('@E0_gun@', str('%.5f'%amplitude_gun))
        replaced_contents = replaced_contents.replace('@Bmax@', str('%.5f'%amplitude_solenoid))
        file1.close()

    with open(input_file_SC, "w") as file2:
        file2.write(replaced_contents)
        file2.close()

    with open(template_file_noSC, "r") as file3:
        contents = file3.read()
        replaced_contents = contents.replace('@Number@', str('{:06d}'.format(run_number)))
        replaced_contents = replaced_contents.replace('@cavity_phase1@', str('%.5f'%phase_booster1))
        replaced_contents = replaced_contents.replace('@E0max1@', str('%.5f'%amplitude_booster1))
        replaced_contents = replaced_contents.replace('@cavity_phase2@', str('%.5f'%phase_booster2))
        replaced_contents = replaced_contents.replace('@E0max2@', str('%.5f'%amplitude_booster2))
        replaced_contents = replaced_contents.replace('@cavity_phase3@', str('%.5f'%phase_booster3))
        replaced_contents = replaced_contents.replace('@E0max3@', str('%.5f'%amplitude_booster3))
	file3.close()

    with open(input_file_noSC, "w") as file4:
        file4.write(replaced_contents)
        file4.close()
    
    subprocess.run = run_process
    try:
    	generator_run = subprocess.run(['./Astra_files/generator', str(generator_file)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	#move = subprocess.call('mv Dist'+'{:06d}'.format(run_number) + '.ini Astra_files/', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.run(['./Astra_files/Astra', str(input_file_SC)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	#run = subprocess.run(['./Astra_files/Astra', str(input_file_noSC)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	move = subprocess.call('mv Astra_files/3boosters' + '{:06d}'.format(run_number) + '_FBL_SC.0174.001 .', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	Qbunch_final = refill_distribution('3boosters' + '{:06d}'.format(run_number) + '_FBL_SC.0174.001',0.00025,20000)
    	run = subprocess.run(['./Astra_files/Astra', str(input_file_noSC)], stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    except:
    	print('--> Woops, something went wrong in run ' + '{:06d}'.format(run_number)+ ', this run will return np.inf')

    #-------------------------------------------OUTPUT ANALYSIS---------------------------------------
    
    output_file_ref = 'Astra_files/3boosters' + '{:06d}'.format(run_number) + '_FBL_noSC.0764.001'
    try:
        output_list = np.loadtxt(output_file_ref)
        #print(output_list)
    except:
    	run = subprocess.call('rm Dist' + '{:06d}'.format(run_number) + '.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.call('rm 3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.0174.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(run_number)+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_noSC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        return np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf

    #output_dataframe.columns=['x','y','z','px','py','pz','clock','macro_charge','particle_index','status']
    status = output_list[:,9:10]
#    print(status)
    if any(status<0):
    	run = subprocess.call('rm Dist'+'{:06d}'.format(run_number)+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.call('rm 3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.0174.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(run_number)+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_noSC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        return np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf
    
    output_file_bunch_z = 'Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_noSC.Zemit.001'
    #bunch_dataframe.columns=['z_bunch','t_bunch','Ekin_bunch','bunch_size','delta_e_bunch','emittance_z_norm','z_e_derivative']
    bunch_list_z = np.loadtxt(output_file_bunch_z)

    output_file_bunch_x = 'Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_noSC.Xemit.001'
    #bunch_dataframe.columns=['z_bunch','t_bunch','x_average','x_rms','x_prime_rms','emittance_x_norm','x_x_prime']
    bunch_list_x = np.loadtxt(output_file_bunch_x)
    #print('Bunch_size is: ' + str('%.3f' % (bunch_size[-1]*1e3)) + 'um' + '\n'*5)
    try:
        run = subprocess.call('rm Dist'+'{:06d}'.format(run_number)+'.ini', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    	run = subprocess.call('rm 3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.0174.001', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/generator'+'{:06d}'.format(run_number)+'.in', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_SC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
        run = subprocess.call('rm Astra_files/3boosters'+'{:06d}'.format(run_number)+'_FBL_noSC.*', shell=True) #stdout=subprocess.PIPE)#, creationflags=CREATE_NO_WINDOW)
    except:
	print('I have not been able to delete run number ' + str('{:06d}'.format(run_number)))
    
    #print(Ekin_bunch[-1])
    print('Done '+str(run_number))
    #returns: longitudinal emittance, bunch length, energy, energy deviation, time of flight, transverse spot size, normalized transverse emittance, final charge
    return bunch_list_z[-1,5],bunch_list_z[-1,3],bunch_list_z[-1,2],bunch_list_z[-1,4],bunch_list_z[-1,1],bunch_list_x[-1,3],bunch_list_x[-1,5],Qbunch_final

#focus = 8.0
#phase_b1 = 30.0
#phase_b2 = -80.0
#phase_b3 = 120.0
#E_b1 = 7.5
#E_b2 = 10.0
#E_b3 = 3.7
#
#emittance,bunch_length,Ekin,delta_e = runAstraFunction_surrogated(focus,phase_b1,E_b1,phase_b2,E_b2,phase_b3,E_b3,1)
#
#print(emittance,bunch_length,Ekin,delta_e)


