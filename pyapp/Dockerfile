FROM python:3.11-bullseye

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
&& apt install wget curl libpng-dev libjpeg-dev libtiff-dev \
&& wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
&& apt install ./google-chrome-stable_current_amd64.deb \
&& curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor | sudo tee /usr/share/keyrings/google-chrome.gpg >> /dev/null \
&& echo deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main | sudo tee /etc/apt/sources.list.d/google-chrome.list \
&& apt update \
&& apt install google-chrome-stable ffmpeg imagemagick \
&& :

COPY --link requirements.txt .

RUN : \
&& pip install wheel setuptools pip --upgrade \
&& pip install --no-cache-dir -r requirements.txt \
&& :

WORKDIR $STARTUPDIR

RUN : \ 
&& echo "#!/bin/bash" > $STARTUPDIR/startup.sh \
&& echo "/usr/local/bin/python3 -u /pyapp/main.py" >> $STARTUPDIR/startup.sh \
&& crontab -l > crontab_new \
&& rm crontab_new \
&& echo "30 0 * * * /home/baeldung/job.sh" >> crontab_new \
&& crontab crontab_new \
&& chmod +x $STARTUPDIR/startup.sh \
&& chown 1000:0 $HOME \
&& :

ENV HOME /home/user

WORKDIR $HOME

RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000

ENTRYPOINT [ "/app/startup.sh" ]
