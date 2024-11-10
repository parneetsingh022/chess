import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "This release introduces a new settings page and improves version information visibility.",
    "features": [
        "Settings Page: Added a settings page with basic settings options for better user experience.",
        "Improved Font: Updated the font to improve readability and visibility in main menu.",
        "Game Screen Update: Implemented a top navigation bar featuring a back button and a settings page access button.",
        "Visual Improvements: Chess pieces now have a more polished look and feel.",
        "Resume Option: Added an option to resume the game or start new game from the main menu."
    ],
    "bug-fix": [
        "Turn Indicator Flickering: Resolved an issue causing the turn indicator to flicker during gameplay.",
    ]
}

# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)