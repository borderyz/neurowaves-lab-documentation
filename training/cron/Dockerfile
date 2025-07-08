FROM php:8.3-cli-alpine
WORKDIR /var/www/html

# just cron
RUN apk add --no-cache bash busybox-extras

# run cron in foreground
CMD ["sh", "-c", "echo '* * * * * php /var/www/html/admin/cli/cron.php >/proc/1/fd/1 2>&1' | crond -f"]
