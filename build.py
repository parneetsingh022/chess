import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
        "Resize Option: Added option to resize window and choose between small, large and medium sizes",
        "Last Move: Now a grey box is displayed around the last moved piece to improve experience."
    ],
    "bug-fix": [
        "Game crash: Fixed a bug which causes game to crash.",
    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)