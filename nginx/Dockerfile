FROM nginx:stable

RUN rm -rf /etc/nginx/conf.d

COPY ./certs/ /etc/nginx/certs/
COPY ./sites-enabled/web.template /etc/nginx/conf.d/web.template
COPY ./assets/ /usr/share/nginx/html/
