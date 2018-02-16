FROM nginx:stable

RUN rm -rf /etc/nginx/conf.d

COPY ./certs/ /etc/nginx/certs/
COPY ./sites-enabled/web.conf /etc/nginx/conf.d/web.conf
COPY ./assets/ /usr/share/nginx/html/