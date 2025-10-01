# NPDC portal
Web-based internal database for managing and serving NPDC genome sequencing data.

## Quick Start

### Prerequisites
- requirements.txt

### Setup

1. **Configure environment**
   ```bash
   cp env_example.sh env_local_dev.sh
   ```
   or
   ```
   cp env_example.sh env_local_prod.sh
   ```
2. **Edit and Set environment variables**
   ```bash
   # Example: edit env_local_prod.sh 
   source env_local_prod.sh
   ```
3. **Start services**
   ```
   ./startup.sh
   ```
   or
   ``` 
   cd ./flask_app
   python init_db.py
   cp /pubapps/npdc/npdc_portal/instance/db_data/npdc_portal.db /pubapps/npdc/npdc_portal/instance/db_data/npdc_portal_searchable.db
   python init_db_searchable.py
   cd ..
   python ./runner/runner.py

   ```
