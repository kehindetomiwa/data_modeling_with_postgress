FROM ubuntu:latest
RUN apt-get update && apt-get -y update
RUN apt-get install -y build-essential python3.7 python3-pip python3-dev  libpq-dev
RUN pip3 install pip --upgrade

#RUN apt-get update && apt-get -y upgrade
#RUN apt-get install -y build-essential python-dev
#RUN apt-get install -y python python-distribute python-pip
#RUN pip install pip --upgrade

RUN mkdir src
WORKDIR src
COPY . .

# Copy app files from local to container

RUN pip3 install -r requirements.txt
RUN pip3 install psycopg2
RUN pip3 install jupyter
RUN pip3 install numpy
WORKDIR .


# Add Tini. Tini operates as a process subreaper for jupyter. This prevents kernel crashes.
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]