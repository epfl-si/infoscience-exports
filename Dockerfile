FROM python:3.5

# create directories
RUN mkdir -p /usr/src/app && \
	mkdir -p /usr/src/app/staticfiles && \
	mkdir -p /usr/src/app/infoscience_exports && \
	mkdir -p /var/log/django

# install requirements 
# (asap to make cache more efficent)
COPY ./requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip install -r requirements.txt

# copy project files
COPY ./staticfiles /usr/src/app/staticfiles
COPY ./infoscience_exports /usr/src/app/infoscience_exports
