#! ../../usr/bin/bash

set -e

git pull

make up
make migrate

systemctl daemon-reload
systemctl reload nginx.service

source .env
commit_hash=$(git rev-parse HEAD)
curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_ACCESS_TOKEN \
  -F environment=$ROLLBAR_ENVIRON \
  -F revision=$commit_hash \
  -F local_username=$ROLLBAR_NAME \
  -F comment="Deployed new version" \
  -F status=succeeded

echo "Обновление проекта успешно завершено"
