#!/usr/bin/env bash

echo "Enter your email address.";
read -r email;

echo "Enter the app password.";
read -r password

echo "EMAIL_HOST_USER='$email'" | sudo tee -a /opt/bitnami/projects/quicksched/.env
echo "EMAIL_HOST_PASSWORD='$password'" | sudo tee -a /opt/bitnami/projects/quicksched/.env
sudo chown -R daemon:daemon /opt/bitnami/projects/quicksched/*
