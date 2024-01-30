from logging import getLogger
import logging
import os
from subprocess import Popen, PIPE, STDOUT
import sys
from alfalfa_client import AlfalfaClient
from requests import HTTPError
from uuid import UUID
from asyncio import run, create_task
import asyncio

def get_site_id(client: AlfalfaClient, alfalfa_site: str):
    try:
        return client.get_alias(alfalfa_site)
    except HTTPError:
        if is_valid_uuid(alfalfa_site):
            return alfalfa_site
        else:
            return None

def is_valid_uuid(uuid_str: str, version="4"):
    try:
        uuid_obj = UUID(uuid_str, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str

def is_process_alive(process: Popen):
    if process:
        process.poll()
        return process.returncode == None
    return False


async def main_loop(host: str, alfalfa_site: str, command: str):

    logger = getLogger("ALFALFA WATCHDOG")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    client = AlfalfaClient(host)
    old_site_id = None
    child_process:Popen = None


    while True:
        try:
            site_id = get_site_id(client, alfalfa_site)

            if site_id != None and (site_id != old_site_id or not is_process_alive(child_process)):
                logger.info(f"Found new site with ID: '{site_id}'")
                status = client.status(site_id)
                logger.info(f"Site status is: '{status}'")
                if status == "RUNNING":
                    if is_process_alive(child_process):
                        logger.info(f"Killing old child process: '{child_process.pid}'")
                        child_process.kill()
                    elif child_process != None:
                        logger.info(f"Process '{child_process.pid}' died, restarting process")
                    child_process = Popen(["python", "-u", command, host, site_id])
                    logger.info(f"Spawned new child process: '{child_process.pid}'")
                    old_site_id = site_id

            if site_id and is_process_alive(child_process) and client.status(site_id) != "RUNNING":
                logger.info(f"Killing old child process: '{child_process.pid}'")
                child_process.kill()

            elif site_id == None:
                logger.info(f"No site found with identifier: '{alfalfa_site}'")

        except Exception as e:
            logger.error(e)

        await asyncio.sleep(5)

if __name__ == "__main__":
    alfalfa_site = os.getenv('ALFALFA_SITE')
    host = os.getenv('ALFALFA_HOST')
    command = sys.argv[1]
    run(main_loop(host, alfalfa_site, command))

