import json
from constants.version import version

build_notes = {
    "version": version,
    "description": "LAN multiplayer, consented reset, board flip for black, and new right-click board arrows with smoother rendering.",
    "features": [
        "Multiplayer: Host a game with a code on LAN and join by code; auto-discovery via UDP and TCP session.",
        "Multiplayer UX: Single Multiplayer menu with a dedicated Host/Join screen and a Waiting Room showing the room code.",
        "Random Colors: Colors are assigned randomly on connect; board flips automatically for black.",
        "Move Relay: Reliable move synchronization between peers over the LAN session.",
        "Consented Reset: Reset now requires opponent approval (request/accept/reject) with popups and a waiting indicator in multiplayer.",
        "En Passant: Added support for en passant capture in pawn movement logic.",
        "UX Improvement: Enhanced main menu buttons with animation and better look.",
        "Board Annotations: Right-click and drag to draw arrows (straight, diagonal, and knight L). Multiple arrows supported and orientation-aware.",
        "Input Change: Left-click only for selecting/moving pieces. Left-click clears all arrows; Esc/C also clear arrows.",
        "Arrow Rendering: Smooth, flicker-free previews with debounced hover and improved layering; clean arrowheads and rounded caps; seamless L-turn corners."
    ],
    "bug-fix": [
        "Eliminated arrow flicker by drawing arrows after board/pieces and updating the screen once per frame.",
        "Fixed arrowhead alignment to prevent a line protruding past the triangle tip.",
        "Smoothed L-turn arrows to avoid visible gaps at the corner."
    ]
}


# Write the build notes to release.json
with open('release.json', 'w') as json_file:
    json.dump(build_notes, json_file, indent=4)