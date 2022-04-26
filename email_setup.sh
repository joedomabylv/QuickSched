#!/usr/bin/env bash

echo "Enter your email address.";
read -r email;

echo "Enter the app password.";
read -r password

echo "EMAIL_HOST_USER='$email'" >> /opt/bitnami/projects/quicksched/.env
echo "EMAIL_HOST_PASSWORD='$password'" >> /opt/bitnami/projects/quicksched/.env
