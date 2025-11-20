#!/bin/sh

# Use environment variables with defaults
USER_NAME_GOOGLE=${USER_NAME_GOOGLE:-churtado_gcp1}
SOURCE_FILES_DATA_BUCKET=${SOURCE_FILES_DATA_BUCKET:-source-files-data-distcp}
ENVIRONMENT=${ENVIRONMENT:-dev}

echo "Initializing cluster for environment: $ENVIRONMENT"
echo "User: $USER_NAME_GOOGLE"
echo "Bucket: $SOURCE_FILES_DATA_BUCKET"

cd "/home/$USER_NAME_GOOGLE" || exit

gsutil cp "gs://$SOURCE_FILES_DATA_BUCKET/input_data/titanic.csv" "/home/$USER_NAME_GOOGLE/titanic.csv"
gsutil cp "gs://$SOURCE_FILES_DATA_BUCKET/audit_hdfs_script.sh" "/home/$USER_NAME_GOOGLE/audit_hdfs_script.sh"

sudo hdfs dfs -mkdir "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/"

hdfs dfs -mkdir "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_1/"

hdfs dfs -copyFromLocal "/home/$USER_NAME_GOOGLE/titanic.csv" "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_1/file_1.csv"
hdfs dfs -copyFromLocal "/home/$USER_NAME_GOOGLE/titanic.csv" "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_1/file_2.csv"
hdfs dfs -copyFromLocal "/home/$USER_NAME_GOOGLE/titanic.csv" "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_1/file_3.csv"

hdfs dfs -mkdir "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_2/"

hdfs dfs -copyFromLocal "/home/$USER_NAME_GOOGLE/titanic.csv" "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_2/file_4.csv"
hdfs dfs -copyFromLocal "/home/$USER_NAME_GOOGLE/titanic.csv" "hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/folder_2/file_5.csv"

sudo chmod +x "/home/$USER_NAME_GOOGLE/audit_hdfs_script.sh"
echo "*/5 * * * * /home/$USER_NAME_GOOGLE/audit_hdfs_script.sh" > "/home/$USER_NAME_GOOGLE/mycron"
sudo chmod 777 "/home/$USER_NAME_GOOGLE/mycron"
sudo crontab "/home/$USER_NAME_GOOGLE/mycron"