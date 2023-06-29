# Jellyfin media automation script

![License](https://img.shields.io/badge/license-MIT-blue.svg)

This is a Python script that automates the process of moving watched TV show episodes from a Jellyfin media server to a backup storage location, helping to save space on the primary storage device. It provides a convenient way to organize and archive watched TV shows while freeing up space on the original server.

## Features

- Automatically detects and moves watched TV show episodes from a Jellyfin library.
- Supports the option to move entire TV shows once all seasons are watched.
- Excludes specific libraries from the backup process.
- Checks for supported file formats before moving the files.
- Schedule the backup process at specific times using the `schedule` library.

## Usage

1. Ensure you have Python installed on your system (version X.X or higher).
2. Clone or download this repository to your local machine.
3. Update the configuration in the script (`config` dictionary) with your Jellyfin server details and backup folder path.
4. Install the required dependencies by running the command: `pip install -r requirements.txt`
5. Run the script using the command: `python Jellyfin media automation script.py`
6. The script will run at the scheduled times (02:00 and 07:00 by default) and move watched media(movies, music, TV show episodes) to the backup folder u choose.



Getting Started:

Configure the script by providing the Jellyfin server URL, API key, user ID, backup folder path, excluded libraries (if any), and supported file formats.
Set up the desired schedule using the powerful schedule library to automate the backup process at your preferred times.
Run the script, sit back, and relax as it takes care of the entire backup process, intelligently moving watched items once all seasons of a TV show have been completed.
Enjoy enhanced storage management, improved performance, and peace of mind knowing that your watched items are safely backed up on a secondary storage device.

## License

This project is licensed under the [MIT License](LICENSE).
