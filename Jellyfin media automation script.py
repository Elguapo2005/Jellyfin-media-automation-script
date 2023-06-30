 import os
import requests
import schedule
import shutil
import time
import logging
import re
import json
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Configuration
config = {
    "jellyfin_url": "http://localhost:8096",
    "api_key": "",
    "user_id": "",
    "backup_folder_path": "/path/to/backup/folder/",
    "excluded_libraries": [],
    "supported_formats": [".mkv", ".mp4", ".mp3", ".wav", ".flac", ".aac", ".avi", ".mov"]
}

# Global variables
is_paused = False

def validate_config():
    """ Validates the configuration to ensure all required fields are present and have valid values. """
    required_fields = ["jellyfin_url", "api_key", "user_id", "backup_folder_path"]
    for field in required_fields:
        if field not in config or not config[field]:
            raise ValueError(f"Invalid configuration: '{field}' is missing or has an empty value.")

def fetch_data(url: str, params: Dict = None) -> List[Dict]:
    """ Fetches data from the provided URL. """
    headers = {"Authorization": f"Bearer {config['api_key']}"}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return []
    return response.json()

def fetch_libraries() -> List[Dict]:
    """ Fetches the list of libraries from Jellyfin. """
    url = f"{config['jellyfin_url']}/Users/{config['user_id']}/Items"
    params = {
        "Recursive": True,
        "IncludeItemTypes": "Library",
        "Fields": "BasicSyncInfo"
    }
    return fetch_data(url, params)

def move_tv_show_files(library_id):
    """ Move all the watched TV show episodes for a given library to the backup folder. """
    validate_config()
    watched_items = fetch_watched_items(library_id)
    seasons = fetch_seasons(library_id)
    watched_seasons = set()

    # Determine the watched seasons
    for item in watched_items:
        if item["Type"] == "Episode":
            watched_seasons.add(item["ParentIndexNumber"])

    # Check if all seasons have been watched
    if len(watched_seasons) != len(seasons):
        logging.info("Not all seasons have been watched for this TV show. Skipping backup.")
        return

    for item in watched_items:
        if is_paused:
            logging.info("Backup process is paused. Resuming in 5 minutes...")
            time.sleep(300)  # Pause for 5 minutes before resuming
            continue
        
        file_path = item["Path"]
        full_path = os.path.join("/home/user/videos", file_path)

        # Check if the file format is supported
        if not is_supported_format(file_path):
            logging.info(f"Skipping file '{file_path}' as it is not in a supported format.")
            continue

        # Check if the destination folder exists
        dest_folder_path = os.path.join(config["backup_folder_path"], library_id)
        if not os.path.exists(dest_folder_path):
            try:
                os.makedirs(dest_folder_path)
            except OSError as e:
                logging.error(f"Error creating destination folder: {e}")
                return

        # Check if the file is already in the destination folder
        dest_file_path = os.path.join(dest_folder_path, os.path.basename(file_path))
        if os.path.exists(dest_file_path):
            logging.info(f"File already exists in the destination folder: {dest_file_path}")
            return

        # Move the file
        try:
            shutil.move(full_path, dest_file_path)
        except shutil.Error as e:
            logging.error(f"Error moving file: {e}")
            raise

        # Remove the file from the previous library
        remove_from_library(item)

def move_movie_files(library_id):
    """ Move the watched movie file along with its containing folder for a given library to the backup folder. """
    validate_config()
    watched_items = fetch_watched_items(library_id)

    for item in watched_items:
        if is_paused:
            logging.info("Backup process is paused. Resuming in 5 minutes...")
            time.sleep(300)  # Pause for 5 minutes before resuming
            continue
        
        file_path = item["Path"]
        full_path = os.path.join("/home/user/videos", file_path)

        # Check if the file format is supported
        if not is_supported_format(file_path):
            logging.info(f"Skipping file '{file_path}' as it is not in a supported format.")
            continue

        # Check if the destination folder exists
        dest_folder_path = os.path.join(config["backup_folder_path"], library_id)
        if not os.path.exists(dest_folder_path):
            try:
                os.makedirs(dest_folder_path)
            except OSError as e:
                logging.error(f"Error creating destination folder: {e}")
                return

        # Check if the file is already in the destination folder
        dest_file_path = os.path.join(dest_folder_path, os.path.basename(file_path))
        if os.path.exists(dest_file_path):
            logging.info(f"File already exists in the destination folder: {dest_file_path}")
            return

        # Move the file along with its containing folder
        try:
            shutil.move(os.path.dirname(full_path), dest_folder_path)
        except shutil.Error as e:
            logging.error(f"Error moving file and its folder: {e}")
            raise

        # Remove the file from the previous library
        remove_from_library(item)

def remove_from_library(item):
    """ Removes the given item from the library using the Jellyfin API. """
    item_id = item["Id"]
    url = f"{config['jellyfin_url']}/Users/{config['user_id']}/Items/{item_id}"
    try:
        response = requests.delete(url, headers={"Authorization": f"Bearer {config['api_key']}"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error removing item from library: {e}")
        raise

def is_supported_format(file_path):
    """ Checks if the file format is supported for backup. """
    _, ext = os.path.splitext(file_path)
    return ext.lower() in config["supported_formats"]

if __name__ == "__main__":
    # Schedule the backup process
    libraries = fetch_libraries()
    for library in libraries:
        library_type = library["Type"]
        library_id = library["Id"]
        
        if library_type == "Movie":
            schedule.every().day.at("02:00").do(move_movie_files, library_id=library_id)  # Schedule movie backup at 2 AM
        elif library_type == "Series":
            schedule.every().day.at("07:00").do(move_tv_show_files, library_id=library_id)  # Schedule TV show backup at 7 AM
        else:
            logging.warning(f"Skipping library '{library_id}'. Unsupported library type: {library_type}")

    logging.info("Backup script is running. Press Ctrl+C to exit.")

    while True:
        schedule.run_pending()
        time.sleep(1)
