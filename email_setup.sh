#!/usr/bin/env bash

echo "Enter your email address.";
read -r email;

echo "Enter the app password.";
read -r password

sudo echo "EMAIL_HOST_USER='$email'" >> /opt/bitnami/projects/quicksched/.env
sudo echo "EMAIL_HOST_PASSWORD='$password'" >> /opt/bitnami/projects/quicksched/.env
sudo chown -R daemon:daemon /opt/projects/bitnami/quicksched/*
