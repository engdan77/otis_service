#!/usr/bin/env bash
IP=$(cat otis_service.conf | awk '$1 ~ /db_ip/ {print $3}')
NAME=$(cat otis_service.conf | awk '$1 ~ /db_name/ {print $3}')
USER=$(cat otis_service.conf | awk '$1 ~ /db_user/ {print $3}')
PASS=$(cat otis_service.conf | awk '$1 ~ /db_pass/ {print $3}')
mysql -u${USER} -p${PASS} -h${IP} -D${NAME}
