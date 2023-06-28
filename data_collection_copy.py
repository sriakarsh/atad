import re
import numpy as np
import matplotlib.pyplot as plt
import csv


csv_path = "" #csv path to note the data 
with open(csv_path, 'w', newline='') as csvfile:
    fieldnames = ['Ftype', 'C1', 'C2', 'C3']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    SIRgrid_values = [0.2,0.5,2]  
    FT_values = ["AG","BCG","ABCG","AB"]  
    FL_values = [1,5,15,20,24,36,50,64,76,80,85,95,99]  
    Rf_values = [0.01,10,20,30,50]  
    FIA_values = [0,90,135]  
    
    for SIRgrid in SIRgrid_values:
        for FT in FT_values:
            for FL in FL_values:
                for Rf in Rf_values:
                    for FIA in FIA_values:
                        Path = '' #varying path for different SIR,FT,FL,Rf,FIA values
                        
                        CfgFileName = 'Local.cfg'
                        PathAndCfgName = Path + '\\' + CfgFileName
                        DatFileName = re.sub(r'\.cfg$', '.dat', CfgFileName)
                        PathAndDatName = Path + '\\' + DatFileName


                        cfg_id = open(PathAndCfgName, 'r')
                        dat_id = open(PathAndDatName, 'r')
                        cfg = cfg_id.readlines()
                        dat = dat_id.readlines()
                        cfg_id.close()
                        dat_id.close()

                        cfg_len = len(cfg)
                        cfg_string = []
                        for i in range(cfg_len):
                            temp_string = cfg[i].strip()
                            cfg_string.append(re.split(r',', temp_string))

                        Title = cfg_string[0][0]
                        if len(cfg_string[0]) < 3:
                            Version = '1999'
                        else:
                            Version = cfg_string[0][2]

                        No_Ch = int(cfg_string[1][0])
                        Ana_Ch = int(re.sub(r'\D', '', cfg_string[1][1]))
                        Dig_Ch = int(re.sub(r'\D', '', cfg_string[1][2]))

                        dat_len = int(re.sub(r'\D', '', cfg_string[No_Ch + 4][1]))
                        frequency = float(cfg_string[No_Ch + 1][0])
                        samp_rate = float(cfg_string[No_Ch + 4][0])
                        start_date = cfg_string[No_Ch + 5][0]
                        start_time = cfg_string[No_Ch + 5][1]
                        end_date = cfg_string[No_Ch + 6][0]
                        end_time = cfg_string[No_Ch + 6][1]

                        dat_string = []
                        data = np.zeros((dat_len, No_Ch + 2))
                        for i in range(dat_len):
                          temp_string = dat[i].strip()
                          dat_string.append(re.split(r',', temp_string))
                          data[i, :] = [float(val) for val in dat_string[i]]

                        t = data[:, 1] * 1e-6

                        n = int(samp_rate / frequency) 
                        var_string = []
                        for i in range(No_Ch):
                            j = i + 2
                            temp_string = cfg_string[j][1]
                            if not temp_string[0].isalpha():
                                temp_string = 'x' + temp_string[1:]
                            temp_string = re.sub(r'\W+', '_', temp_string)
                            var_string.append(temp_string)

                        Title = str(Title)
                        Version = str(Version)
                        Total_Channels = No_Ch
                        Analogue_Channels = Ana_Ch
                        Digital_Channels = Dig_Ch
                        Frequency = frequency
                        Sample_rate = samp_rate
                        Start_date = start_date
                        Start_time = start_time
                        End_date = end_date
                        End_time = end_time

                        if Ana_Ch >= 1:
                            dat = np.zeros((dat_len, Ana_Ch + 2))
                            for i in range(Ana_Ch):
                                j = i + 2
                                min_level = float(cfg_string[j][8])
                                max_level = float(cfg_string[j][9])
                                multiplier = float(cfg_string[j][5])
                                offset = float(cfg_string[j][6])

                                data[:, j] = np.where(data[:, j] <= min_level, min_level, data[:, j])
                                data[:, j] = np.where(data[:, j] >= max_level, max_level, data[:, j])
                                dat[:, i] = data[:, j] * multiplier + offset

                                if len(cfg_string[j]) > 10:
                                    pri_scaling = float(cfg_string[j][10])
                                    sec_scaling = float(cfg_string[j][11])
                                    pri_sec = cfg_string[j][12]

                                    if pri_sec == 'P':
                                        dat[:, i] = dat[:, i]
                                    else:
                                        dat[:, i] = dat[:, i] * (pri_scaling / sec_scaling)

                                exec(var_string[i] + ' = dat[:, i]')

                        V = dat[:, :3] / 1000
                        I = dat[:, 3:6] / 1000

                        dI = []
                        dIa = []
                        dIb = []
                        dIc = []

                        t_interval = []
                        Ns = 20

                        for i in range(1):
                            for k in range(2 * Ns, len(I)):
                                dIi = (I[k] - I[k - Ns]) - (I[k - Ns] - I[k - 2 * Ns])
                                dI1 = (I[k, i] - I[k - Ns, i]) - (I[k - Ns, i] - I[k - 2 * Ns, i])
                                dI2 = (I[k, i + 1] - I[k - Ns, i + 1]) - (I[k - Ns, i + 1] - I[k - 2 * Ns, i + 1])
                                dI3 = (I[k, i + 2] - I[k - Ns, i + 2]) - (I[k - Ns, i + 2] - I[k - 2 * Ns, i + 2])
                                t_interval_ind = t[k]

                                dI.append(dIi)
                                dIa.append(dI1)
                                dIb.append(dI2)
                                dIc.append(dI3)
                                t_interval.append(t_interval_ind)

                        cI1 = abs(dIa[70] - dIa[60])
                        cI2 = abs(dIb[70] - dIb[60])
                        cI3 = abs(dIc[70] - dIc[60])
                        cI = cI1 + cI2 + cI3

                        cI1 = cI1 / cI
                        cI2 = cI2 / cI
                        cI3 = cI3 / cI

                        Ftype = FT
                        C1 = cI1
                        C2 = cI2
                        C3 = cI3
                        
                        data = [{'Ftype': Ftype, 'C1': C1, 'C2': C2, 'C3': C3}]
                        writer.writerow({'Ftype': Ftype, 'C1': C1, 'C2': C2, 'C3': C3})
                        


                      