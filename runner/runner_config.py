#!/usr/bin/env python3
import os

conf = {
	"webserver_num_threads": 4,
	"webserver_port": os.getenv('NPDC_GUNICORN_PORT'),
	"blastserver_num_threads": 4,
	"blastserver_ram_size_gb": 8,
	"blastserver_use_srun": False,
	"downloadserver_num_threads": 4,
	"downloadserver_use_srun": False,
}
