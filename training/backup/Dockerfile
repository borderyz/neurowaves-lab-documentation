FROM node:20-alpine

RUN apk add --no-cache bash tar gzip rsync curl docker-cli tini \
 && npm install -g @box/cli            # Box CLI v4

ENV BOX_CONFIG_FILE=/opt/box_config.json
RUN box configure:environments:add /opt/box_config.json


COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh \
 && echo "0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1" > /etc/crontabs/root

ENTRYPOINT ["/sbin/tini","--"]
CMD ["crond","-f"]
