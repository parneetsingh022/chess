import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
    ],
    "bug-fix": [
        "Reset Button: Resolved the issue where players could reset the game even when it was already reset or there was nothing to reset.",
    ]
}

# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)