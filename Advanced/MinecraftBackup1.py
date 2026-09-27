import os
import json
import shutil
from datetime import datetime


# ----------- DEFAULT CONFIG -----------

DEFAULT_CONFIG_FILE = "Conf.json"

DEFAULT_MAX_BACKUPS = 10
DEFAULT_TIMESTAMP_FORMAT = "Copy.%d.%m.%Y_%H-%M-%S"
DEFAULT_LOG_FILE = "backup.log"
DEFAULT_CLI = True
DEFAULT_SUMMARY = "default"

DEFAULT_LOCATIONS = []


# ----------- LOG FUNCTION -----------

def log(level, message, log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}\n"

    with open(log_file, "a") as logfile:
        logfile.write(line)


# ----------- INITIALIZE LOG FILE -----------

def initialize_log(log_file):
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a") as logfile:
        logfile.write(
            f"\n===================== {start_time} =====================\n"
        )


# ----------- LOAD CONFIG -----------

def load_config(log_file):
    log(
        "INFO",
        f"Loading configuration file: '{DEFAULT_CONFIG_FILE}'",
        log_file
    )

    try:
        with open(DEFAULT_CONFIG_FILE, "r") as file:
            config = json.load(file)

    except FileNotFoundError:
        log(
            "ERROR",
            f"Configuration file '{DEFAULT_CONFIG_FILE}' was not found.",
            log_file
        )

        log(
            "WARN",
            "Using default configuration.",
            log_file
        )

        return {
            "max_backups": DEFAULT_MAX_BACKUPS,
            "timestamp_format": DEFAULT_TIMESTAMP_FORMAT,
            "log_file": log_file,
            "cli_enabled": DEFAULT_CLI,
            "summary": DEFAULT_SUMMARY,
            "locations": DEFAULT_LOCATIONS
        }

    except json.JSONDecodeError as e:
        log(
            "ERROR",
            f"Configuration file '{DEFAULT_CONFIG_FILE}' "
            f"contains invalid JSON: {e}",
            log_file
        )

        log(
            "WARN",
            "Using default configuration.",
            log_file
        )

        return {
            "max_backups": DEFAULT_MAX_BACKUPS,
            "timestamp_format": DEFAULT_TIMESTAMP_FORMAT,
            "log_file": log_file,
            "cli_enabled": DEFAULT_CLI,
            "summary": DEFAULT_SUMMARY,
            "locations": DEFAULT_LOCATIONS
        }

    except Exception as e:
        log(
            "ERROR",
            f"Could not read configuration file "
            f"'{DEFAULT_CONFIG_FILE}': {e}",
            log_file
        )

        log(
            "WARN",
            "Using default configuration.",
            log_file
        )

        return {
            "max_backups": DEFAULT_MAX_BACKUPS,
            "timestamp_format": DEFAULT_TIMESTAMP_FORMAT,
            "log_file": log_file,
            "cli_enabled": DEFAULT_CLI,
            "summary": DEFAULT_SUMMARY,
            "locations": DEFAULT_LOCATIONS
        }

    if not isinstance(config, dict):
        log(
            "ERROR",
            "Configuration root must be a JSON object.",
            log_file
        )

        log(
            "WARN",
            "Using default configuration.",
            log_file
        )

        return {
            "max_backups": DEFAULT_MAX_BACKUPS,
            "timestamp_format": DEFAULT_TIMESTAMP_FORMAT,
            "log_file": log_file,
            "cli_enabled": DEFAULT_CLI,
            "summary": DEFAULT_SUMMARY,
            "locations": DEFAULT_LOCATIONS
        }

    settings = config.get("Settings", {})
    locations = config.get("Locations", DEFAULT_LOCATIONS)

    if not isinstance(settings, dict):
        log(
            "ERROR",
            "'Settings' must be a JSON object.",
            log_file
        )

        settings = {}

    if not isinstance(locations, list):
        log(
            "ERROR",
            "'Locations' must be a JSON array.",
            log_file
        )

        locations = []

    configured_log_file = settings.get(
        "LogFile",
        DEFAULT_LOG_FILE
    )

    # If the config specifies another logfile,
    # continue logging to that file as well.
    if configured_log_file != log_file:
        try:
            initialize_log(configured_log_file)

            log(
                "INFO",
                f"Configuration loaded successfully from "
                f"'{DEFAULT_CONFIG_FILE}'.",
                configured_log_file
            )

            log_file = configured_log_file

        except Exception as e:
            log(
                "ERROR",
                f"Could not switch to configured log file "
                f"'{configured_log_file}': {e}",
                log_file
            )

            log(
                "WARN",
                f"Continuing to use default log file: '{log_file}'",
                log_file
            )

    else:
        log(
            "INFO",
            f"Configuration loaded successfully from "
            f"'{DEFAULT_CONFIG_FILE}'.",
            log_file
        )

    max_backups = settings.get(
        "MaxBackups",
        DEFAULT_MAX_BACKUPS
    )

    timestamp_format = settings.get(
        "TimestampFormat",
        DEFAULT_TIMESTAMP_FORMAT
    )

    cli_enabled = settings.get(
        "CLI",
        DEFAULT_CLI
    )

    summary = settings.get(
        "Summary",
        DEFAULT_SUMMARY
    )

    return {
        "max_backups": max_backups,
        "timestamp_format": timestamp_format,
        "log_file": log_file,
        "cli_enabled": cli_enabled,
        "summary": summary,
        "locations": locations
    }


