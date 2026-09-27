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
DEFAULT_SUMMARY = True
DEFAULT_SUMMARY_FILE = "Summary.txt"

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


# ----------- INITIALIZE SUMMARY FILE -----------

def initialize_summary_file(summary_file):
    with open(summary_file, "a") as summary:
        summary.write(
            "\n"
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
            "summary_file": DEFAULT_SUMMARY_FILE,
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
            "summary_file": DEFAULT_SUMMARY_FILE,
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
            "summary_file": DEFAULT_SUMMARY_FILE,
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
            "summary_file": DEFAULT_SUMMARY_FILE,
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

    summary_file = settings.get(
        "SummaryFile",
        DEFAULT_SUMMARY_FILE
    )

    if not isinstance(summary, bool):
        log(
            "ERROR",
            "'Summary' must be true or false. "
            "Using default value.",
            log_file
        )

        summary = DEFAULT_SUMMARY

    if not isinstance(summary_file, str) or not summary_file.strip():
        log(
            "ERROR",
            "'SummaryFile' must be a non-empty string. "
            "Using default value.",
            log_file
        )

        summary_file = DEFAULT_SUMMARY_FILE

    return {
        "max_backups": max_backups,
        "timestamp_format": timestamp_format,
        "log_file": log_file,
        "cli_enabled": cli_enabled,
        "summary": summary,
        "summary_file": summary_file,
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
        error_message = (
            f"Source world folder does not exist: "
            f"{source_world_folder}"
        )

        log(
            "ERROR",
            error_message,
            log_file
        )

        return {
            "success": False,
            "location": location_name,
            "world": world,
            "source": source_world_folder,
            "destination": backup_world_target,
            "duration": "00:00:00",
            "error": "Source world folder does not exist."
        }

    session_file = os.path.join(
        source_world_folder,
        "session.lock"
    )

    session_lock_detected = os.path.exists(session_file)

    if session_lock_detected:
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
        error_message = (
            f"Could not create backup folder "
            f"'{copy_folder}': {e}"
        )

        log(
            "ERROR",
            error_message,
            log_file
        )

        return {
            "success": False,
            "location": location_name,
            "world": world,
            "source": source_world_folder,
            "destination": backup_world_target,
            "duration": "00:00:00",
            "error": f"Could not create backup folder: {e}"
        }

    start_backup_time = datetime.now()

    try:
        shutil.copytree(
            source_world_folder,
            backup_world_target,
            dirs_exist_ok=True
        )

        duration = datetime.now() - start_backup_time
        duration_text = str(duration).split(".")[0]

        log(
            "INFO",
            f"Backup SUCCESS for world '{world}' "
            f"in {duration_text}",
            log_file
        )

        return {
            "success": True,
            "location": location_name,
            "world": world,
            "source": source_world_folder,
            "destination": backup_world_target,
            "duration": duration_text,
            "error": None,
            "session_lock": session_lock_detected
        }

    except Exception as e:
        duration = datetime.now() - start_backup_time
        duration_text = str(duration).split(".")[0]

        error_message = str(e)

        log(
            "ERROR",
            f"Backup FAILURE for world '{world}' "
            f"after {duration_text}: {error_message}",
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

        return {
            "success": False,
            "location": location_name,
            "world": world,
            "source": source_world_folder,
            "destination": backup_world_target,
            "duration": duration_text,
            "error": error_message,
            "session_lock": session_lock_detected
        }


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

    cleanup_result = {
        "deleted": 0,
        "failed": 0
    }

    if not os.path.exists(backup_base_path):
        log(
            "DEBUG",
            f"No backup directory found for world '{world}'. "
            "Skipping cleanup.",
            log_file
        )

        return cleanup_result

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

            cleanup_result["deleted"] += 1

            log(
                "INFO",
                f"Deleted old backup: {folder_path}",
                log_file
            )

        except Exception as e:
            cleanup_result["failed"] += 1

            log(
                "ERROR",
                f"Failed to delete old backup "
                f"'{folder_path}': {e}",
                log_file
            )

    return cleanup_result


# ----------- CREATE SUMMARY -----------

def create_summary(
    session_start,
    locations,
    total_worlds,
    skipped_worlds,
    backup_results,
    cleanup_deleted,
    cleanup_failed
):
    session_end = datetime.now()

    duration = session_end - session_start
    duration_text = str(duration).split(".")[0]

    successful_backups = sum(
        1
        for result in backup_results
        if result["success"]
    )

    failed_backups = sum(
        1
        for result in backup_results
        if not result["success"]
    )

    session_locks = sum(
        1
        for result in backup_results
        if result.get("session_lock", False)
    )

    if failed_backups > 0 or cleanup_failed > 0:
        overall_result = "FAILED"

    elif successful_backups > 0:
        overall_result = "SUCCESS"

    else:
        overall_result = "NOTHING TO DO"

    lines = [
        "",
        "===================== BACKUP SUMMARY =====================",
        "",
        "SESSION",
        "-----------------------------------------------------------",
        f"Started:               {session_start.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Finished:              {session_end.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total duration:        {duration_text}",
        "",
        "RESULT",
        "-----------------------------------------------------------",
        f"Locations processed:   {len(locations)}",
        f"Worlds configured:     {total_worlds + skipped_worlds}",
        f"Worlds attempted:      {len(backup_results)}",
        f"Worlds skipped:        {skipped_worlds}",
        "",
        f"Successful backups:    {successful_backups}",
        f"Failed backups:        {failed_backups}",
        f"Overall result:        {overall_result}",
        "",
        "CLEANUP",
        "-----------------------------------------------------------",
        f"Old backups deleted:   {cleanup_deleted}",
        f"Cleanup failures:      {cleanup_failed}",
        "",
        "WARNINGS",
        "-----------------------------------------------------------",
        f"session.lock detected:  {session_locks}",
        "",
        "BACKUP RESULTS",
        "-----------------------------------------------------------"
    ]

    if not backup_results:
        lines.append(
            "No backup attempts were made."
        )

    else:
        for result in backup_results:
            if result["success"]:
                lines.extend([
                    "",
                    "[ SUCCESS ]",
                    f"Location:              {result['location']}",
                    f"World:                 {result['world']}",
                    f"Source:                {result['source']}",
                    f"Destination:           {result['destination']}",
                    f"Duration:              {result['duration']}"
                ])

                if result.get("session_lock", False):
                    lines.append(
                        "Warning:               session.lock was detected"
                    )

            else:
                lines.extend([
                    "",
                    "[ FAILED ]",
                    f"Location:              {result['location']}",
                    f"World:                 {result['world']}",
                    f"Source:                {result['source']}",
                    f"Destination:           {result['destination']}",
                    f"Duration:              {result['duration']}",
                    f"Reason:                {result['error']}"
                ])

                if result.get("session_lock", False):
                    lines.append(
                        "Warning:               session.lock was detected"
                    )

    lines.extend([
        "",
        "===========================================================",
        ""
    ])

    return "\n".join(lines)


# ----------- PRINT SUMMARY -----------

def print_summary(summary):
    print(summary)


# ----------- SAVE SUMMARY -----------

def save_summary(summary, summary_file):
    try:
        with open(summary_file, "a") as file:
            file.write(summary)

        return True

    except Exception:
        return False


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

    session_start = datetime.now()

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
        f"Summary enabled: {config['summary']}",
        log_file
    )

    log(
        "DEBUG",
        f"Summary file: {config['summary_file']}",
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

    skipped_worlds = 0
    total_worlds = 0

    backup_results = []

    cleanup_deleted = 0
    cleanup_failed = 0

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
                skipped_worlds += 1

                log(
                    "WARN",
                    f"Empty world entry found in location "
                    f"'{location_name}'. Skipping.",
                    log_file
                )

                continue

            total_worlds += 1

            result = backup_world(
                location,
                world,
                config["max_backups"],
                config["timestamp_format"],
                log_file
            )

            backup_results.append(result)

            cleanup_result = cleanup_old_backups(
                backup_destination,
                world,
                config["max_backups"],
                log_file
            )

            cleanup_deleted += cleanup_result["deleted"]
            cleanup_failed += cleanup_result["failed"]

    successful_backups = sum(
        1
        for result in backup_results
        if result["success"]
    )

    failed_backups = sum(
        1
        for result in backup_results
        if not result["success"]
    )

    if total_worlds == 0:
        log(
            "WARN",
            "No worlds were selected for backup.",
            log_file
        )

    elif failed_backups > 0:
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

    if config["summary"]:
        summary = create_summary(
            session_start,
            locations,
            total_worlds,
            skipped_worlds,
            backup_results,
            cleanup_deleted,
            cleanup_failed
        )

        print_summary(summary)

        if save_summary(
            summary,
            config["summary_file"]
        ):
            log(
                "INFO",
                f"Summary saved to '{config['summary_file']}'.",
                log_file
            )

        else:
            log(
                "ERROR",
                f"Could not save summary to "
                f"'{config['summary_file']}'.",
                log_file
            )

    with open(log_file, "a") as logfile:
        logfile.write(
            "===============================================================\n"
        )


if __name__ == "__main__":
    main()