import socket
import json
import random
from typing import Optional, Tuple


BROADCAST_PORT = 54000
TCP_PORT = 54010
BUFFER_SIZE = 4096


def _get_local_broadcast() -> str:
    # Fallback broadcast address
    return '255.255.255.255'


def host_advertise(room_code: str) -> socket.socket:
    """Start a UDP broadcast socket advertising the host and room code.
    Returns the socket; caller should keep it alive and can close it to stop broadcasting.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)
    payload = json.dumps({"type": "ad", "code": room_code, "port": TCP_PORT}).encode()

    def _send():
        try:
            sock.sendto(payload, (_get_local_broadcast(), BROADCAST_PORT))
        except Exception:
            pass

    # Send once immediately; caller can schedule periodic calls to _send()
    _send()
    return sock


def advertise_tick(sock: socket.socket, room_code: str):
    try:
        payload = json.dumps({"type": "ad", "code": room_code, "port": TCP_PORT}).encode()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(payload, (_get_local_broadcast(), BROADCAST_PORT))
    except Exception:
        pass


def host_wait_for_connection(room_code: str) -> Tuple[socket.socket, Tuple[str, int], str]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", TCP_PORT))
    srv.listen(1)
    while True:
        conn, addr = srv.accept()
        try:
            raw = conn.recv(BUFFER_SIZE)
            hello = json.loads(raw.decode())
            if hello.get("type") == "join" and hello.get("code") == room_code:
                conn.send(json.dumps({"type": "ok"}).encode())
                # Randomly assign host/client colors
                host_color = random.choice(["white", "black"])
                client_color = "black" if host_color == "white" else "white"
                # Inform client of their color
                try:
                    conn.send(json.dumps({"type": "start", "your_color": client_color}).encode())
                except Exception:
                    pass
                return conn, addr, host_color
            else:
                conn.close()
        except Exception:
            conn.close()


def client_find_host(timeout: float = 2.0) -> Optional[Tuple[str, int, str]]:
    """Listen for a host advertisement and return (ip, port, code)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    sock.settimeout(timeout)
    try:
        data, (ip, _) = sock.recvfrom(BUFFER_SIZE)
        msg = json.loads(data.decode())
        if msg.get("type") == "ad":
            return ip, int(msg.get("port")), msg.get("code")
    except Exception:
        return None
    finally:
        sock.close()


def client_connect(ip: str, port: int, room_code: str) -> Optional[Tuple[socket.socket, Optional[str]]]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.send(json.dumps({"type": "join", "code": room_code}).encode())
        resp = json.loads(s.recv(BUFFER_SIZE).decode())
        if resp.get("type") == "ok":
            # Expect a start message with assigned color
            try:
                s.settimeout(3.0)
                start_msg = json.loads(s.recv(BUFFER_SIZE).decode())
                your_color = start_msg.get("your_color") if start_msg.get("type") == "start" else None
            except Exception:
                your_color = None
            finally:
                try:
                    s.settimeout(None)
                except Exception:
                    pass
            return s, your_color
    except Exception:
        s.close()
        return None
    return None


def send_move(sock: socket.socket, from_pos, to_pos, promo: Optional[str] = None):
    payload = {"type": "move", "from": from_pos, "to": to_pos}
    if promo:
        payload["promo"] = promo
    payload = json.dumps(payload).encode()
    sock.send(payload)


def recv_message(sock: socket.socket) -> Optional[dict]:
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None
        return json.loads(data.decode())
    except Exception:
        return None
