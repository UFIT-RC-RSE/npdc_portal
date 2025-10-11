#!/usr/bin/env python3
import os

conf = {
    "webserver_num_threads": int(os.getenv('NPDC_WEBSERVER_NUM_THREADS', 4)),
    "webserver_port": os.getenv('NPDC_GUNICORN_PORT'),
    "blastserver_num_threads": int(os.getenv('BLASTSERVER_NUM_THREADS', 4)),
    "blastserver_ram_size_gb": int(os.getenv('BLASTSERVER_MEM_GB', 8)),
    "blastserver_use_srun": bool(int(os.getenv('BLASTSERVER_USE_SRUN', 0))),
    "downloadserver_num_threads": int(os.getenv('DOWNLOADSERVER_NUM_THREADS', 4)),
    "downloadserver_use_srun": bool(int(os.getenv('DOWNLOADSERVER_USE_SRUN', 0))),
}