# ----------- VALIDATE LOCATIONS -----------

def validate_locations(locations, log_file):
    valid_locations = []

    for index, location in enumerate(locations, start=1):

        if not isinstance(location, dict):
            log(
                "ERROR",
                f"Location #{index} is not a JSON object. Skipping.",
                log_file
            )

            continue

        required_fields = [
            "Name",
            "Path",
            "BackupDestination",
            "Worlds"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in location
        ]

        if missing_fields:
            log(
                "ERROR",
                f"Location #{index} is missing required field(s): "
                f"{', '.join(missing_fields)}. Skipping.",
                log_file
            )

            continue

        if not isinstance(location["Worlds"], list):
            log(
                "ERROR",
                f"Worlds for location '{location['Name']}' "
                "must be a JSON array. Skipping location.",
                log_file
            )

            continue

        valid_locations.append(location)

    return valid_locations


# ----------- BACKUP WORLD -----------

def backup_world(
    location,
    world,
    max_backups,
    timestamp_format,
    log_file
):
    location_name = location["Name"]
    source_path = location["Path"]
    backup_destination = location["BackupDestination"]

    backup_base_path = os.path.join(
        backup_destination,
        world
    )

    timestamp = datetime.now().strftime(timestamp_format)

    copy_folder = os.path.join(
        backup_base_path,
        timestamp
    )

    source_world_folder = os.path.join(
        source_path,
        world
    )

    backup_world_target = os.path.join(
        copy_folder,
        world
    )

    log(
        "INFO",
        f"Starting backup for world '{world}' "
        f"from location '{location_name}'",
        log_file
    )

    log(
        "DEBUG",
        f"Source: {source_world_folder}",
        log_file
    )

    log(
        "DEBUG",
        f"Destination: {backup_world_target}",
        log_file
    )

    if not os.path.exists(source_world_folder):
        log(
            "ERROR",
            f"Source world folder does not exist: "
            f"{source_world_folder}",
            log_file
        )

        return False

    session_file = os.path.join(
        source_world_folder,
        "session.lock"
    )

    if os.path.exists(session_file):
        log(
            "WARN",
            f"session.lock detected for world '{world}'. "
            "Minecraft may currently be running.",
            log_file
        )

    try:
        os.makedirs(
            copy_folder,
            exist_ok=True
        )

        log(
            "DEBUG",
            f"Created backup folder: {copy_folder}",
            log_file
        )

    except Exception as e:
        log(
            "ERROR",
            f"Could not create backup folder "
            f"'{copy_folder}': {e}",
            log_file
        )

        return False

    start_backup_time = datetime.now()

    try:
        shutil.copytree(
            source_world_folder,
            backup_world_target,
            dirs_exist_ok=True
        )

        duration = datetime.now() - start_backup_time

        log(
            "INFO",
            f"Backup SUCCESS for world '{world}' "
            f"in {str(duration).split('.')[0]}",
            log_file
        )

        return True

    except Exception as e:
        duration = datetime.now() - start_backup_time

        log(
            "ERROR",
            f"Backup FAILURE for world '{world}' "
            f"after {str(duration).split('.')[0]}: {e}",
            log_file
        )

        if os.path.exists(copy_folder):
            try:
                shutil.rmtree(copy_folder)

                log(
                    "INFO",
                    f"Incomplete backup removed: {copy_folder}",
                    log_file
                )

            except Exception as e2:
                log(
                    "ERROR",
                    f"Failed to remove incomplete backup "
                    f"'{copy_folder}': {e2}",
                    log_file
                )

        return False


