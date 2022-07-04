FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get -y install vim nano
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y wget
#RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#RUN apt-get install ./google-chrome-stable_current_amd64.deb -y
#RUN apt-get install xvfb -y

RUN mkdir /leolist
WORKDIR /leolist
COPY ./ /leolist

RUN pip install -r ./requirements.txt
CMD ["python", "app.py"]