FROM nginx:1.11

RUN rm -rf /etc/nginx/conf.d

COPY ./sites-enabled/web.conf /etc/nginx/conf.d/web.conf
COPY ./assets/ /usr/share/nginx/html/