FROM public.ecr.aws/dataminded/spark-k8s-glue:v3.1.2-hadoop-3.3.1
USER root
WORKDIR /repo
COPY . /repo
RUN  pip install --upgrade pip && pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["ETL_weather_pipe.py"]