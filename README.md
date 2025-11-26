# NPDC portal
Web-based internal database for managing and serving NPDC genome sequencing data.

## Quick Start

### Prerequisites
- podman

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
        ```
        In the case you need to run the container on a local machine outside of the quadlet-style service:
        ```
        podman run -d \
        --name npdc-dev \
        -v ./instance:/npdc_portal/instance:Z \
        -p $NPDC_GUNICORN_PORT:$NPDC_GUNICORN_PORT \ # check or source env.sh
        npdc-dev
        ```
        **Note: `systemd` service for the container**
        In some cases, it may be necessary to replace the systemd service for running the container. This can be accomplished simply in deployment by creating a `.container` file:
        ```
        # Example: service for development deployment
        # container-npdc-dev.container - NPDC portal development service container .container file
        [Unit]
        Wants=network-online.target
        After=network-online.target
        Description=Podman - NPDC Portal (dev)
        After=local-fs.target

        [Container]
        Image=npdc-dev:latest
        ContainerName=npdc-dev
        PublishPort=8334:8334
        Network=host

        # Mount volumes - instance, slurm, and diamond access
        Volume=%h/npdc_portal_dev/instance:/npdc_portal/instance:Z
        Environment=PYTHONPATH=/npdc_portal

        Volume=/tmp:/tmp:Z
        Volume=/opt/slurm:/opt/slurm:Z

        # Munge
        Volume=/var/run/munge:/run/munge:Z

        # Set PATH - include slurm, diamond
        Environment=PATH=/opt/slurm/bin:/opt/diamond:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

        # Keep UID/GID
        UserNS=keep-id
        ```
        ```
        loginctl enable-linger $USER
        mv container-npdc-dev.container .config/containers/systemd/ # new .container file
        systemctl --user daemon-reload
        ```
        **Starting / Stopping / Restarting / Checking the service**
        ```
        systemctl --user start container-npdc-dev.service
        systemctl --user stop container-npdc-dev.service
        systemctl --user restart container-npdc-dev.service
        systemctl --user status container-npdc-dev.service
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
