# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 09:08:19 2019

@author: leosel
"""
import glob
import shutil
import os

bisect_filefolder = 'D:\\Neuer Ordner\\T12\\frag\\txt_output\\*.txt'
maxfat_filefolder = 'D:\\Neuer Ordner\\T12\\skel\\txt_output\\*.txt'
new_folder = bisect_filefolder.replace('frag\\txt_output\\*.txt', 'combi_txt_output\\')
if not os.path.exists(new_folder):
    os.makedirs(new_folder)


def get_files(folder):
    files = glob.glob(folder)
    files_ind = []
    for f in files:
        files_ind.append((f, int(f.split("\\")[-1].split(".")[0])))
    files_ind = sorted(files_ind, key=lambda x: x[1])
    files = [x[0] for x in files_ind]
    return files_ind

bisect_files = get_files(bisect_filefolder)
maxfat_files = get_files(maxfat_filefolder)


def combine_decompositions(bisect_files, maxfat_files):
    bisect_ind = [x[1] for x in bisect_files]
    maxfat_ind = [x[1] for x in maxfat_files]

    max_ind = max(bisect_ind+maxfat_ind)
    combi_decomp = []
    for i in range(max_ind+1):
        if i in maxfat_ind:
            file = [x[0] for x in maxfat_files if x[1] == i][0]
            combi_decomp.append(file)
            shutil.copy2(file, new_folder)
        elif i in bisect_ind:
            file = [x[0] for x in bisect_files if x[1] == i][0]
            combi_decomp.append(file)
            shutil.copy2(file, new_folder)
        else:
            print('no decomposition for object ', i)
    print(combi_decomp)



combine_decompositions(bisect_files, maxfat_files)
