import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
        "Pawn Promotion: Users can now promote their pawn to a desired piece upon reaching the end of the board.",
        "Default Player: Added option to switch between white and black as the default player in settings.",
    ],
    "bug-fix": [
        "Check: fixed a bug where kings check is displayed at wrong position when default player is black."
    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)