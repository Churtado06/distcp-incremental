# DistcCp Incremental POC using a GCS sensor

**Table of contents**


[1. DistcCp Incremental POC using GCS sensor diagram](#DistcCpIncrementalPOCusingGCSsensordiagram)

[2. Copy the distcp_sensor_v1 folder to the cloud shell](#Copythedistcp_sensor_v1foldertothecloudshell)

[3. Set variables](#Setvariables)

[4. Composer version 2 environment](#Composerversion2environment)

* [4.1. Set ServiceAgentV2Ext role to the service account that you will use with the composer version 2 environment](#SetServiceAgentV2Extroletotheserviceaccountthatyouwillusewiththecomposerversion2environment)

* [4.2. Create the composer v2 environment named distcp-orch](#Createthecomposerv2environmentnameddistcp-orch)

[5. Create two dataproc clusters with labels](#Createtwodataprocclusterswithlabels)

[6. Initialization actions](#Initializationactions)
	
* [6.1  Create the buckets](#Createthebuckets)

* [6.2. Copy the input file to the $SOURCE_FILES_DATA_BUCKET bucket](#CopytheinputfiletotheSOURCE_FILES_DATA_BUCKETbucket)
* [6.3. Modify the  audit_hdfs_script.sh and initialize_onprem_cluster.sh files](#Modifytheaudit_hdfs_script.shandinitialize_onprem_cluster.shfiles)
* [6.4. Copy the  shell files to the $SOURCE_FILES_DATA_BUCKET bucket](#CopytheshellfilestotheSOURCE_FILES_DATA_BUCKETbucket)

[7. Create the on-premise simulated cluster](#Createtheon-premisesimulatedcluster)

[8. SSH into the on-premise simulated master cluster](#SSHintotheon-premisesimulatedmastercluster)

* [8.1. Add files to the two folders that are created in the on-premise simulated cluster](#Addfilestothetwofoldersthatarecreatedintheon-premisesimulatedcluster)

[9. Check the audit files in Google Cloud Storage](#ChecktheauditfilesinGoogleCloudStorage)
* [9.1. Create two new directories and add files to these directories](#Createtwonewdirectoriesandaddfilestothesedirectories)

[10. Copy the DistCp Airflow DAG to the composer environment](#CopytheDistCpAirflowDAGtothecomposerenvironment)

* [10.1. Open Airflow](#OpenAirflow)
* [10.2. Click on the DAG named **distcp_incremental_gcs_sensor**](#ClickontheDAGnameddistcp_incremental_gcs_sensor)



##  1. DistcCp Incremental POC using GCS sensor diagram <a name='DistcCpIncrementalPOCusingGCSsensordiagram'></a>

The architecture prepared for this POC simulates a Groupon OnPrem. The simulated On-premise cluster runs a shell script to validate FILE CHANGES on the HDFS directories. Once changes are detected, it will write the directory and the cloud storage bucket destination in a key-value file. The shell script is scheduled to be executed Using cron every 5 minutes.  Then, the Key-Value file will be copied to a Google Cloud Storage bucket. This process is done using gsutil cp tool.

A DAG in Cloud Composer is scheduled to be triggered every 5 minutes. This DAG is using a GCS sensor that checks the existence of objects with a specific prefix in a bucket, if the GCS sensor detects objects with that prefix, the next task will submit a job or jobs depending on the number of lines in the file that was found in the bucket. These jobs are running in a dataproc cluster pool that consists of two clusters using the “PULL” model.  The job or jobs are going to execute the DISTCP to get the data from the on premise cluster with the PULL model implementation, having Google Cloud Storage as the sink.

![](images/image1.png)
*Picture 1. DistcCp Incremental POC using GCS sensor diagram*

##  2. <a name='Copythedistcp_sensor_v1foldertothecloudshell'></a>2. Copy the distcp_sensor_v1 folder to the cloud shell 

Using the cloud shell, copy the folder distcp_sensor_v1 that contains all the files needed to execute the DistCp Incremental POC with the following command:

```
git clone command
```

Change to the directory where the files uploaded are located:

```
cd distcp_gcs_sensor_v1
```

```
ls distcp_gcs_sensor_v1
```

![](images/image2.png)
*Picture 2: distcp_sensor_v1 folder content seen in the cloud shell*


##  3. <a name='Setvariables'></a>3. Set variables

In cloud shell execute the following commands, replace projectId with the desired project id:

```
gcloud config set project projectId
export PROJECT_ID=$(gcloud info --format='value(config.project)')
export COMPOSER_ENVIRONMENT=distcp-orch

export AUDIT_BUCKET=audit-file-distcp-bucket1
export DISTCP_BUCKET=dest-distcp-bucket-demo
export SOURCE_FILES_DATA_BUCKET=source-files-data-onprem-groupon

export ONPREM_CLUSTER=cluster-src
export REGION=us-central1
export ZONE=us-central1-a
```

##  4. <a name='Composerversion2environment'></a>4. Composer version 2 environment 

###  4.1. <a name='SetServiceAgentV2Extroletotheserviceaccountthatyouwillusewiththecomposerversion2environment'></a>4.1. Set ServiceAgentV2Ext role to the service account that you will use with the composer version 2 environment

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:service-783621314563@cloudcomposer-accounts.iam.gserviceaccount.com \
    --role roles/composer.ServiceAgentV2Ext
```


###  4.2. <a name='Createthecomposerv2environmentnameddistcp-orch'></a>4.2. Create the composer v2 environment named distcp-orch

```
gcloud beta composer environments create $COMPOSER_ENVIRONMENT \
    --location $REGION \
    --airflow-configs=api-auth_backend=airflow.composer.api.backend.composer_auth \
    --image-version composer-2.0.0-preview.4-airflow-2.1.2
```
*Note: The creation process of composer v2 environment takes around 20 minutes*

##  5. <a name='Createtwodataprocclusterswithlabels'></a>5. Create two dataproc clusters with labels

Create two cluster-pool that are going to used in the Pull model to extract the data from the simulated On-premise cluster

```
gcloud dataproc clusters create cluster-pull-1 --region $REGION --zone $ZONE --no-address  --subnet=projects/prj-grp-sharedvpc-e2b0/regions/us-central1/subnetworks/sub-vpc-dev-sharedvpc01-us-central1-private--service-account=sa-dataproc-nodes@prj-grp-general-sandbox-7f70.iam.gserviceaccount.com --single-node --master-machine-type n1-standard-2 --master-boot-disk-size 200 --image-version=1.5-centos8 --labels cluster-pool=pool-1 --project $PROJECT_ID --tags=allow-iap-ssh,dataproc-vm,egress-internet
```

```
gcloud dataproc clusters create cluster-pull-2 --region $REGION --no-address --zone $ZONE --single-node --master-machine-type n1-standard-2 --subnet=projects/prj-grp-sharedvpc-e2b0/regions/us-central1/subnetworks/sub-vpc-dev-sharedvpc01-us-central1-private --service-account=sa-dataproc-nodes@prj-grp-general-sandbox-7f70.iam.gserviceaccount.com --master-boot-disk-size 200 --image-version=1.5-centos8  --labels cluster-pool=pool-1 --project $PROJECT_ID --tags allow-iap-ssh,dataproc-vm,egress-internet
```

##  6. <a name='Initializationactions'></a>6. Initialization actions

###  6.1. <a name='Createthebuckets'></a>6.1  Create the buckets

```
gsutil mb -b on gs://$AUDIT_BUCKET
gsutil mb -b on gs://$DISTCP_BUCKET
gsutil mb -b on gs://$SOURCE_FILES_DATA_BUCKET
```

**$AUDIT_BUCKET** is where the audit files will be stored,  **$DISTCP_BUCKET** is the destiny bucket where the files specified in the audit files will be copied using distcp. **$SOURCE_FILES_DATA_BUCKET** will be the bucket that contains the buckets needed to create the simulated on prem cluster.  


##  7. <a name='CopytheinputfiletotheSOURCE_FILES_DATA_BUCKETbucket'></a>6.2. Copy the input file to the $SOURCE_FILES_DATA_BUCKET bucket

```bash
gsutil cp ./input_data/titanic.csv gs://$SOURCE_FILES_DATA_BUCKET/input_data/titanic.csv
```


##  8. <a name='Modifytheaudit_hdfs_script.shandinitialize_onprem_cluster.shfiles'></a>6.3. Modify the  audit_hdfs_script.sh and initialize_onprem_cluster.sh files 

In this step, the **audit_hdfs_script.sh** and **initialize_onprem_cluster.sh** is going to be modified, in the second line of both files, modify ``USER_NAME_GOOGLE``  variable with the user name that appears in the left side on the cloud shell without @cloudshell , example:

![](images/image3.png)
*Picture 3: user name example*

To modify the **audit_hdfs_script.sh** file use the following command: 

```
vim audit_hdfs_script.sh
```

Click **i** to edit the file, copy the name in the second line. Then press **ESC** and write **:wq** to write and quit to the file. 

![](images/image4.png)
*Picture 4:  audit_hdfs_script.sh file*

To modify the **initialize_onprem_cluster.sh** file use the following command: 

```
vim initialize_onprem_cluster.sh
```

Click **i** to edit the file, copy the name in the second line. Then press **ESC** and write **:wq** to write and quit to the file. 

![](images/image5.png)
*Picture 5:  initialize_onprem_cluster.sh file*

###  8.1. <a name='CopytheshellfilestotheSOURCE_FILES_DATA_BUCKETbucket'></a>6.4. Copy the  shell files to the $SOURCE_FILES_DATA_BUCKET bucket

Once the **audit_hdfs_script.sh** was modified with the correct user name, copy the file **audit_hdfs_script.sh** and **initialize_onprem_cluster.sh** to the source-files-data-onprem-groupon bucket with the following commands:

```
gsutil cp audit_hdfs_script.sh gs://$SOURCE_FILES_DATA_BUCKET/audit_hdfs_script.sh
```

```
gsutil cp initialize_onprem_cluster.sh gs://$SOURCE_FILES_DATA_BUCKET/initialize_onprem_cluster.sh
```

##  9. <a name='Createtheon-premisesimulatedcluster'></a>7. Create the on-premise simulated cluster

Create a dataproc cluster that is going to simulate an on-premise cluster, this cluster will be created with the initialization actions found in the **initialize_onprem_cluster.sh** file which was copied to the *$SOURCE_FILES_DATA_BUCKET* in the previous step. 

```
gcloud dataproc clusters create $ONPREM_CLUSTER --region $REGION \
    --zone $ZONE --single-node --master-machine-type n1-standard-2 \
    --master-boot-disk-size 200 --image-version 2.0.28-debian10 --project $PROJECT_ID \
    --initialization-actions=gs://$SOURCE_FILES_DATA_BUCKET/initialize_onprem_cluster.sh
```

##  10. <a name='SSHintotheon-premisesimulatedmastercluster'></a>8. SSH into the on-premise simulated master cluster

In the cloud shell copy the following command to enter into the ssh master cluster that was created in the previous step. 

```
gcloud compute ssh --zone ${ZONE} ${ONPREM_CLUSTER}-m
```

###  10.1. <a name='Addfilestothetwofoldersthatarecreatedintheon-premisesimulatedcluster'></a>8.1. Add files to the two folders that are created in the on-premise simulated cluster

```
hdfs dfs -copyFromLocal titanic.csv folder_1/file_1.csv
hdfs dfs -copyFromLocal titanic.csv folder_1/file_2.csv
hdfs dfs -copyFromLocal titanic.csv folder_1/file_3.csv
hdfs dfs -copyFromLocal titanic.csv folder_2/file_4.csv
hdfs dfs -copyFromLocal titanic.csv folder_2/file_5.csv
```

##  11. <a name='ChecktheauditfilesinGoogleCloudStorage'></a>9. Check the audit files in Google Cloud Storage

Wait for about 5 minutes and then open the GCS bucket named **audit-file-distcp-bucket1**, you should find inside this bucket a file with the prefix **folders_to_copy_**, the next value in the name corresponds to the time where the file was created. 


![](images/image6.png)
*Picture 6:  audit-file-distcp-bucket1 content*

If you click on the file and then click on the link which is on the **Authenticated URL** you will see the content of the file, the file has two lines. The first part of every line, for example:  *hdfs://cluster-src-m/user/churtado_gcp/folder_3* correspond to the path in HDFS where a file or files were added to the folder in the last five minutes, and the next part correspond to the bucket and folder in GCS where that folder in HDFS is going to be copied using distcp *gs://dest-distcp-bucket-demo/folder_3*.

###  11.1. <a name='Createtwonewdirectoriesandaddfilestothesedirectories'></a>9.1. Create two new directories and add files to these directories

Get back to the ssh master cluster and create two new directories and add files to these folders:

```
hdfs dfs -mkdir folder_3/
```

``` 
hdfs dfs -copyFromLocal titanic.csv folder_3/file_6.csv
hdfs dfs -copyFromLocal titanic.csv folder_3/file_7.csv
```

``` 
hdfs dfs -mkdir folder_4/
```

```
hdfs dfs -copyFromLocal titanic.csv folder_4/file_8.csv
hdfs dfs -copyFromLocal titanic.csv folder_4/file_9.csv
```

The command to exit to the ssh master and get back to the cloud shell is:

```
exit
```

*Note: Wait for about 5 minutes and then If you check again the audit-file-distcp-bucket1 bucket another file was added, the content of this new file will be the data needed to execute the distcp in the next steps.*

##  12. <a name='CopytheDistCpAirflowDAGtothecomposerenvironment'></a>10. Copy the DistCp Airflow DAG to the composer environment 

In the cloud shell, verify that you are inside the folder where the files needed to execute the POC are located. If not, use the following command:

```
cd distcp_gcs_sensor_v1/ 
```

Copy the python file that contains the Airflow DAG to the DAGs folder inside the composer environment named **distcp-orch** 

```
gcloud composer environments storage dags import --environment distcp-orch --location $REGION --source airflow_parallel_distcp_dag_gcs_sensor.py
```

###  12.1. <a name='OpenAirflow'></a>10.1. Open Airflow 

Open composer and select Airflow to open the Airflow webserver

![](images/image7.png)
*Picture 7:  Cloud Composer*

###  12.2. <a name='ClickontheDAGnameddistcp_incremental_gcs_sensor'></a>10.2. Click on the DAG named **distcp_incremental_gcs_sensor**

The **distcp_incremental_gcs_sensor** DAG is scheduled to be executed every five minutes. The first and last tasks of this DAG are created using a ``DummyOperator``. Those two tasks were created in order to clarify the start and end of the DAG.  The next task is going to use an airflow operator named ``GCSObjectsWithPrefixExistenceSensor`` to validate if there is any file in the bucket named *audit-file-distcp-bucket1*. If there is any file inside the bucket with the prefix *folders_to_copy_*, a group task per file is created. 

The group tasks will contain two types of tasks, the first one is related to submission of the dataproc job that is going to execute the distcp, these tasks are created using ``BashOperator``and the second one is the task in charge of deleting the audit file using the operator ``GCSDeleteObjectsOperator``.

A task in charge of submitting the dataproc job to execute the distcp is created per line in the audit file with the prefix *folders_to_copy_* and only one task about deleting the file is created per task group. The DAG diagram created in Airflow about this POC is in the next image, you can see it in Airflow clicking on **Graph View**:

![](images/image8.png)  
*Picture 8:  Graph view of the Airflow DAG created to execute the DistcCp Incremental POC using GCS sensor* 

If you check the **audit-file-distcp-bucket1** bucket in GCS once the DAG has successfully ended, there will not be more txt files with the *prefix folders_to_copy_* in the bucket because those files were deleted, and if you check the **dest-distcp-bucket-demo bucket**, all the folders with the files that were specified in the folders_to_copy_ txt files now were copied to this bucket as you can see in the following image.  

![](images/image9.png)  
*Picture 9:   audit-file-distcp-bucket1  content*

