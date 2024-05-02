FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
# Install necessary packages
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libgl1-mesa-glx nano ghostscript python3-tk python3.8-venv python3.8 git python3-pip python3-dotenv && \
    apt-get clean
    
RUN pip3 install opencv-python jupyter camelot-py pandas ghostscript shortuuid requests langdetect python-dotenv
# Set the default shell to bash
ENV SHELL /bin/bash
# COPY . /root
# Set the command to open a new terminal session
# CMD ["/bin/bash"]