FROM ubuntu:24.04

# Use bash instead of sh.
SHELL ["/bin/bash", "-c"]

EXPOSE 8010

# non-interactive
ARG DEBIAN_FRONTEND=noninteractive

# set Honolulu Timezone
ENV TZ="Pacific/Honolulu"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Use the default UTF-8 language.
ENV LANG=C.UTF-8

RUN apt update && apt upgrade -y
RUN apt-get install -y software-properties-common build-essential

# Add Python packages and other goodiexs
RUN add-apt-repository ppa:deadsnakes/ppa -y; 
RUN apt-get install -y python3-pip python3-dev python3-venv\
    python-is-python3 \
    vim \
    wget \
    curl \
    git;

# Install PyDiet
WORKDIR /opt/pydiet
COPY . /opt/pydiet/

# Create Pythyon virtual environment and run install via pip.
RUN python3 -m venv venv_pydiet && \
    source venv_pydiet/bin/activate && \
    pip install . && \
    pip install pydiet[doc]

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the script and make it executable
COPY ./docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["sleep", "infinity"]
# you CMD should look something like this
# CMD ["/bin/bash", "-c", "python your_app_script.py"]

