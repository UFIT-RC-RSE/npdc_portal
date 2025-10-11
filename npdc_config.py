#!/usr/bin/env python3
import os

conf = {
    "blast_genome_limit": int(os.getenv('BLAST_GENOME_LIMIT', 1000)),
    "MAIL_SERVER": os.getenv('MAIL_SERVER'),
    "MAIL_PORT": int(os.getenv('MAIL_PORT')),
    "MAIL_USERNAME": os.getenv('MAIL_USERNAME'),
    "MAIL_PASSWORD": os.getenv('MAIL_PASSWORD'),
    "MAIL_USE_TLS": bool(int(os.getenv('MAIL_USE_TLS'))),
    "MAIL_USE_SSL": bool(int(os.getenv('MAIL_USE_SSL'))),
    "MAIL_SEND_AS": os.getenv('MAIL_SEND_AS'),
    "MAIL_SEND_FEEDBACKS_TO": os.getenv('MAIL_SEND_FEEDBACKS_TO'),
    "MAIL_SEND_ORDER_TO": os.getenv('MAIL_SEND_ORDER_TO')
}
