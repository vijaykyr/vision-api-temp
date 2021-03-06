# Set the base image to Ubuntu
FROM ubuntu

# Update the sources list
RUN apt-get update

# Install python, pip and git
RUN apt-get install -y python=2.7.5-5ubuntu3 python-pip=1.5.4-1ubuntu3

# Install Google API python client
RUN pip install --upgrade google-api-python-client

# Install Open Computer Vision python module, used for extracting stills from video
RUN apt-get install -y python-opencv

# Copy application to container (assumes code is in current directory)
ADD . /application 

# Set the default directory where CMD will execute
WORKDIR /application

# This gets rid of the "libdc1394 error: Failed to initialize libdc1394" warning
# Edit: Actually for some reason this command doesn’t take unless you run it from inside the container (after the image is built)
RUN ln /dev/null /dev/raw1394
