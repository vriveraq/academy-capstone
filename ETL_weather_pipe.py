from pathlib import Path
from pyspark import SparkConf
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import isnan, when, count, col
from pyspark.sql.types import TimestampType
import botocore 
import botocore.session 
import json
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig 

# Get credentials from AWS Secrets Manager
def get_credentials():
    client = botocore.session.get_session().create_client('secretsmanager')
    cache_config = SecretCacheConfig()
    cache = SecretCache( config = cache_config, client = client)

    secret_dict = json.loads(cache.get_secret_string('snowflake/capstone/login'))
    return secret_dict

def flatten_df(nested_df):

    flat_cols = [c[0] for c in nested_df.dtypes if c[1][:6] != 'struct']
    nested_cols = [c[0] for c in nested_df.dtypes if c[1][:6] == 'struct']

    flat_df = nested_df.select(flat_cols +
                               [col(nc+'.'+c).alias(nc+'_'+c)
                                for nc in nested_cols
                                for c in nested_df.select(nc+'.*').columns])
    return flat_df

s3_path = "s3a://dataminded-academy-capstone-resources/raw/open_aq/"
config = {"spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.1.2,net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1,net.snowflake:snowflake-jdbc:3.13.3", 
        "fs.s3a.aws.credentials.provider": "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
        }

conf = SparkConf().setAll(config.items())
spark = SparkSession.builder.config(conf = conf).getOrCreate()
df = spark.read.json(s3_path)
flat_df = flatten_df(df)
flat_df = flat_df.withColumn("date_local" , col("date_local").cast(TimestampType()))\
       .withColumn("date_utc" , col("date_utc").cast(TimestampType()))

## Get secrete log-in information
secrets_dict = get_credentials()

## Load to Snowflake
sfOptions = { 
"sfURL": secrets_dict["URL"], 
"sfUser" : secrets_dict["USER_NAME"], 
"sfPassword" : secrets_dict["PASSWORD"], 
"sfDatabase" : secrets_dict["DATABASE"], 
"sfSchema" : "VANESSA", 
"sfWarehouse" : secrets_dict["WAREHOUSE"], 
"sfRole" :secrets_dict["ROLE"], 
}

## Credentials to connect to Snowflake
sfOptions = { 
"sfURL": secrets_dict["URL"], 
"sfUser" : secrets_dict["USER_NAME"], 
"sfPassword" : secrets_dict["PASSWORD"], 
"sfDatabase" : secrets_dict["DATABASE"], 
"sfSchema" : "VANESSA", 
"sfWarehouse" : secrets_dict["WAREHOUSE"], 
"sfRole" :secrets_dict["ROLE"], 
}

# Load data to Snowflake
flat_df.write.format("net.snowflake.spark.snowflake").options(**sfOptions).option("dbtable", "clean_data").mode("overwrite").save()