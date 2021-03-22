# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 09:08:19 2019

@author: leosel
"""
import glob
import h5py
import os

def read_bisect(filepath):
    f = h5py.File(filepath)

    temp_contour = list(f['original'])
    temp_zip = zip(temp_contour[1], temp_contour[0])
    contour = list(temp_zip)
    partition = list()

    for i in range(f['partitions'].maxshape[1]):
        h5part = f[f['partitions'][0][i]]
        temp_tuple = tuple(map(tuple, h5part))
        temp_zip = zip(temp_tuple[1], temp_tuple[0])
        partition.append(list(temp_zip))

    temp_index = filepath.split("_")[1].split(".")[0]
    index = int(temp_index)-1
    print(len(partition))
    return contour, partition, index

def get_files_from_folder(folderpath):
    files = glob.glob(folderpath)
    files_ind = []
    for f in files:
        files_ind.append((f, int(f.split("_")[1].split(".")[0])))
    files_ind = sorted(files_ind, key=lambda x: x[1])
    files = [x[0] for x in files_ind]
    return files

def decomposition_to_txt(folderpath):
    new_directory = folderpath.replace('*.mat', 'txt_output')
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)

    files = get_files_from_folder(folderpath)

    for f in files:
        contour, partition, index = read_bisect(f)
        with open(new_directory + '\\' + str(index) + '.txt', "w") as filehandle:
            for subpolgon in partition:
                filehandle.write('%s\n' % list(subpolgon))

if __name__ == '__main__':

    bisect_filefolder = 'D:\\Neuer Ordner\\T12\\frag\\*.mat'

    decomposition_to_txt(bisect_filefolder)

