#!/bin/sh
export USER_NAME_GOOGLE=churtado_gcp
now=$(date +%s)
src=hdfs://cluster-src-m/user/$USER_NAME_GOOGLE/
dst=gs://dest-distcp-bucket-demo/
dst_text_file=gs://audit-file-distcp-bucket1/
dir_to_copy=$1
cd /home/$USER_NAME_GOOGLE

hdfs dfs -ls -R $src/$dir_to_copy | grep "^d" | while read f; do

  dir_date_day=`echo $f | awk '{print $6}'`
  dir_date_hour=`echo $f | awk '{print $7}'`
  difference=$((( $now - $(date -d "$dir_date_day $dir_date_hour" +%s) ) / ( 60 )))

  if [ $difference -lt 5 ]; then
    distcp_source=$(echo $f | sort -k6,7 | tr -s ' ' | awk '{print $8}')
    folder=$(echo ${distcp_source##*$src})
    echo $distcp_source,$dst$folder >> folders_to_copy.txt
    echo "$now: " $distcp_source $dst$folder >> audit_log.txt
  fi

done
gsutil cp folders_to_copy.txt $dst_text_file
rm folders_to_copy.txt