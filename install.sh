#!/usr/bin/env bash

# generate .env file
django_key=$(echo $RANDOM | md5sum | head -c 30);
"SECRET_KEY=$django_key" >> env_file;

# rename env file
mv /home/bitnami/QuickSched/project/env_file /home/bitnami/QuickSched/project/.env

# rename and enable vhost files
sudo cp /opt/bitnami/apache2/conf/vhosts/sample-vhost.conf.disabled /opt/bitnami/apache2/conf/vhosts/quicksched-vhost.conf;
sudo cp /opt/bitnami/apache2/conf/vhosts/sample-https-vhost.conf.disabled /opt/bitnami/apache2/conf/vhosts/quicksched-https-vhost.conf;

# edit vhost files to configure them for quicksched
sudo sed -r -i 's/sample|SAMPLE/quicksched/g' /opt/bitnami/apache2/conf/vhosts/quicksched-vhost.conf;
sudo sed -r -i 's/sample|SAMPLE/quicksched/g' /opt/bitnami/apache2/conf/vhosts/quicksched-https-vhost.conf;

# install decouple dependency
pip install python-decouple;

# move decouple to other directory for apache daemon
sudo cp .local/lib/python3.8/site-packages/decouple.py /opt/bitnami/python/lib/python3.8/decouple.py;

# make a directory for deployed django files
sudo mkdir -pv /opt/bitnami/projects/quicksched/;

# deploy django files to specified directory
sudo mv /home/bitnami/QuickSched/project/* /opt/bitnami/projects/quicksched/;

# set up django database
python /opt/bitnami/projects/quicksched/project/manage.py makemigrations;
python /opt/bitnami/projects/quicksched/project/manage.py migrate;

# create new superuser
python /opt/bitnami/projects/quicksched/project/manage.py createsuperuser;

# collect static files for apache to serve
python /opt/bitnami/projects/quicksched/project/manage.py collectstatic --noinput;

# change the owner of the django files to the apache wsgi mod daemon
sudo chown -R daemon:daemon /opt/bitnami/projects/quicksched/

# restart apache
sudo /opt/bitnami/ctlscript.sh restart apache

# report success
echo "\n\n\n\nYou have successfully installed your QuickSched instance! Enter your server's public IP address in your browser to login with your credentials."
