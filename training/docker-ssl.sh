#!/bin/sh
a2enmod ssl 2>&1
exec "$@"