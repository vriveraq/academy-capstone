# Data Minded Academy Capstone
Welcome to the Capstone project! During the next 1.5 days you will apply everything you've learned during the past days 
in an integrated exercise. You will:
1) Read, transform and load weather data from S3 to Snowflake through PySpark
2) Build dashboards with SQL on Snowflake
3) Take a stab at running your application on AWS through Docker, AWS Batch and Airflow

## Getting started
We set up a gitpod environment containing all the tools required to complete this exercise (awscli, python, vscode, ...).
You can access this environment by clicking the button below:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/datamindedbe/academy-capstone)

This is an ubuntu-based environment pre-installed with:
- VSCode
- A Python3 virtual environment, we recommend you always work inside this environment
- The AWS cli

Before you commence data crunching, set up your `.aws/credentials` file. This required to access AWS services through the API.
Run `aws configure` in the terminal and enter the correct information:
```shell
AWS Access Key ID [None]: [YOUR_ACCESS_KEY]
AWS Secret Access Key [None]: [YOUR_SECRET_KEY]
Default region name [None]: eu-west-1
Default output format [None]: json
```
IMPORTANT: Create a new branch and periodically push your work to the remote. After 30min of inactivity this
environment shuts down and you will lose unsaved progress.

## Task 1: Extract, transform and load weather data from S3 to Snowflake
Our team recently ingested Belgian weather data from the [openaq](https://openaq.org/) API and stored it on AWS S3
under `s3://dataminded-academy-capstone-resources/raw/open_aq/`.

You are tasked with building a PySpark application that reads this weather, transforms it and stores it in a Snowflake Table 
for further analysis. 
### Step 1: Extract and transform
Required transformations:
- Flatten all nested columns
- Some timestamp columns are stored as string, cast them to timestamp

You can access the weather data through your AWS credentials. While working locally, you'll need to
pass these to your spark application. In addition, your spark application requires 
the following JAR to interact with AWS S3 `org.apache.hadoop:hadoop-aws:3.1.2`.

### Step 2: Retrieve Snowflake credentials
After you successfully extracted and transformed the data, you can move on to loading said data to Snowflake.
To this end, you'll require Snowflake credentials stored on AWS Secretsmanager 
under the following secret `snowflake/capstone/login`.

Write Python code that retrieves this secret to leverage in the next step.

### Step 3: Load to Snowflake
The final step requires you to load the tranformed data to a Snowflake table utilizing the login details
obtained in the previous step. Your Spark application will also require additional JARs:
- `net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1`
- `net.snowflake:snowflake-jdbc:3.13.3`

Scan the Snowflake docs to figure out how to load data through Spark. All required configuration is stored in the AWS secret except the following:
- Snowflake Schema: On Snowflake, we created individual schema's for every participant. Write to your schema. The schema name is based on your username so login on Snowflake to retrieve it.
- Table name: Feel free to use any table name you want

When everything's tied together and functional, you can proceed to the next task.

## Task 2: Build dashboards through SQL queries on Snowsight
With the transformed weather data available on Snowflake, login on Snowflake and navigate to Snowsight.
The team wants you to perform a couple analysis through SQL and build an insightful graph for each of them:
1) Show the monthly maximum values of each air quality metric
2) [Optional] Compare the daily max of each metric to its 7-day historic maximum. You will require window functions

## Task 3: Run your PySpark application on the cloud
As a data engineer, you might run your application locally during develoment (as you have done during the first task)
but you should always run your applications on a stable, scalable environment with scheduling in place and
ideally deployed through CICD.

During the final step of this Capstone you will run your application on AWS Batch scheduled through Airflow (MWAA).
This requires you to execute the following steps:
1) Containerize your application through Docker
2) Create an ECR repository and push your image
3) Create a batch job definition which runs your application (and test it for good measure)
4) Set up an MWAA environment and create/push a DAG that trigger a batch job using your job definition
5) ??
6) Profit

IMPORTANT NOTES:
- While using the AWS console, make sure you are in the `eu-west-1` region
- Most resources you create will require a name that starts with your AWS username
- Where applicable, you will need to tag every resource you create with:
  
  `environment`: `academy-capstone-winter-2022`

### Step 1: Containerize
Create a `Dockerfile` that packages your application. You can start from one of our Data Minded images
which pre-installs Spark and it's dependencies: put `FROM public.ecr.aws/dataminded/spark-k8s-glue:v3.1.2-hadoop-3.3.1` at the top of your Dockerfile.

### Step 2: Push your image to an ECR repository
Through the AWS console, create a private ECR repository. It's name should start with your AWS username.
After creation, push your docker image to this repo.

### Step 3: Create a batch job definition
With your image pushed to the repository, navigate to AWS Batch and create a new Job Definition. Apply the following configuration:
- Name: Make sure it starts with your AWS username
- Platform type: EC2
- Execution role: `academy-capstone-winter-2022-batch-job-role`
- Job configuration:
    - Image: Image you pushed during the previous step
    - Command: Depends on your image:)
- Tags:
  - `environment`: `academy-capstone-winter-2022`
  
After creating the job definition you can run it by submitting a new job. Again, apply the correct naming convention and tags. 
You can submit the job to the following queue: `academy-capstone-winter-2022-job-queue`

### Step 4: Scheduling through MWAA
To conclude this capstone project, you will setup an Airflow environment and upload a DAG that triggers your AWS Batch job.

Navigate to MWAA in the AWS console and create a new environment. Apply the following configuration:
- Naming convetion and tags still apply
- S3 Bucket: `s3://dataminded-academy-capstone-resources`
- DAGs folder: s3://dataminded-academy-capstone-resources/{YOUR_AWS_USERNAME}/dags
- Switch `web server access` to `Public network` 
- UNcheck `create new security group` and select `academy-capstone-winter-2022-mwaa-sg` under the existing SG dropdown menu
- Check all logs and set log level to INFO
- Select `academy-capstone-winter-2022-mwaa-role` as the execution role

Following successfull creation you can access the Airflow Web UI through the link in the console.

Finally, create a DAG that triggers a batch job and upload it in the previously specified DAG folder on S3. It should pop up in the Airflow UI where you can trigger it manually.


If the Airflow triggered Batch job ran successfully: Congratulations! You've completed the Data Minded Academy Capstone!

## Bonus: Writing and scheduling an air quality data ingest job
In case you finished the capstone but want to expand your pipeline, feel free to create an ingest job which fetches air quality data and stores it in S3.
To this end, have a look at the [openaq project](https://openaq.org/#/). They expose a public API which can be called to retrieve air quality metrics filtered on a set of parameters. (Note: We used this API to gather the raw files you transformed and loaded into Snowflake)

Feel free to tackle this however you want and we are here to help!