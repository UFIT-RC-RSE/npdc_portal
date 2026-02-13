#!/usr/bin/env python3

from os import path, listdir, getenv
from subprocess import run, DEVNULL
from shutil import copytree
from tempfile import TemporaryDirectory
from sys import exit, argv
from sqlite3 import connect
from time import sleep
from datetime import datetime
from multiprocessing import cpu_count
import pandas as pd
import numpy as np
import subprocess
import json

def fetch_pending_jobs(jobs_db):
    with connect(jobs_db) as con:
        cur = con.cursor()
        return [(row[0], row[1]) for row in cur.execute((
            "select id, refseq"
            " from jobs"
            " where status=0"
            " order by submitted asc"
        )).fetchall()]



def deploy_jobs(pending, jobs_db, npdc_db, instance_folder, num_threads, ram_size_gb, use_srun, num_genomes_limit):
    for job_id, refseq in pending:
        if refseq==1:
            portalname="npdc_portal_refseq.dmnd"
            npdc_db = str(npdc_db).replace("npdc_portal.db", "npdc_portal_searchable_refseq.db")
        else:
            portalname="npdc_portal.dmnd"
        print("PROCESSING: job#{}".format(job_id))
        # update status to "PROCESSING"
        with connect(jobs_db) as con:
            cur = con.cursor()
            cur.execute((
                "update jobs"
                " set status=?, started=?"
                " where id=?"
            ), (1, datetime.now(), job_id))
            con.commit()

        with TemporaryDirectory(dir=path.join('/npdc_portal', 'instance', 'tmp')) as temp_dir:
            query_proteins = pd.read_sql((
                    "select id,aa_seq from query_proteins"
                    " where jobid=?"
                    ),
                con=connect(jobs_db),
                params=(job_id,)
                )

            # create fasta input
            fasta_input_path = path.join(temp_dir, "input.fasta")
            with open(fasta_input_path, "w") as oo:
                for idx, row in query_proteins.iterrows():
                    oo.write(">{}\n{}\n".format(
                        row["id"],
                        row["aa_seq"]
                        ))

            # run DIAMOND BLASTP
            blast_columns = "qseqid sseqid qstart qend sstart send evalue bitscore pident slen qlen"
            diamond_blast_db_path = path.join(
                getenv('INSTANCE_GLOBAL_PATH'),
                "db_data",
                portalname
            )
            blast_output_path = path.join(temp_dir, "output.txt")
            blast_tmpdir = path.join(getenv('INSTANCE_GLOBAL_PATH'), 'tmp')
            try:
                cmd = "{}{} blastp --verbose -t {} -d {} -q {} -e 1e-10 -o {} -f 6 {} --ignore-warnings --query-cover 80 --id 40 -k 999999 -p {} -b{:.1f} -c1".format(
                    "srun --chdir {} -c {} -n 1 --mem={}G -t 1000 ".format(getenv('INSTANCE_GLOBAL_PATH'), num_threads, ram_size_gb) if use_srun else "",
                    getenv('DIAMOND_GLOBAL_PATH'),
                    blast_tmpdir,
                    diamond_blast_db_path.replace(path.join('/npdc_portal', 'instance'), getenv('INSTANCE_GLOBAL_PATH')),
                    fasta_input_path.replace(path.join('/npdc_portal', 'instance'), getenv('INSTANCE_GLOBAL_PATH')),
                    blast_output_path.replace(path.join('/npdc_portal', 'instance'), getenv('INSTANCE_GLOBAL_PATH')),
                    blast_columns,
                    num_threads,
                    max(1, ram_size_gb / 7)
                )
                subprocess.check_output(
                    cmd, shell=True
                )
                status = 2
            except subprocess.CalledProcessError as e:
                status = -1

            if status != -1 and (path.getsize(blast_output_path) > 0): # else, no hit's produced
                # process BLAST result
                blast_result = pd.read_csv(
                    blast_output_path, sep="\t", header=None
                )
                blast_result.columns = blast_columns.split(" ")
                blast_result = blast_result.sort_values(by=["qseqid", "bitscore"], ascending=False)
                # fetch bgc_id and genome_id for the proteins
                all_target_cds_ids = [int(cds_id) for cds_id in blast_result["sseqid"].unique()]
                cds_to_genome_id = pd.read_sql((
                    "select id as cds_id, genome_id from cds where id in ({})"
                ).format(
                    ",".join(["?"]*len(all_target_cds_ids))
                ), connect(npdc_db), params=tuple([*all_target_cds_ids]))
                if cds_to_genome_id.shape[0] > 0:
                    cds_to_genome_id = cds_to_genome_id.groupby("cds_id").apply(lambda x: x.iloc[0])["genome_id"].to_dict()
                else:
                    cds_to_genome_id = {}
                cds_to_bgc_id = pd.read_sql((
                    "select cds_id, bgc_id from cds_bgc_map where cds_id in ({})"
                ).format(
                    ",".join(["?"]*len(all_target_cds_ids))
                ), connect(npdc_db), params=(tuple([*all_target_cds_ids])))
                if cds_to_bgc_id.shape[0] > 0:
                    cds_to_bgc_id = cds_to_bgc_id.groupby("cds_id").apply(lambda x: x.iloc[0])["bgc_id"].to_dict()
                else:
                    cds_to_bgc_id = {}

                blast_result = pd.DataFrame({
                    "query_prot_id": blast_result["qseqid"],
                    "target_cds_id": blast_result["sseqid"],
                    "target_bgc_id": blast_result["sseqid"].map(lambda x: cds_to_bgc_id.get(int(x), -1)),
                    "target_genome_id": blast_result["sseqid"].map(lambda x: cds_to_genome_id[int(x)]),
                    "query_start": blast_result["qstart"],
                    "query_end": blast_result["qend"],
                    "query_cov": abs(blast_result["qend"] - blast_result["qstart"]) / blast_result["qlen"] * 100,
                    "target_start": blast_result["sstart"],
                    "target_end": blast_result["send"],
                    "target_cov": abs(blast_result["send"] - blast_result["sstart"]) / blast_result["slen"] * 100,
                    "evalue": blast_result["evalue"],
                    "bitscore": blast_result["bitscore"],
                    "pct_identity": blast_result["pident"]
                })

                # limit only to x best hit genomes
                per_genome = blast_result.groupby("target_genome_id").apply(
                    lambda rows: pd.Series({
                        "avg_score": rows["bitscore"].mean(),
                        "unique_query_counts": rows["query_prot_id"].nunique()
                    })
                ).sort_values(by=["unique_query_counts", "avg_score"], ascending=False).iloc[:num_genomes_limit]
                blast_result = blast_result[blast_result["target_genome_id"].isin(per_genome.index)]

                # insert into db
                blast_result.to_sql("blast_hits", connect(jobs_db, timeout=60), index=False, if_exists="append")
                status = 2


            # update status
            with connect(jobs_db) as con:
                cur = con.cursor()
                cur.execute((
                    "update jobs"
                    " set status=?, finished=?"
                    " where id=?"
                ), (status, datetime.now(), job_id))
                con.commit()

            print("COMPLETED: job#{}".format(job_id))

    return 0


