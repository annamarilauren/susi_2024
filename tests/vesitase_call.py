# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 15:18:47 2022

@author: alauren
"""

from dwts_para import para
import numpy as np
import datetime
from susi.susi_utils import read_FMI_weather

from inputs.susi_para import get_susi_para
from susi.susi_main import Susi
import susi.susi_io



#***************** local call for SUSI*****************************************************
folderName=r'C:/Users/laurenan/OneDrive - University of Helsinki/SUSI/vesitase/vesitase_out/'

#r'C:/Users/laurenan/OneDrive - University of Helsinki/SUSI/vesitase/vesitase_out/'

wpath = r'C:/Users/laurenan/OneDrive - University of Helsinki/SUSI/vesitase/vesitase_wfiles/'
mottipath =  r'C:/Users/laurenan/OneDrive - University of Helsinki/SUSI/vesitase/motti_files/'

sites =['ansa21', 'ansa26', 'jaakkoin61', 'jaakkoin62', 'koira11', 'koira12',
    'neva11', 'neva14', 'neva31', 'neva34','parkano11']
 
params = para(period='start-end')



for s in sites:
    if not params[s]['thinning']: 
        print (s)
        #print (params[s])
        #import sys; sys.exit()
        
        mottifile = {'path':mottipath,
              'dominant':{1: params[s]['mottifile']},
              'subdominant':{0:'susi_motti_input_lyr_1.xlsx'},
              'under':{0:'susi_motti_input_lyr_2.xlsx'}} 

        start_date = params[s]['start_date']
        end_date=params[s]['end_date']
        start_yr = start_date.year; end_yr = end_date.year
        yrs = (end_date - start_date).days/365.25
        length = (end_date - start_date).days +1
        wdata  =  params[s]['wfile']
        
        sarkaSim = params[s]['Swidth'] #+ 4.0
        n = int(sarkaSim / 2)
        sfc =  np.ones(n, dtype = int)*params[s]['sfc']                                                                         #soil fertility class
        
        ageSim = {'dominant': params[s]['Aini']*np.ones(n),
                  'subdominant': 0*np.ones(n),
                  'under': 0*np.ones(n)}                                                         # age of the stand in each node
            

        ddwest = params[s]['ddepth']
        ddeast = params[s]['ddepth'] 
        
        site = 'wbal_scens'
        
        forc=read_FMI_weather(0, start_date, end_date, sourcefile=wpath+wdata)           # read weather input
        
        peatN = None #idata.T[nro]['n_mg/g']/10.  
        peatP = None #idata.T[nro]['p_mg/g']/10.
        peatK = None #idata.T[nro]['k_mg/g']/10.
        
        wpara, cpara, org_para, spara, outpara, photopara = get_susi_para(wlocation='undefined', peat=site, 
                                                                                  folderName=folderName, hdomSim=None,  
                                                                                  ageSim=ageSim, sarkaSim=sarkaSim, sfc=sfc, 
                                                                                  n=n)
        spara['sarkaSim'] = sarkaSim
        spara['n'] = n
        spara['ditch depth west'][0] = params[s]['ddepth']
        spara['ditch depth east'][0] = params[s]['ddepth']
        spara['ditch depth 20y west'][0] = params[s]['ddepth']
        spara['ditch depth 20y east'][0] = params[s]['ddepth']
        
        outpara['netcdf'] = s + '.nc'
        
        spara['vonP'] = True
        spara['vonP bottom'] = 9
        spara['scenario name']=[s]
        spara['vonP top'] = params[s]['vonP']
        
        spara['peat type'] = params[s]['ptype']
        bd = params[s]['bulk dens']/1000. #0.14 #idata.T[nro]['bd']
        spara['bd top']=[bd, bd, bd, bd, bd, bd, bd, bd]
        #spara['peat type'] = ['S','S','S','S','S','S','S','S']
        #spara['peat type bottom']=['S']

        #spara['peat type'] = ['A','A','A','A','A','A','A','A']
        #spara['peat type bottom']=['A']

        spara['depoN'] = params[s]['depoN']       #
        spara['depoP'] = params[s]['depoP']      #+dry deposition Ruoho-Airola et al 2015
        spara['depoK'] = params[s]['depoK'] * 1.1   #1.1 +dry deposition  Ruoho-Airola et al 2003 

        mass_mor = 1.616*np.log(params[s]['drain_age'])-1.409     #Pitkänen et al. 2012 Forest Ecology and Management 284 (2012) 100–106
        spara['anisotropy'] = 10
        if params[s]['sfc'] < 3:
            spara['rho_mor'] = 110.0
        elif params[s]['sfc'] == 3:
            spara['rho_mor'] = 100.0
        elif params[s]['sfc'] == 4:
            spara['rho_mor'] = 85.0            
        elif params[s]['sfc'] == 5:
            spara['rho_mor'] = 80.0
        else:           
            spara['rho_mor'] = 60.0

        #spara['rho_mor'] = 90
        spara['h_mor'] = mass_mor/ spara['rho_mor']          
        print (s, mass_mor)
        
        susi_c = Susi()
        susi_c.run_susi(forc, wpara, cpara, org_para, spara, outpara, photopara, start_yr, end_yr, wlocation = 'undefined', 
                                mottifile=mottifile, peat= 'other', photosite='All data', 
                                folderName=folderName,ageSim=ageSim, sarkaSim=sarkaSim, sfc=sfc)
    
                                                  
            
#%%
# from figures import *
# ff = folderName + sites[3] + '.nc'
# scen = 0
# hydrology(ff, scen)
# stand(ff, scen)
# mass(ff, scen)
# carbon(ff, scen)        
