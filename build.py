import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
        "Checkmate: The game now detects checks and checkmates.",
    ],
    "bug-fix": [
        "Reset button: The reset button now resets the game only when the game is in progress.",
    ]
}

# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)