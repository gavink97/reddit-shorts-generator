FROM python:3.11-bookworm

ENV LANG=C.UTF-8

ENV PYTHONUNBUFFERED=1

USER root

ENV STARTUPDIR /app

ENV HOME /home/default

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Jakarta

WORKDIR $HOME

# VPN Singapore 61
RUN : \
&& apt update \
&& apt install -y -o Debug::pkgProblemResolver=1 libpng-dev libjpeg-dev libtiff-dev libmagick++-dev \
&& apt update \
&& apt install -y -o Debug::pkgProblemResolver=1 firefox-esr imagemagick ffmpeg bash cron python3-dotenv \
&& echo "deb http://deb.debian.org/debian bookworm contrib non-free" > /etc/apt/sources.list.d/contrib.list \
&& apt update \
&& apt install -y -o Debug::pkgProblemResolver=1 ttf-mscorefonts-installer \
&& :

COPY --link requirements.txt .
# For some reason install pip as non root user makes dotenv module not load
# fix message pip install pygobject
RUN : \
&& pip install --verbose wheel setuptools pip --upgrade \
&& pip install --verbose --no-cache-dir -r requirements.txt \
&& :

WORKDIR $STARTUPDIR

COPY cronjob /etc/cron.d/shorts-cron

RUN : \
&& useradd --uid 1000 1000 \
&& chmod 0644 /etc/cron.d/shorts-cron \
&& crontab /etc/cron.d/shorts-cron \
&& crontab -u 1000 /etc/cron.d/shorts-cron \
&& chmod u+s /usr/sbin/cron \
&& touch /var/log/cron.log \
&& chmod u+rwx /var/log/cron.log \
&& chown 1000:0 $HOME \
&& :

ENV HOME /home/user

WORKDIR $HOME

RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000

# ENTRYPOINT /usr/local/bin/python3 -u /pyapp/main.py
CMD cron && tail -f /var/log/cron.log
