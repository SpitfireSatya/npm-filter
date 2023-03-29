FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
	&& apt-get -y install --no-install-recommends python3 git unzip vim curl gnupg nodejs npm xz-utils parallel nano chromium-browser

RUN apt update
RUN apt -y install python3-pip
RUN pip3 install bs4 scrapy
RUN npm install -g typescript npx @angular/cli

SHELL ["/bin/bash", "--login", "-i", "-c"]
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
RUN source /root/.bashrc && nvm install 18.15.0
SHELL ["/bin/bash", "--login", "-c"]

RUN mkdir -p /home/npm-filter/results

COPY . /home/npm-filter

WORKDIR /home/npm-filter

RUN git config --global http.sslVerify "false"
RUN npm config set strict-ssl false
RUN ./build.sh