# ----------- DELETE OLD BACKUPS -----------

def cleanup_old_backups(
    backup_destination,
    world,
    max_backups,
    log_file
):
    backup_base_path = os.path.join(
        backup_destination,
        world
    )

    if not os.path.exists(backup_base_path):
        log(
            "DEBUG",
            f"No backup directory found for world '{world}'. "
            "Skipping cleanup.",
            log_file
        )

        return

    copy_folders = [
        folder
        for folder in os.listdir(backup_base_path)
        if folder.startswith("Copy")
        and os.path.isdir(
            os.path.join(
                backup_base_path,
                folder
            )
        )
    ]

    copy_folders.sort(
        key=lambda name: os.path.getctime(
            os.path.join(
                backup_base_path,
                name
            )
        )
    )

    log(
        "DEBUG",
        f"Found {len(copy_folders)} backup(s) "
        f"for world '{world}'.",
        log_file
    )

    while len(copy_folders) > max_backups:
        oldest = copy_folders.pop(0)

        folder_path = os.path.join(
            backup_base_path,
            oldest
        )

        try:
            shutil.rmtree(folder_path)

            log(
                "INFO",
                f"Deleted old backup: {folder_path}",
                log_file
            )

        except Exception as e:
            log(
                "ERROR",
                f"Failed to delete old backup "
                f"'{folder_path}': {e}",
                log_file
            )


# ----------- MAIN -----------

def main():
    # The default logfile is needed before Conf.json
    # can tell us which logfile to use.
    log_file = DEFAULT_LOG_FILE

    initialize_log(log_file)

    log(
        "INFO",
        "Backup script started.",
        log_file
    )

    config = load_config(log_file)

    # The config may have supplied a different logfile.
    log_file = config["log_file"]

    log(
        "DEBUG",
        f"Max backups: {config['max_backups']}",
        log_file
    )

    log(
        "DEBUG",
        f"Timestamp format: {config['timestamp_format']}",
        log_file
    )

    log(
        "DEBUG",
        f"CLI enabled: {config['cli_enabled']}",
        log_file
    )

    log(
        "DEBUG",
        f"Summary mode: {config['summary']}",
        log_file
    )

    locations = validate_locations(
        config["locations"],
        log_file
    )

    if not locations:
        log(
            "WARN",
            "No valid backup locations are configured.",
            log_file
        )

        log(
            "WARN",
            "Nothing will be backed up.",
            log_file
        )

    else:
        log(
            "INFO",
            f"Loaded {len(locations)} valid backup location(s).",
            log_file
        )

    backup_failed = False
    backups_attempted = 0

    for location in locations:
        location_name = location["Name"]
        location_path = location["Path"]
        backup_destination = location["BackupDestination"]
        worlds = location["Worlds"]

        log(
            "INFO",
            f"Processing location: '{location_name}'",
            log_file
        )

        log(
            "DEBUG",
            f"Location path: {location_path}",
            log_file
        )

        log(
            "DEBUG",
            f"Backup destination: {backup_destination}",
            log_file
        )

        log(
            "DEBUG",
            f"Configured worlds: {worlds}",
            log_file
        )

        for world in worlds:

            if not world:
                log(
                    "WARN",
                    f"Empty world entry found in location "
                    f"'{location_name}'. Skipping.",
                    log_file
                )

                continue

            backups_attempted += 1

            success = backup_world(
                location,
                world,
                config["max_backups"],
                config["timestamp_format"],
                log_file
            )

            if not success:
                backup_failed = True

            cleanup_old_backups(
                backup_destination,
                world,
                config["max_backups"],
                log_file
            )

    if backups_attempted == 0:
        log(
            "WARN",
            "No worlds were selected for backup.",
            log_file
        )

    elif backup_failed:
        log(
            "WARN",
            "Backup session finished with one or more failures.",
            log_file
        )

    else:
        log(
            "INFO",
            "Backup session finished successfully.",
            log_file
        )

    with open(log_file, "a") as logfile:
        logfile.write(
            "===============================================================\n"
        )


if __name__ == "__main__":
    main()