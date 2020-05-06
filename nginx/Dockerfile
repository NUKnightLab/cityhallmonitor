FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
COPY conf.d/ /etc/nginx/conf.d/
RUN ln -sf /dev/stdout /var/log/nginx/cityhallmonitor.log \
	&& ln -sf /dev/stderr /var/log/nginx/cityhallmonitor.err.log
