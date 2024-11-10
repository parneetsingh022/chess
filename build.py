import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "",
    "features": [
        
    ],
    "bug-fix": [
        "Menu button glitch: Fixed an issue where the \"Resume\" and \"Start New Game\" buttons appeared after selecting and deselecting a piece without making a move."
    ]
}

# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)