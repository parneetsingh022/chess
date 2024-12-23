import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "This update introduces advanced game mechanics for better gameplay experience and fixes critical bugs to ensure rules are strictly followed.",
    "features": [
        "Checkmate: The game now detects checks and checkmates.",
        "Movements: The game now only allows moves that eliminate check when the king is under threat.",
        "Menu Logo: The game now displays a logo on the menu screen.",
    ],
    "bug-fix": [
        "Reset button: The reset button now resets the game only when the game is in progress.",
        "Castling: Fixed an issue where castling was incorrectly allowed when the king was under check or when a piece could attack the squares the king passes through during castling.",
    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)