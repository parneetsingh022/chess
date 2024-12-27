import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
        "Resize Option: Added option to resize window and choose between small, large and medium sizes",
    ],
    "bug-fix": [
        
    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)