#!/bin/bash

cd ./flask_app
python init_db.py
cp /pubapps/npdc/npdc_portal/instance/db_data/npdc_portal.db /pubapps/npdc/npdc_portal/instance/db_data/npdc_portal_searchable.db
python init_db_searchable.py
cd ..
python ./runner/runner.py
