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

echo "Обновление проекта успешно завершено"
