import asyncio
import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
import serial_asyncio
from bleak import BleakClient, BleakScanner
# following enables the display on the Raspberry Pi when using Tkinter
import os
os.environ["DISPLAY"] = ":0"

# NUS (Nordic UART Service) UUIDs
NUS_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
NUS_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write to BLE device
NUS_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Read/Notify from BLE device

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logging.getLogger("asyncio").setLevel(logging.INFO)

class AsyncScannerApp(tk.Tk):
    def __init__(self, serial_port: str):
        super().__init__()
        logging.info("\nInitializing AsyncScannerApp...")
        
        self.serial_port = serial_port
        self.attempt =0
        
        # Hardware communication objects
        self.ser_reader: Optional[asyncio.StreamReader] = None
        self.ser_writer: Optional[asyncio.StreamWriter] = None
        self.ble_client: Optional[BleakClient] = None
        
        # Runtime states
        self.is_running = True
        self.is_scanning = False
        self.discovered_devices: Dict[str, str] = {}  # Map "Name (MAC)" -> MAC Address

        # UI Initialization
        self.title("Squeezer GUI with Serial")
        self.geometry("1000x750")
        
        # 1. Configuration Section Frame
        config_frame = ttk.LabelFrame(self, text=" Hardware Connections ", padding=10)
        config_frame.pack(fill="x", padx=15, pady=10)
        
        # BLE Dropdown Menu Setup
        ttk.Label(config_frame, text="Select BLE Device:").grid(row=0, column=0, sticky="w", padx=5)
        self.ble_dropdown = ttk.Combobox(config_frame, width=30, state="readonly")
        self.ble_dropdown.set("Click Scan to search...")
        self.ble_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # # Scan and Connect Buttons
        # self.scan_btn = ttk.Button(config_frame, text="Scan", command=self.on_scan_click)
        # self.scan_btn.grid(row=0, column=2, padx=5)
        
        # self.connect_btn = ttk.Button(config_frame, text="Connect", command=self.on_connect_click, state="disabled")
        # self.connect_btn.grid(row=0, column=3, padx=5)

        # 2. Status Information Panel
        self.status_label = ttk.Label(self, text="System: Waiting for Serial Initialization...", font=("Arial", 11, "bold"))
        self.status_label.pack(anchor="w", padx=20, pady=5)
        
        # 3. Log Output Panel
        self.log_widget = tk.Text(self, height=15, width=60, state='disabled', background="#1e1e1e", foreground="#ffffff")
        self.log_widget.pack(padx=15, pady=10, fill="both", expand=True)
        
        # 4. Global Action Controller
        self.send_btn = ttk.Button(self, text="Broadcast PING Command", command=self.on_send_click, state="disabled")
        self.send_btn.pack(pady=10)
        
        # Setup clean closure protocols
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def log_to_ui(self, message: str):
        """Thread-safe context logging text to UI panel."""
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')

    # def on_scan_click(self):
    #     """Triggered when the scan button is clicked."""
    #     if not self.is_scanning:
    #         asyncio.create_task(self.scan_for_ble_devices())

    # def on_connect_click(self):
    #     """Triggered when the connect button is clicked."""
    #     selected = self.ble_dropdown.get()
    #     if selected in self.discovered_devices:
    #         mac_address = self.discovered_devices[selected]
    #         asyncio.create_task(self.connect_ble(mac_address))

    def on_send_click(self):
        """Dispatches outbound command to both communication systems."""
        asyncio.create_task(self.send_serial(b"BP:?\n"))
        asyncio.create_task(self.send_ble(b"BP:?\n"))
        
    async def ble_supervisor_loop(self):
        """Keeps scanning/connecting in the background; never blocks the UI."""
        while self.is_running:
            if not self.ble_client or not self.ble_client.is_connected:
                if not self.is_scanning:
                    await self.scan_for_ble_devices()
            await asyncio.sleep(1)  # pause between scan cycles / connection checks
    

    async def scan_for_ble_devices(self):
        """Scans for BLE devices and automatically connects if 'Squeezer' is found."""
        self.is_scanning = True
        # self.scan_btn.config(state="disabled")
        self.ble_dropdown.set("Searching for Squeezer...")
        self.log_to_ui("[BLE]: Scanning for 'Squeezer'...")
        logging.info("[BLE]: Starting scan for devices...")
        # attempt =0
        
        try:
            # Look for devices for up to 4 seconds
            devices = await BleakScanner.discover(timeout=1.0)
            
            self.discovered_devices.clear()
            dropdown_options = []
            target_mac: Optional[str] = None
            # max_attempts = 5
            target_mac = None

            # for attempt in range(1, max_attempts + 1):
            self.attempt = 1 + self.attempt
            logging.info(f"[BLE]: Attempt {self.attempt} to discover devices...")
            devices = await BleakScanner.discover(timeout=1.0)
            logging.info(f"[BLE]: Discovered devices: {[d.address for d in devices]}")
            self.discovered_devices.clear()
            dropdown_options = []
            target_mac = None

            for d in devices:
                name = d.name if d.name else "Unknown Device"
                display_string = f"{name} ({d.address})"
                self.discovered_devices[display_string] = d.address
                dropdown_options.append(display_string)

                if name == "Squeezer":
                    target_mac = d.address

                if dropdown_options:
                    self.ble_dropdown.config(values=dropdown_options)

                if target_mac:
                    break

                            
            # Action path conditional on finding the target device
            if target_mac:
                self.ble_dropdown.set(f"Squeezer Found! ({target_mac})")
                self.log_to_ui(f"[BLE]: Found 'Squeezer' at {target_mac}. Connecting automatically...")
                
                # Hand control off to the connection manager task
                await self.connect_ble(target_mac)
            else:
                self.ble_dropdown.set("Squeezer not found.")
                self.log_to_ui("[BLE]: Scan finished. 'Squeezer' was not detected in this cycle.")
                if dropdown_options:
                    self.connect_btn.config(state="normal")  # Allow fallback manual connect
                
        except Exception as e:
            self.log_to_ui(f"[BLE Scan Error]: {e}")
            self.ble_dropdown.set("Scan failed.")
        finally:
            self.is_scanning = False
            # self.scan_btn.config(state="normal")

    async def connect_serial(self):
        """Connects to the background Serial line."""
        try:
            self.ser_reader, self.ser_writer = await serial_asyncio.open_serial_connection(
                url=self.serial_port, baudrate=115200
            )
            self.log_to_ui(f"[Serial]: Connected safely to {self.serial_port}")
            asyncio.create_task(self.read_serial_loop())
            self.status_label.config(text="System: Serial Connected. Ready to scan BLE.")
        except Exception as e:
            self.log_to_ui(f"[Serial Error]: Connection failed: {e}")
            self.status_label.config(text="System: Serial initialization failed.")

    async def read_serial_loop(self):
        """Reads characters streaming from the USB serial device."""
        while self.is_running and self.ser_reader:
            try:
                line = await self.ser_reader.readline()
                if not line:
                    break
                self.log_to_ui(f"[RX Serial]: {line.decode('utf-8', errors='ignore').strip()}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_to_ui(f"[Serial RX Error]: {e}")
                break

    async def connect_ble(self, mac_address: str):
        """Connects to the user-selected Nordic NUS BLE peripheral."""
        self.log_to_ui(f"[BLE]: Connecting to {mac_address}...")
        logging.info(f"Attempting to connect to BLE device at {mac_address}")
        # self.connect_btn.config(state="disabled")
        # self.scan_btn.config(state="disabled")
        
        self.ble_client = BleakClient(mac_address)
        try:
            await self.ble_client.connect()
            self.log_to_ui("[BLE]: Connected to NUS service successfully!")
            logging.info(f"Connected to BLE device at {mac_address}")
            self.attempt = 0
            
            # Start notifications from the device TX channel
            await self.ble_client.start_notify(NUS_TX_UUID, self.on_ble_notification)
            
            self.status_label.config(text="System: Fully Connected (Serial + BLE)")
            self.send_btn.config(state="normal")
        except Exception as e:
            self.log_to_ui(f"[BLE Connection Error]: {e}")
            self.connect_btn.config(state="normal")
            self.scan_btn.config(state="normal")

    def on_ble_notification(self, characteristic, data: bytearray):
        """Callback processing inbound wireless frames."""
        decoded = data.decode('utf-8', errors='ignore').strip()
        self.log_to_ui(f"[RX BLE]: {decoded}")
        logging.info(f"[BLE_RX]: {decoded}")
        
    async def send_serial(self, data: bytes ):
        """Sends data the serial device over USB."""
        if self.ser_writer:
              self.ser_writer.write(data)
              await self.ser_writer.drain()
              self.log_to_ui(f"[TX Serial]: {data.decode().strip()}")    
              
    async def send_ble(self, data: bytes):
        """Sends data to the BLE device over the Nordic NUS service."""
        if self.ble_client and self.ble_client.is_connected:
            try:
                await self.ble_client.write_gatt_char(NUS_RX_UUID, data, response=False)
                self.log_to_ui(f"[TX BLE]: {data.decode().strip()}")
                logging.info(f"[BLE_TX]: {data.decode().strip()}")
            except Exception as e:
                self.log_to_ui(f"[BLE TX Error]: {e}")
                
    async def broadcast_data(self, data: bytes):
        """Sends identical payloads to both interfaces synchronously."""
        if self.ser_writer:
            self.ser_writer.write(data)
            await self.ser_writer.drain()
            self.log_to_ui(f"[TX Serial]: {data.decode().strip()}")
            logging.info(f"[TX Serial]: {data.decode().strip()}")
            
        if self.ble_client and self.ble_client.is_connected:
            try:
                await self.ble_client.write_gatt_char(NUS_RX_UUID, data, response=False)
                self.log_to_ui(f"[TX BLE]: {data.decode().strip()}")
                logging.info(f"[BLE_TX]: {data.decode().strip()}")
            except Exception as e:
                self.log_to_ui(f"[BLE TX Error]: {e}")

    async def gui_updater_loop(self):
        """Explicit layout pump executing Tkinter frames every 10ms."""
        while self.is_running:
            try:
                self.update()
            except tk.TclError:
                break  # Window destroyed
            await asyncio.sleep(0.01)

    def close_app(self):
        """Enforces clean execution teardowns."""
        self.is_running = False
        self.destroy()

    async def main_lifecycle(self):
        """Application orchestrator sequencing configurations."""
        # Initialize serial connection immediately upon startup
        await self.connect_serial()
        # Start the BLE supervisor loop in the background
        logging.info("Starting main lifecycle...")

        scan_task = asyncio.create_task(self.ble_supervisor_loop())
        logging.info("BLE supervisor loop started.")
        try:
            await self.gui_updater_loop()
        finally:
            scan_task.cancel()
            if self.ble_client and self.ble_client.is_connected:
                await self.ble_client.disconnect()
        logging.info("Main run context safely closed.")

        
        # logging.info("Starting main lifecycle...")
                
        # """Scans for BLE devices and automatically connects if 'Squeezer' is found."""
        # if not self.ble_client or not self.ble_client.is_connected:
        #     logging.info("Scanning for BLE devices...")
        #     await self.scan_for_ble_devices()
        #     logging.info("BLE scan completed.")
        
        # # Enter the event loop driving UI adjustments
        # await self.gui_updater_loop()
        
        # # Cleanup routine when the loop stops
        # if self.ble_client and self.ble_client.is_connected:
        #     await self.ble_client.disconnect()
        # logging.info("Main run context safely closed.")

# ==========================================
# Application Launch Hook
# ==========================================
if __name__ == "__main__":
    # Point this to the reliable USB alias found on your Pi
    USB_SERIAL_PORT = "/dev/ttyUSB0" 
    
    app = AsyncScannerApp(serial_port=USB_SERIAL_PORT)
    
    try:
        asyncio.run(app.main_lifecycle())
        logging.info("Application exited normally.")
    except KeyboardInterrupt:
        print("Application stopped via terminal.")
