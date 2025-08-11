import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "LAN multiplayer with host/join by code, consented reset flow, board flip for black, and stability fixes.",
    "features": [
         "Multiplayer: Host a game with a code on LAN and join by code; auto-discovery via UDP and TCP session.",
         "Multiplayer UX: Single Multiplayer menu with a dedicated Host/Join screen and a Waiting Room showing the room code.",
         "Random Colors: Colors are assigned randomly on connect; board flips automatically for black.",
         "Move Relay: Reliable move synchronization between peers over the LAN session.",
         "Consented Reset: Reset now requires opponent approval (request/accept/reject) with popups and a waiting indicator in multiplayer.",
         "En Passant: Added support for en passant capture in pawn movement logic.",
         "UX Improvement: Enhanced main menu buttons with animation and better look."
    ],
    "bug-fix": [

    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)