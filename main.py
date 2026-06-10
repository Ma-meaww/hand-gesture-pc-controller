import asyncio

from config import HOST, PORT
from server.websocket_server import start_server


def main():
    try:
        asyncio.run(start_server(HOST, PORT))
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()