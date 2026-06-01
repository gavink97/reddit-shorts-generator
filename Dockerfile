FROM python:3.11-bookworm

ENV LANG=C.UTF-8

ENV PYTHONUNBUFFERED=1

USER root

ENV STARTUPDIR /app

ENV HOME /home/default

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Jakarta

WORKDIR $HOME

RUN : \
&& apt update \
&& apt install -y \
    -o Debug::pkgProblemResolver=1 \
    --no-install-recommends \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    libmagick++-dev \
&& apt update \
&& apt install -y \
    -o Debug::pkgProblemResolver=1 \
    --no-install-recommends \
    firefox-esr \
    imagemagick \
    ffmpeg \
    bash \
    cron \
    python3-dotenv \
    fonts-liberation \
    git \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* \
&& :

COPY --link requirements.txt .
COPY --link reddit-shorts/setup.py .
COPY --link reddit-shorts/shorts ./shorts
COPY --link reddit-shorts/setup.cfg .
COPY --link reddit-shorts/.env .

# For some reason install pip as non root user makes dotenv module not load
# fix message pip install pygobject
RUN : \
&& pip install --verbose wheel setuptools pip --upgrade \
&& pip install --verbose --no-cache-dir -r requirements.txt \
&& pip install -e . \
&& :

WORKDIR $STARTUPDIR

COPY cronjob /etc/cron.d/shorts-cron

RUN : \
&& useradd --uid 1000 user \
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

RUN mkdir -p $HOME && chown -R user:1000 $HOME

USER 1000

RUN mkdir -p $HOME/.cache/fontconfig && \
    chmod -R 700 $HOME/.cache

# ENTRYPOINT /usr/local/bin/python3 -u /pyapp/main.py
CMD cron && tail -f /var/log/cron.log
