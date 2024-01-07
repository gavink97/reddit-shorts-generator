FROM ubuntu:20.04

ARG PYTHON_VERSION=3.11.7

ENV LANG=C.UTF-8

ENV PYTHONUNBUFFERED=1

USER root

ENV STARTUPDIR /app
ENV PATH /usr/local/bin:$PATH

ENV HOME /home/default

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Jakarta

WORKDIR $HOME

# VPN Singapore 61
RUN : \
&& apt update \
&& apt install -y -o Debug::pkgProblemResolver=1 libpng-dev libjpeg-dev software-properties-common \
&& apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev \
&& apt update \
&& apt install -y -o Debug::pkgProblemResolver=1 ffmpeg bash cron fonts-liberation git \
&& apt update \
&& add-apt-repository -y ppa:mozillateam/ppa \
&& echo '\
Package: *\
Pin: release o=LP-PPA-mozillateam\
Pin-Priority: 1001\

Package: firefox\
Pin: version 1:1snap1-0ubuntu2\
Pin-Priority: -1\
' | tee /etc/apt/preferences.d/mozilla-firefox\
&& apt update \
&& apt install -y firefox python3-pip \
&& :

WORKDIR /opt

RUN : \
&& wget -qO- https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz | tar -xJf - \
&& cd Python-$PYTHON_VERSION \
&& ./configure \
 --prefix=/opt/python/$PYTHON_VERSION\
 --enable-optimizations\
 --enable-shared\
 LDFLAGS=-Wl,-rpath=/opt/python/$PYTHON_VERSION/lib,--disable-new-dtags \
&& make -j 6 \
&& make install \
&& :

WORKDIR /opt/python/$PYTHON_VERSION

COPY --link requirements.txt .

# For some reason install pip as non root user makes dotenv module not load
# fix message pip install pygobject
RUN : \
&& update-alternatives --install /usr/local/bin/python python /opt/python/$PYTHON_VERSION/bin/python3 1 \
&& update-alternatives --install /usr/local/bin/python3 python3 /opt/python/$PYTHON_VERSION/bin/python3 1 \
&& update-alternatives --install /usr/local/bin/pip pip /opt/python/$PYTHON_VERSION/bin/pip3 1 \
&& python -m pip install --user --no-cache-dir --upgrade pip \
&& pip install --verbose wheel setuptools --upgrade \
&& pip install --verbose --no-cache-dir -r requirements.txt \
&& apt-get autoremove -yqq --purge \
&& rm -rf /var/lib/apt/lists/* \
&& rm -rf /var/log/* \
&& :

WORKDIR $STARTUPDIR

COPY cronjob /etc/cron.d/shorts-cron

RUN : \
&& useradd --uid 1001 user \
&& chmod 0644 /etc/cron.d/shorts-cron \
&& crontab /etc/cron.d/shorts-cron \
&& crontab -u user /etc/cron.d/shorts-cron \
&& chmod u+s /usr/sbin/cron \
&& touch /var/log/cron.log \
&& chmod u+rwx /var/log/cron.log \
&& chown user:0 $HOME \
&& :

ENV HOME /home/user

WORKDIR $HOME

RUN mkdir -p $HOME && chown -R user:0 $HOME

USER user

# ENTRYPOINT /usr/local/bin/python3 -u /pyapp/main.py
CMD cron && tail -f /var/log/cron.log
