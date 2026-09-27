import os
import json
import shutil

from datetime import datetime


# ----------- DEFAULT CONFIG -----------

defaultMaxMinecraftSaveBackups = 10
defaultBackupDestination = "Z:\\minecraft\\BackupWorlds"
defaultMinecraftSavePath = "C:\\Users\\<USER>\\AppData\\Roaming\\.minecraft\\saves"
defaultTimestampFormat = "Copy.%d.%m.%Y"
defaultLogFile = "backup.log"
defaultWorlds = ["main survival"]
current_run_log = []


# ----------- LOG FUNCTION -----------

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message} \n"

    with open(log_file, "a") as logfile:
        logfile.write(line)

    current_run_log.append(line)


# ----------- TAIL FUNCTION -----------

def show_tail(lines):
    try:
        with open(log_file, "r") as logfile:
            last_lines = logfile.readlines()[-lines:]

        print("\n" + "".join(last_lines))

    except Exception as e:
        print(f"Could not read log file: {e}")


# ----------- INITIALIZE LOG FILE -----------

log_file = defaultLogFile

start_time_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(log_file, "a") as logfile:
    logfile.write(
        f"\n===================== {start_time_log} =====================\n"
    )

log(f"Backup script started.\n")


# ----------- LOAD CONFIG.JSON -----------

try:
    with open("ConfigLinux.json", "r") as file:
        config = json.load(file)

    params = {
        item["Name"]: item["DefaultValue"]
        for item in config["Params"]
    }

    worlds_to_backup = params.get("Worlds", defaultWorlds)

    defaultMaxMinecraftSaveBackups = params.get(
        "Length",
        defaultMaxMinecraftSaveBackups
    )

    backup_destination = params.get(
        "BackupDestination",
        defaultBackupDestination
    )

    minecraft_save_path = params.get(
        "MinecraftSavePath",
        defaultMinecraftSavePath
    )

    timestamp_format = params.get(
        "TimestampFormat",
        defaultTimestampFormat
    )

    log_file = params.get(
        "LogFile",
        defaultLogFile
    )

    log(
        f"SUCCESS: Config.json loaded: "
        f"Worlds={worlds_to_backup}, "
        f"MaxBackups={defaultMaxMinecraftSaveBackups}, "
        f"BackupDestination='{backup_destination}', "
        f"MinecraftSavePath='{minecraft_save_path}', "
        f"TimestampFormat='{timestamp_format}', "
        f"LogFile='{log_file}'\n"
    )

except Exception as e:
    log(f"ERROR: Config.json could not be read: {e}")
    log("Using default config values.\n")

    worlds_to_backup = defaultWorlds
    backup_destination = defaultBackupDestination
    minecraft_save_path = defaultMinecraftSavePath
    timestamp_format = defaultTimestampFormat
    log_file = defaultLogFile


# ----------- BACKUP LOOP -----------

backup_failed = False

for world in worlds_to_backup:

    backup_base_path = os.path.join(
        backup_destination,
        world
    )

    today = datetime.today().strftime(timestamp_format)

    copy_folder = os.path.join(
        backup_base_path,
        today
    )

    source_world_folder = os.path.join(
        minecraft_save_path,
        world
    )

    backup_world_target = os.path.join(
        copy_folder,
        world
    )

    log(f"Starting backup for world: '{world}'")

    os.makedirs(
        copy_folder,
        exist_ok=True
    )

    log(f"Created backup folder: {copy_folder}")

    start_backup_time = datetime.now()

    try:
        shutil.copytree(
            source_world_folder,
            backup_world_target,
            dirs_exist_ok=True
        )

        duration = datetime.now() - start_backup_time

        log(
            f"Backup SUCCESS for world '{world}' "
            f"in {str(duration).split('.')[0]}\n"
        )

    except Exception as e:
        backup_failed = True

        duration = datetime.now() - start_backup_time

        log(
            f"Backup FAILURE for world '{world}' - {e}"
        )

        session_file = os.path.join(
            source_world_folder,
            "session.lock"
        )

        if os.path.exists(session_file):
            log(
                "FAILURE reason: "
                "Minecraft appears to be running."
            )

        elif not os.path.exists(backup_world_target):
            log(
                "FAILURE reason: "
                "Source world folder does not exist."
            )

        else:
            log(
                "FAILURE reason: Unknown."
            )

        if os.path.exists(copy_folder):
            try:
                shutil.rmtree(copy_folder)

                log(
                    f"Incomplete backup removed: "
                    f"{copy_folder}\n"
                )

            except Exception as e2:
                log(
                    f"Failed to remove incomplete backup: "
                    f"{e2}\n"
                )

    # ----------- DELETE OLD BACKUPS -----------

    if os.path.exists(backup_base_path):

        copy_folders = [
            f
            for f in os.listdir(backup_base_path)
            if f.startswith("Copy")
            and os.path.isdir(
                os.path.join(
                    backup_base_path,
                    f
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

        while len(copy_folders) > defaultMaxMinecraftSaveBackups:

            oldest = copy_folders.pop(0)

            folder_path = os.path.join(
                backup_base_path,
                oldest
            )

            try:
                shutil.rmtree(folder_path)

                log(
                    f"Deleted old backup: "
                    f"{folder_path}"
                )

            except Exception as e:
                log(
                    f"Failed to delete old backup "
                    f"{folder_path}: {e}"
                )


# ----------- FINISH -----------

log("Backup script finished.")

with open(log_file, "a") as logfile:
    logfile.write(
        "===============================================================\n"
    )


print("\n" + "".join(current_run_log))