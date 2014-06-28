IP=$(cat edoAutoHome.conf | awk '$1 ~ /db_ip/ {print $3}')
NAME=$(cat edoAutoHome.conf | awk '$1 ~ /db_name/ {print $3}')
USER=$(cat edoAutoHome.conf | awk '$1 ~ /db_user/ {print $3}')
PASS=$(cat edoAutoHome.conf | awk '$1 ~ /db_pass/ {print $3}')
mysql -u${USER} -p${PASS} -h${IP} -D${NAME}
