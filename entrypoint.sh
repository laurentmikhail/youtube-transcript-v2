#!/bin/sh
set -e

# This command executes the CMD from the Dockerfile,
# ensuring the shell correctly processes environment variables like $PORT.
exec "$@"
