from pathlib import Path
from pyspark import SparkConf
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import isnan, when, count, col

# Save data from S3 bucket 
s3_path = "s3a://dataminded-academy-capstone-resources/raw/open_aq/"
config = {"spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.1.2", "fs.s3a.aws.credentials.provider": "com.amazonaws.auth.DefaultAWSCredentialsProviderChain"}
conf = SparkConf().setAll(config.items())
spark = SparkSession.builder.config(conf = conf).getOrCreate()
df = spark.read.json(s3_path)

def flatten_df(nested_df):
    flat_cols = [c[0] for c in nested_df.dtypes if c[1][:6] != 'struct']
    nested_cols = [c[0] for c in nested_df.dtypes if c[1][:6] == 'struct']

    flat_df = nested_df.select(flat_cols +
                               [col(nc+'.'+c).alias(nc+'_'+c)
                                for nc in nested_cols
                                for c in nested_df.select(nc+'.*').columns])
    return flat_df

flat_df = flatten_df(df)
flat_df = flat_df.withColumn("date_local" , col("date_local").cast(TimestampType()))\
       .withColumn("date_utc" , col("date_utc").cast(TimestampType()))