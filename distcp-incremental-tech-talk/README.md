

##  1. DistcCp Incremental POC using a Cloud Function

The architecture prepared for this POC simulates an OnPrem Cluster using Cloud Dataproc. The simulated On-premise cluster runs a shell script to validate FILE CHANGES on the HDFS directories. Once changes are detected, it will write the directory and the cloud storage bucket destination in a key-value file. The shell script is scheduled to be executed using cron every 5 minutes.  Then, the Key-Value file will be copied to a Google Cloud Storage bucket. This process is done using gsutil cp tool.

A DAG in Cloud Composer is going to be triggered by a Cloud Function when a new file is uploaded into the bucket. 

The next task will submit a job or jobs depending on the number of lines in the file that was found in the bucket. These jobs are running in a dataproc cluster pool that consists of two clusters using the “PULL” model.  The job or jobs are going to execute DISTCP commands to get the data from the on premise cluster with the PULL model implementation, having Google Cloud Storage as the sink.



In cloud shell execute the following commands, replace projectId with the desired project id:

```
gcloud config set project projectId
export PROJECT_ID=$(gcloud info --format='value(config.project)')
export COMPOSER_ENVIRONMENT=distcp-orch

export AUDIT_BUCKET=audit-files-distcp
export DISTCP_BUCKET=dest-distcp-data
export SOURCE_FILES_DATA_BUCKET=source-files-data-distcp

export ONPREM_CLUSTER=cluster-src
export REGION=us-central1
export ZONE=us-central1-a
```
# Cloud Composer Creation

1. Set ServiceAgentV2Ext role to the service account that you will use with the composer version 2 environment

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:service-$PROJECT_NUMBER@cloudcomposer-accounts.iam.gserviceaccount.com \
    --role roles/composer.ServiceAgentV2Ext
```
How to get the project number in a variable 
service-537054103430@cloudcomposer-accounts.iam.gserviceaccount.com

2. Create a cloud composer environment 

```
gcloud composer environments create $COMPOSER_ENVIRONMENT \
    --location $REGION \
    --image-version composer-2.0.15-airflow-2.2.5
```


# Buckets creation 

gsutil mb (make buckets) -b (Uniform bucket level access) 

```
gsutil mb -b on gs://$AUDIT_BUCKET
gsutil mb -b on gs://$DISTCP_BUCKET
gsutil mb -b on gs://$SOURCE_FILES_DATA_BUCKET
```

# Modify audit_hdfs_script.sh and initialize_onprem_cluster.sh files 

In this step, the **audit_hdfs_script.sh** and **initialize_onprem_cluster.sh** is going to be modified, in the second line of both files, modify ``USER_NAME_GOOGLE``  variable with the user name that appears in the left side on the cloud shell without @cloudshell , example:

![](images/image3.png)
*Picture 3: user name example*

To modify the **audit_hdfs_script.sh** file use the following command: 

```
vim audit_hdfs_script.sh
```

Type **i** to edit the file, copy the name in the second line. Then press **ESC** and write **:wq** to write the changes and quit to the file. 

![](images/image4.png)
*Picture 4:  audit_hdfs_script.sh file*

To modify the **initialize_onprem_cluster.sh** file use the following command: 

```
vim initialize_onprem_cluster.sh
```

Type **i** to edit the file, copy the name in the second line. Then press **ESC** and write **:wq** to write and quit to the file. 


Copy folder that contains the file that we are going to transfer using distcp jobs in the next steps and the files that were modified to the source bucket using the following commands:

```
gsutil cp initialize_onprem_cluster.sh gs://$SOURCE_FILES_DATA_BUCKET
gsutil cp audit_hdfs_script.sh gs://$SOURCE_FILES_DATA_BUCKET
gsutil cp -r input_data/ gs://$SOURCE_FILES_DATA_BUCKET
```

# Dataproc clusters creation 

## Simulated on prem cluster
```
gcloud dataproc clusters create cluster-src --region $REGION --zone $ZONE --single-node --master-machine-type n1-standard-2 --master-boot-disk-size 200 --image-version 2.0-debian10 --project $PROJECT_ID --initialization-actions=gs://$SOURCE_FILES_DATA_BUCKET/initialize_onprem_cluster.sh
```

## Cluster pools

Needed to execute the distcp jobs using the PULL model 
```
gcloud dataproc clusters create cluster-pull-1 --region $REGION --zone $ZONE --single-node --master-machine-type n1-standard-2 --master-boot-disk-size 200 --image-version 2.0-debian10 --labels cluster-pool=pool-1 --project $PROJECT_ID
```

```
gcloud dataproc clusters create cluster-pull-2 --region $REGION --zone $ZONE --single-node --master-machine-type n1-standard-2 --master-boot-disk-size 200 --image-version 2.0-debian10 --labels cluster-pool=pool-1 --project $PROJECT_ID
```


# Upload the Airflow DAG 

Using the following command the python file that contains the Airflow DAG called **** will be uploaded into the DAGs folder created inside the bucket created by the composer environment

```
gcloud composer environments storage dags import --environment $COMPOSER_ENVIRONMENT --location $REGION --source airflow_parallel_distcp_dag.py.py
```


# Cloud Function 

Obtain the composer URL with the following command 

```
gcloud composer environments describe $COMPOSER_ENVIRONMENT \
    --location=$REGION \
    --format="value(config.airflowUri)"
```


gcloud composer environments describe $COMPOSER_ENVIRONMENT \
    --location $REGION \
    --format='value(config.airflowUri)'

Copy the URL in the 46 line of the main.py file found in the cloud_function_composer2 folder
```
vim cloud_function_composer2/main.py
```

Type **i** to edit the file, copy the name in the second line. Then press **ESC** and write **:wq** to write and quit to the file. 


### Create a zip file 

Change to the cloud_function_composer2 directory

```
cd cloud_function_composer2/
```
Create a zip file that contains all the files needed to deploy the Cloud Function that will trigger the Airflow DAG in charge of executing the distcp jobs to copy the data from the simulated on prem cluster to a specific GCS bucket, a DAG instance will be created every time that that a new file is uploaded into the audit file bucket.

```
zip -r main.zip composer2_airflow_rest_api.py main.py requirements.txt
```
### Copy zip file to bucket
```
gsutil cp ./main.zip gs://$SOURCE_FILES_DATA_BUCKET/main.zip
```
### Deploy cloud function
```
gcloud functions deploy trigger_dag_function --entry-point trigger_dag_gcf --runtime python39 --trigger-resource gs://$AUDIT_BUCKET --trigger-event google.storage.object.finalize --source gs://$SOURCE_FILES_DATA_BUCKET/main.zip
```


