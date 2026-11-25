import asyncio
import logging
from typing import Optional
import serial_asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AsyncSerialDevice:
    def __init__(self, port: str, baudrate: int = 115200):
        self.port: str = port
        self.baudrate: int = baudrate
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._read_task: Optional[asyncio.Task] = None
        self._running: bool = False

    async def connect(self) -> None:
        """Establishes the async serial connection and starts the read loop."""
        logging.info(f"Connecting to {self.port} at {self.baudrate} baud...")
        
        # Open the async serial connection
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.port, 
            baudrate=self.baudrate
        )
        
        self._running = True
        self._read_task = asyncio.create_task(self._read_loop())
        logging.info(f"Connected to {self.port} successfully.")

    async def _read_loop(self) -> None:
        """Internal background task that continuously reads incoming bytes."""
        while self._running and self.reader:
            try:
                # Read line-by-line (or use self.reader.read(n) for raw byte chunks)
                line = await self.reader.readline()
                if not line:
                    # EOF reached / connection lost
                    logging.warning("Received EOF from serial port.")
                    break
                
                await self.handle_data(line)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in read loop: {e}")
                break

    async def handle_data(self, data: bytes) -> None:
        """Override this method in a subclass or handle parsing here."""
        decoded_line = data.decode('utf-8', errors='ignore').strip()
        logging.info(f"[RX]: {decoded_line}")

    async def send(self, data: bytes) -> None:
        """Thread-safe/async-safe way to transmit data down the wire."""
        if not self.writer:
            raise RuntimeError("Serial connection is not open. Call connect() first.")
        
        self.writer.write(data)
        await self.writer.drain()
        logging.info(f"[TX]: {data.decode('utf-8', errors='ignore').strip()}")

    async def disconnect(self) -> None:
        """Gracefully shuts down the background loop and closes the port."""
        logging.info(f"Disconnecting from {self.port}...")
        self._running = False
        
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
        self.reader = None
        self.writer = None
        logging.info("Serial port closed cleanly.")


# ==========================================
# Example Usage
# ==========================================
async def main():
    # Instantiate the device controller
    logging.info
    device = AsyncSerialDevice(port='/dev/ttyUSB0', baudrate=115200)
    
    try:
        await device.connect()
        
        # Periodic command injection example
        for i in range(100):
            await asyncio.sleep(2)
            await device.send(f"COMMAND_{i}\n".encode())
            await device.send("bp:?\n".encode())
            
        # Keep running a bit longer to catch trailing data
        await asyncio.sleep(2)
        
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure it cleans up even on errors/crashes
        await device.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
