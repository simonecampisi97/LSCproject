from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.functions import col
from pyspark.sql.window import Window
from pyspark.sql.functions import format_number 
from DataManipulation.DemographicInfo import DemographicInfo
from DataManipulation.PatientDiagnosis import PatientDiagnosis
from DataManipulation.Utils.Path import Path
from pyspark.sql import functions as F
import sys,os
from importlib import reload
from Utils.BMI import replace_bmi_child

spark_session = SparkSession.builder \
                .master('local') \
                .appName('LSC_PROJECT') \
                .getOrCreate()

# ----the dataframe containing the informations about patients is created
demographic_info = DemographicInfo(spark_session)

# ----the diagnosis dataframe is created
patient_diagnosis = PatientDiagnosis(spark_session)

# ----visualize first 20 rows and the schema 
#df_patient_diagnosis=patient_diagnosis.get_DataFrame()
#df_patient_diagnosis.show()
#df_patient_diagnosis.printSchema()

# ----visualize first 20 rows and the schema
#df_demographic_info = demographic_info.get_DataFrame()
#df_demographic_info.show() 
#df_demographic_info.printSchema()

# get rid of the Child's informations => now BMI column contains the BMI for both Adult and Children
rdd_demographic_info=demographic_info.get_Rdd()
rdd_demographic_info_shrank= rdd_demographic_info.map(lambda p: replace_bmi_child(p)).toDF(demographic_info.shrank_schema) # new schema DemographicInfo



