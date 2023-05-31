import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#import csv list pipe line number
with open('linelist pipa.csv', 'r') as read_obj:
    csv_reader = csv.reader(read_obj)
    linelist = list(csv_reader)

#import database diameter pipa standar ASME
with open('database_sch.csv', 'r') as read_obj:
    csv_reader = csv.reader(read_obj)
    sch_database = list(csv_reader)

#mencari nilai outside diameter untuk setiap pipe line number dalam list
for x in range(len(linelist)):
    for i in range(len(sch_database)):
        if linelist[x][3] == sch_database[i][0]:
            linelist[x].append(sch_database[i][1])
linelist[0].append('OD')

print(sch_database)
print(linelist)

#membuat list untuk range tebal insulasi yang tersedia
insulation_thicknesses = np.arange(0,6,0.5)
print(insulation_thicknesses)

#menambah header kolom baru untuk list line number untuk parameter suhu permukaan, heat loss, dan tebal insulasi yang dipiih
linelist[0].append('surface')
linelist[0].append('heat loss')
linelist[0].append('thk selected')

#loop untuk pengulangan pada setiap line number
for i in range(1,len(linelist)):
    q = 1000
    T_surface = 1000
    j = 0

    #loop untuk pengulangan pemilihan tebal insulasi
    while q > 250 or T_surface > 60:
        r2 = (float(linelist[i][5])/2)/1000
        T_fluid = float(linelist[i][2])
        T_ambient = 30.2
        T_surface = T_fluid #tebakan awal untuk suhu permukaan

        #loop ntuk pengulangan iterasi perhitungan hambatan termal
        while True:
            # conduction
            r3 = r2 + insulation_thicknesses[j] * 0.0254
            k_conduction = 0.079
            R_conduction = np.log(r3 / r2) / (2 * np.pi * k_conduction)

            # convection
            v_air = 1.4
            viscousity_air = 0.0000258
            Re_convection = v_air * 2 * r3 / viscousity_air
            Pr_convection = 0.685
            Nu_convection = 0.3 + ((0.62 * Re_convection ** (1 / 2) * Pr_convection ** (1 / 3) / (1 + (0.4 / Pr_convection) ** (2 / 3)) ** (1 / 4)) * (1 + (Re_convection / 282000) ** (5 / 8)) ** (4 / 5))
            R_convection = 1 / (Nu_convection * k_conduction / (2 * r3) * 2 * np.pi * r3)

            # radiation
            emissivity = 0.9
            Stefan_boltzman = 0.0000000567
            R_radiation = 1 / (emissivity * Stefan_boltzman * ((T_surface + 273) ** 2 + ((T_ambient + 273) ** 2)) * ((T_surface + 273) + (T_ambient + 273)) * 2 * np.pi * r3)

            # total hambatan termal
            R_total = R_conduction + (R_convection * R_radiation / (R_convection + R_radiation))

            # heat loss rate
            q = (T_fluid - T_ambient) / (R_total)

            # surface temperature baru
            T_surface_new = T_ambient + q * 2 * np.pi * r3 / ((Nu_convection * k_conduction / (2 * r3)) + (emissivity * Stefan_boltzman * ((T_surface + 273) ** 2 + (T_ambient + 273) ** 2) * (T_surface + 273 + T_ambient + 273)))

            # cek percent error relative dan koreksi tebakan surface temperature
            if abs(T_surface_new - T_surface) / abs(T_surface) > 0.001:
                T_surface = T_surface + (T_surface_new - T_surface) / 2

            else:
                T_surface = T_surface_new
                break
        j=j+1

    #memasukkan hasil perhitungan ke dalam list
    linelist[i].append(T_surface)
    linelist[i].append(q)
    linelist[i].append(j * 0.5)
print(linelist)

#ekspor list ke file format csv
df = pd.DataFrame(linelist)
new_header = df.iloc[0]
df = df[1:]
df.columns = new_header
df.to_csv('Hasil Kalkulasi Insulasi.csv')
