# Minecraft World Backup Script

This project contains a Python script that automatically backs up one or multiple Minecraft worlds.  
It detects whether Minecraft is currently running, prevents corrupted backups, logs all actions, and keeps only a configurable number of backups.

---

## Features

- Backup multiple Minecraft worlds
- Detect whether Minecraft is running (via `session.lock`)
- Skip backups safely if worlds are still open
- Remove incomplete backups automatically
- Clean up old backups when exceeding the maximum count
- Fully configurable using `Config.json`
- Can be compiled into a standalone `.exe` via PyInstaller

---

## Understsanding

### 1. Understanding Config.json
Example configuration:
```
{
    "Params":[
        {
            "Name": "Worlds",
            "Type": "List",
            "DefaultValue": ["Survival Hardcore", "creative world"]
        },
        {
            "Name": "Length",
            "Type": "Integer",
            "DefaultValue": 10
        },
        {
            "Name": "BackupDestination",
            "Type": "String",
            "DefaultValue": "Z:\\minecraft\\BackupWorlds"
        },
        {
            "Name": "MinecraftSavePath",
            "Type": "String",
            "DefaultValue": "C:\\Users\\YOURNAME\\AppData\\Roaming\\.minecraft\\saves"
        },
        {
            "Name": "TimestampFormat",
            "Type": "String",
            "DefaultValue": "Copy.%d.%m.%Y"
        },
        {
            "Name": "LogFile",
            "Type": "String",
            "DefaultValue": "backup.log"
        }
    ]
}

```

### 2. Parameter Description
| Parameter             | Description                                 |
| --------------------- | ------------------------------------------- |
| **Worlds**            | A list of Minecraft world names to back up  |
| **Length**            | Maximum number of backups to keep per world |
| **BackupDestination** | Where backups will be saved                 |
| **MinecraftSavePath** | Location of the `.minecraft/saves` folder   |
| **TimestampFormat**   | How backup folders are named                |
| **LogFile**           | Log output filename                         |

### 3. Backing Up Multiple Worlds
Add your worlds inside the Worlds list:
```
"DefaultValue": ["Survival friends", "creative world", "hardcore world"]
```
The names must match the folder names inside:
```
.minecraft/saves/
```
#### Example
```
C:\Users\<USER>\AppData\Roaming\.minecraft\saves\Survival friends
C:\Users\<USER>\AppData\Roaming\.minecraft\saves\creative world
C:\Users\<USER>\AppData\Roaming\.minecraft\saves\hardcore world
```

### 4. MinecraftSavePath Setup
Each Windows user has a different username.  
Modify this line in the configuration:
```
C:\\Users\\YOURNAME\\AppData\\Roaming\\.minecraft\\saves
```
and this line in the python file:
```
13  defaultMinecraftSavePath = "C:\\Users\\<USER>\\AppData\\Roaming\\.minecraft\\saves"
```
#### Example
```
"DefaultValue": "C:\\Users\\Zevy\\AppData\\Roaming\\.minecraft\\saves"
```
and this line in the python file:
```
13  defaultMinecraftSavePath = "C:\\Users\\Zevy\\AppData\\Roaming\\.minecraft\\saves"
```
## Install PyInstaller (for building an executable)

### 5. Install PyInstaller

```bash
pip install pyinstaller
```

### 6. Navigate to the project directory
```bash
cd path/to/project
```

### 7. Build the executable

#### You can choose between:
- a version without console (recommended for normal use)
- a version with console (for debugging)

#### Without console
```bash
pyinstaller --onefile --noconsole BackupMinecraftWorlds.py
```
#### with console
```bash
pyinstaller --onefile BackupMinecraftWorlds.py
```
The compiled .exe will appear in the dist/ folder.

### 8. Copy the Config.json file
You must manually copy `Config.json` next to the executable:
```
dist/
  BackupMinecraftWorlds.exe
  Config.json
```
### 9. Running the Executable
Inside the dist/ folder:
```
BackupMinecraftWorlds.exe
Config.json
```
Double-click BackupMinecraftWorlds.exe to run the backup script.  
Make a shortcut of the .exe for easy use if you like.

### 10. Logs
All events are written to:
```
backup.log
```
This is the default log file if this configuration is untouched in Config.json

### 11. Folder structure
```
BackupMinecraftWorlds.py
BUILD.MD
Config.json
build/
dist/
    backup.log
    BackupMinecraftWorlds.exe
    Config.json
```

### 12. Backup Folder Structure
For each world, the script produces the following structure:
```
WorldName/
  Copy.01.12.2025/
    WorldName/
  Copy.02.12.2025/
  Copy.03.12.2025/
  ...
```

### 13. Automatic cleanup of old backups
The script keeps only the number of backups specified in Length.  

For example:

- If Length is set to 10, only the newest 10 backups are kept.
- Older backups are automatically deleted.
