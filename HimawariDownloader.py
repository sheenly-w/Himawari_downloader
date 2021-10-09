#!/usr/bin/env python
# coding: utf-8

from datetime import datetime, timedelta
import os
import subprocess
import numpy as np

# ipython运行multiprocessing出错，换成multiprocess
# from multiprocessing import Pool
from multiprocess import Pool
from osgeo import gdal
# from tqdm import tqdm


class HimawariDownloader:
    def __init__(self, user, pwd, level, product, version, local_root_dir):
        """Initialization

        Args:
            user ([str]): [email address of the registered account from JAXA]
            pwd ([str]): [password]
            level ([str]): [Himawari-8 data product level]
            product ([str]): [product short name]
            version ([str]): [product version]
            local_root_dir ([str]): [local path]
        """        
        self.user = user
        self.pwd = pwd
        self.level = level
        self.product = product
        self.remote_root_dir = f"pub/himawari/{level}/{product}/{version}/"
        self.local_root_dir = local_root_dir
        if not self.local_root_dir.endswith('/'):
            self.local_root_dir += '/'
        
        # self.proxy = '--socks5 172.16.9.247:10808'
        self.proxy = '--socks5 127.0.0.1:10808'      # set to '' if not necessary
        # self.proxy = '--proxy socks5://127.0.0.1:1080'
        
    def get_hour_list(self, time):
        """get file list in a hour of L2 product

        Args:
            time ([datetime.datetime]): [specify to hour]

        Returns:
            [tuple]: (remote dir, file list)
        """        
        hour_dir = self.remote_root_dir + time.strftime('%Y%m/%d/%H/')
        cmd = f"curl {self.proxy} -l -u {self.user}:{self.pwd} ftp://ftp.ptree.jaxa.jp/{hour_dir}"
        ret = subprocess.run(cmd, capture_output=True)
        remote_names = ret.stdout.decode().split("\r\n")[:-1]     # filename
        
        if self.product == 'PAR':
            # 短波辐射产品既有全球5km的，也有日本1km的，选择全球5km的文件名
            remote_names_5km = []
            for f in remote_names:
                if f[-14:] == "02401_02401.nc":
                    remote_names_5km.append(f)
            remote_names = remote_names_5km
        
        return hour_dir, remote_names
        

        
    def download_single_file(self, remote_name, local_name):
        """download a file

        Args:
            remote_name ([str]): [path of the remote file name]
            local_name ([str]): [path of the local file name]
        """        
        import subprocess
        import os
        from osgeo import gdal
        downloaded = False
        while not downloaded:
            if os.path.isfile(local_name) and (gdal.Open(local_name) is not None):
                print(f'{local_name} exists, skip it')
                downloaded = True
                break
            else:
                cmd = f"curl {self.proxy} -u {self.user}:{self.pwd} -o {local_name} ftp://ftp.ptree.jaxa.jp/{remote_name}"
                subprocess.run(cmd)

        
    def download_filelist_parallel(self, remote_dir, local_dir, remote_names, processes=6):
        """download a file list using multiprocess

        Args:
            remote_dir ([str]): [remote dir]
            local_dir ([str]): [local dir]
            remote_names ([list]): [list of remote file names]
            processes (int, optional): [num of processes to use]. Defaults to 6.
        """        
        if not os.path.isdir(local_dir):
            os.makedirs(local_dir)
            
        arg_list = [(remote_dir+f, local_dir+f) for f in remote_names]
        
        with Pool(processes) as p:
            p.starmap(self.download_single_file, arg_list)

        
    def download_period(self, start_time, end_time):
        """download files in a period

        Args:
            start_time ([datetime.datetime]): [specify to hour]
            end_time ([datetime.datetime]): [specify to hour]
        """        
        length = int((end_time - start_time)/timedelta(hours=1))
        timeseq = [start_time + timedelta(hours=t) for t in range(length)]
        for time in timeseq:
            remote_dir, remote_names = self.get_hour_list(time)
            local_dir = self.local_root_dir + remote_dir
            print(time)
            print(f"remote dir: {remote_dir}")
            print(f"local dir: {local_dir}") 
            print("remote names:\n", '\n'.join(remote_names))
            
            try:
                self.download_filelist_parallel(remote_dir, local_dir, remote_names)
                print('download finished!')        
            except Exception as e:
                print(e)
