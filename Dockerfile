# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Vijay Reddy

# Update the sources list
RUN apt-get update

# Install python, pip and git
RUN apt-get install -y python=2.7.5-5ubuntu3 python-pip=1.5.4-1ubuntu3 git

# Install Google API python client
RUN pip install --upgrade google-api-python-client

# Install Open Computer Vision python module, used for extracting stills from video
RUN apt-get install -y python-opencv

# This gets rid of the "libdc1394 error: Failed to initialize libdc1394" warning
RUN ln /dev/null /dev/raw1394

# Download application from git repository
RUN git clone https://github.com/vijaykyr/coke-vision-api.git /application

# Set the default directory where CMD will execute
WORKDIR /application