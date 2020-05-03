from os import listdir
import os
import io
from os.path import *
from DataManipulation.Utils.Path import Path
from pyspark.sql.types import (StructField,StringType,IntegerType,StructType,FloatType)
from pyspark.sql import SparkSession
from pyspark.sql.functions import split, substring, col, regexp_replace, reverse
from pyspark.sql.functions import lit
from pyspark.sql.functions import *
from time import time
import pandas as pd

import subprocess


class WAV(object):
    
    PATH_FILES_WAV = Path.get_wav_file_path()
    
    def __init__(self,spark_session):
        self.spark_session = spark_session

    def recording_info(self):
        wav_files = self.get_fileNames_test()

        wav_DF = self.spark_session.createDataFrame(wav_files, StructType([StructField("FileName", StringType(), False)]))

        split_col = split(wav_DF['FileName'], '_')
        wav_DF = wav_DF.withColumn("Patient_ID", split_col.getItem(0))
        wav_DF = wav_DF.withColumn("Recording_idx", split_col.getItem(1))
        wav_DF = wav_DF.withColumn("Chest_Location", split_col.getItem(2))
        wav_DF = wav_DF.withColumn("Acquisition_Mode", split_col.getItem(3))
        wav_DF = wav_DF.withColumn("Recording_Equipement", split_col.getItem(4))

        wav_DF.printSchema()
        wav_DF.show(5)

    def recording_annotation(self):
        idx_fileName = len(WAV.PATH_FILES_WAV.split(Path.path_separator))


        original_schema = [ StructField("Start", FloatType(), True),
                            StructField("End",  FloatType(), True),
                            StructField("Crackels", IntegerType(), True),
                            StructField("Wheezes", IntegerType(), True)]

        data_structure = StructType(original_schema)

        df = self.spark_session.read.\
            csv(path=WAV.PATH_FILES_WAV+'*.txt', header=False, schema= data_structure, sep='\t').\
            withColumn("Filename", split(input_file_name(), "/").getItem(idx_fileName) ).\
            withColumn("duration", col("End") - col("Start"))

        

        df.show(5, False)
        df.printSchema()


    
    def get_fileNames_test(self):
        path = Path.get_wav_file_path()
        list_of_fileName = []

        try:
            #IF THE FILE ALREDY EXIST
            indexingFiles = self.openIndexingFiles(folder_path=path)
            print(indexingFiles)
            for line in indexingFiles:
                list_of_fileName.append(line)
        except IOError:
            print("\nIndexing file for path \'{}\' not present, creating it...".format(path))
            list_of_fileName = self.createIndexingFile_andGetContent(folder_path=path)
        finally:
            print("ciao")
            #indexingFiles.close()
        return [list_of_fileName]
    

    def openIndexingFiles(self, folder_path):
        if Path.RunningOnLocal:
            #WINDOWS LOCAL MACHINE
            f = open(folder_path+'index_fileName.txt', 'r')
            return f
        else:
            #UNIGE CLUSTER SERVER
            args = "hdfs dfs -cat "+folder_path+"index_fileName.txt"
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                raise IOError('Indexing file not found.')
            return stdout.split()
    

    def createIndexingFile_andGetContent(self, folder_path):
        list_of_fileName = []
        if Path.RunningOnLocal:
            #WINDOWS LOCAL MACHINE
            list_of_fileName = [f[:-4] for f in listdir(folder_path) if (isfile(join(folder_path, f)) and f.endswith('.txt'))]

            indexingFiles = open(folder_path+'index_fileName.txt','w')
            for fileName in list_of_fileName:
                indexingFiles.write(fileName+"\n")
            indexingFiles.close()
        else:
            #UNIGE CLUSTER SERVER
            args = "hdfs dfs -ls "+folder_path+"*.txt | awk '{print $8}'"
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            s_output, s_err = proc.communicate()
            tmp_list = s_output.split()
            print(Path.path_separator)
            print(Path.RunningOnLocal)
            for line in tmp_list:
                fileName = line.split("/")[-1]
                list_of_fileName.append(fileName[:-4])

            #save file in hadoop file system
            tmpFile = open('tmp','w')
            for fileName in list_of_fileName:
                tmpFile.write(fileName+"\n")
            tmpFile.close()

            args = "hdfs dfs -put tmp "+folder_path+"index_fileName.txt"
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            #os.remove('tmp')

        return list_of_fileName

        

