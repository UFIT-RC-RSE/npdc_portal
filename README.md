# NPDC portal
Web-based internal database for managing and serving NPDC genome sequencing data.

## Quick Start

### Prerequisites
- requirements.txt

### Setup

1. **Configure environment**
   Create a copy of the environment template in the `/instance` directory. This will serve as the configuration for the running instance of the NPDC portal.
   ```bash
   cp env.sh.template instance/env.sh
   ```
   **Edit and Set environment variables**
   ```bash 
   nano ./instance/env.sh
   source env.sh
   ```
   Note: The container automatically sources this file on running via `startup.sh`.
   
2. **Build the container for the application**
	```
	# Example: dev container in /npdc_portal_dev - 'npdc-dev'
	podman rm npdc-dev # remove any existing container by the same name
	
	podman build -t npdc-dev .
	podman run -d \
	--name npdc-dev \
	-v ./instance:/npdc_portal/instance:Z \
	-p $NPDC_GUNICORN_PORT:$NPDC_GUNICORN_PORT \ # check or source env.sh
	npdc-dev
	```
	**Note: `systemd` service for the container**
	In some cases, it may be necessary to replace the systemd service for running the container. You can generate it easily using podman:
	```
	# Example: service for development deployment
	podman generate systemd --name npdc-dev --files --restart-policy=always
	
	loginctl enable-linger $USER
	mv container-npdc-dev.service .config/systemd/user # generated .service file
	systemctl --user enable container-npdc-dev
	systemctl --user daemon-reload
	```
	**Starting / Stopping / Restarting / Checking the service**
	```
	systemctl --user start container-npdc-dev
	systemctl --user stop container-npdc-dev
	systemctl --user restart container-npdc-dev
	systemctl --user status container-npdc-dev
	```
   
3. **(Optional) Perform searchable database copy step**
When `npdc.db` is updated in `/instance/db_data`, before redeploying, perform this step. You can perform this step after building the container.
   ```
   bash init_db.sh
   ```
   
4. **Starting the portal service (containerized deployment)**
   ```
   # Example: development instance
   systemctl --user start container-npdc-dev
   
   # check status
   systemctl --user status container-npdc-dev
   ```
   
   **Starting the portal (uncontainerized)**
   ```
   bash ./startup.sh
   ```
