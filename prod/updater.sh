#! ../../usr/bin/bash

set -e

git pull

source venv/bin/activate
pip install -r requirements.txt
npm ci 

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

deactivate

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
