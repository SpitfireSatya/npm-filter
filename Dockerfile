FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y install --no-install-recommends python3 python3-pip git unzip vim curl gnupg xz-utils parallel chromium-browser

RUN pip3 install bs4 scrapy

SHELL ["/bin/bash", "--login", "-i", "-c"]
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
RUN source /root/.bashrc
RUN nvm install 16
RUN nvm install 18 
RUN nvm install 14
RUN nvm install 12
RUN nvm use 16

RUN mkdir -p /home/npm-filter/results

COPY . /home/npm-filter

WORKDIR /home/npm-filter

RUN git config --global http.sslVerify "false"
RUN npm config set strict-ssl false
RUN ./build.sh
