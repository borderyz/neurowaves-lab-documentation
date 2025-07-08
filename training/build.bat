REM stop & remove any half-built containers
docker compose down
REM fetch moodlehq/moodle-php-apache:8.3  +  mariadb:11
docker compose pull
REM  (re)create with correct images
docker compose up -d