def main():

    num_threads = int(argv[1])
    ram_size_gb = int(argv[2])
    use_srun = False
    if len(argv) > 3:
        use_srun = int(argv[3]) == 1

    instance_folder = path.join(
        path.dirname(__file__),
        "..",
        "instance"
    )

    jobs_db = path.join(instance_folder, "queries.db")
    npdc_db = path.join(instance_folder, "db_data", "npdc_portal.db")
    if not path.exists(jobs_db):
        print("database is not up-to-date, please run init_db.py first!!")
        return(1)

    # fetch jobs in process that got interrupted previously, re-set to pending
    with connect(jobs_db) as con:
        cur = con.cursor()
        status_enums = pd.read_sql(("select * from status_enum where 1"), con)
        status_enums.index = status_enums["name"]
        status_enums = status_enums["code"].to_dict()
        cur.execute(("update jobs set status=? where status=?"), (
            status_enums["PENDING"],
            status_enums["PROCESSING"]
        ))


    print("workers are running...")

    # get the genome limit for BLAST results
    blast_genome_limit = int(getenv('BLAST_GENOME_LIMIT'))

    while(True):
        pending = fetch_pending_jobs(jobs_db)
        if len(pending) > 0:
            print("deploying {} jobs...".format(
                len(pending)
            ))
            deploy_jobs(pending, jobs_db, npdc_db, instance_folder, num_threads, ram_size_gb, use_srun, blast_genome_limit)

        sleep(5)

    return 0


if __name__ == '__main__':
    exit(main())
