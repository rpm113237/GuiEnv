import asyncio
import importlib
import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
import random
import tkinter.font as tkfont
from bleak import BleakClient, BleakScanner
# no idea why I had to do this below
try:
    serial_asyncio = importlib.import_module("serial_asyncio")
except ImportError:
    serial_asyncio = None
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
        
        
                
        # mess with styles;
        self.style =ttk.Style(self)
        self.style.theme_use('clam')
        
        self.style.configure('TButton', background = 'ivory', width=0,foreground='indigo',padding=(0,5), borderwidth =3, font =('Helvetica',12,'bold'))
        self.style.configure('TLabel', background = 'light blue', foreground='magenta',font =('Helvetica',12,'bold'))
        self.style.configure('TLabelFrame', relief='raised', borderwidth =5)
        self.style.configure("TFrame", background ='light blue', bordercolor='yellow',borderwidth = 50, relief='groove')
        self.style.configure("Warning.TButton", foreground = 'red', background='light blue', font=('Helvetica',16,'bold'))
        # Configure the 'Treeview.Heading' style globally
        self.style.configure("Treeview.Heading",background="light blue",foreground="green",font=("Helvetica", 11, "bold"))
        # Configure the frame container style
        self.style.configure("Custom.TLabelframe",background="#f0f0f0",bordercolor='red',borderwidth=2,relief="raised",)
        # Configure the title text inside the labelframe
        self.style.configure("Custom.TLabelframe.Label",background="#f0f0f0",foreground = 'magenta',font=("Helvetica", 16, "bold"),)
        # 
        # Runtime states
        self.is_running = True
        self.is_scanning = False
        self.discovered_devices: Dict[str, str] = {}  # Map "Name (MAC)" -> MAC Address

        # UI Initialization
        self.title("Squeezer GUI with Serial")
        self.geometry("800x1400")
        
        # # 1. Configuration Section Frame
        # config_frame = ttk.LabelFrame(self, text=" Hardware Connections ", padding=10)
        # config_frame.pack(fill="x", padx=15, pady=10)
        
        # # BLE Dropdown Menu Setup
        # ttk.Label(config_frame, text="Select BLE Device:").grid(row=0, column=0, sticky="w", padx=5)
        # self.ble_dropdown = ttk.Combobox(config_frame, width=30, state="readonly")
        # self.ble_dropdown.set("Click Scan to search...")
        # self.ble_dropdown.grid(row=0, column=1, padx=5, pady=5)
              

        # # 2. Status Information Panel
        # self.status_label = ttk.Label(self, text="System: Waiting for Serial Initialization...", font=("Arial", 11, "bold"))
        # self.status_label.pack(anchor="w", padx=20, pady=5)
        
        # # 3. Log Output Panel
        # self.log_widget = tk.Text(self, height=15, width=60, state='disabled', background="#1e1e1e", foreground="#ffffff")
        # self.log_widget.pack(padx=15, pady=10, fill="both", expand=True)
        
        # # 4. Global Action Controller
        # self.send_btn = ttk.Button(self, text="Broadcast PING Command", command=self.on_send_click, state="disabled")
        # self.send_btn.pack(pady=10)
        
        
        # Track all dynamically generated preset buttons for mass state tracking
        self.macro_buttons = []
            
        # Setup clean closure protocols
        self.protocol("WM_DELETE_WINDOW", self.close_app)        
        
       
        self.build_connection_controls()
        self.build_terminal_frame()
        self.build_macro_frame()
        self.build_manual_transmit_frame()
        
    
    #         print("Available themes:", self.style.theme_names())
    def build_connection_controls(self):
        """Builds the connection controls panel."""
            # --- 1. Connection Controls Panel ---
        top_frame = tk.Frame(self, relief='groove',highlightbackground="blue",
        highlightcolor="blue", highlightthickness=4,borderwidth = 5)        
        top_frame.pack(fill=tk.X,padx=10, pady=10)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)

        self.status_lbl = ttk.Label(top_frame, text="Disconnected")
        self.status_lbl.grid(row=0, column=0, sticky ='n')
        
        self.scan_btn = ttk.Button(top_frame,text="Connect",
            command=lambda: asyncio.create_task(self.send_ble('BP:?', 0.1))    )
        #self.scan_btn.pack(side=tk.TOP, anchor='w',)
        self.scan_btn.grid(row=1, column=0, sticky ='n')
        
        self.disconnect_btn = ttk.Button(top_frame,text="Disconnect",state=tk.DISABLED, command=lambda: asyncio.create_task(self.send_ble('R:',0.1)))
        
#         self.disconnect_btn.pack(side=tk.TOP, anchor='w')
        self.disconnect_btn.grid(row=2, column=0, sticky ='n')
        
        self.mac_lbl = ttk.Label(top_frame, text="00:00:00:00:00:00")
        self.mac_lbl.grid(row=3, column=0, sticky ='n')
        
        self.HWID_lbl = ttk.Label(top_frame, text="HWID")
        self.HWID_lbl.grid(row=0, column=1, sticky ='n')
        
        self.SWRev_lbl = ttk.Label(top_frame, text="SW Rev")
        self.SWRev_lbl.grid(row=1, column=1, sticky ='n')
        
        self.BatVolts_lbl = ttk.Label(top_frame, text="BattVolts:---")
        self.BatVolts_lbl.grid(row=2, column=1, sticky ='n')
        
        self.BatPcnt_lbl = ttk.Label(top_frame, text="BattPcnt:---")
        self.BatPcnt_lbl.grid(row=3, column=1, sticky ='n')
                
        self.HF_lbl = ttk.Label(top_frame, text="HF:NN.MM", font=("Helvetica", 16, "bold"))
        self.HF_lbl.grid(row=0, column=2, sticky ='n')
        
        self.SF_lbl = ttk.Label(top_frame, text="SF:NN.MM", font=("Helvetica", 16, "bold"))
        self.SF_lbl.grid(row=1, column=2)
        
        self.TGT_lbl = ttk.Label(top_frame, text="TGT:NN.MM", font=("Helvetica", 16, "bold"))
        self.TGT_lbl.grid(row=2, column=2) 
                   
    #2a------ Terminal Frame
    def build_terminal_frame(self):
        """Builds the terminal frame for displaying received data."""
        
        middle_frame = ttk.LabelFrame(self, text=" Received Data (TX) ", labelanchor = 'n',relief ='raised', borderwidth=15)
        middle_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)

        self.terminal = tk.Text(middle_frame, wrap=tk.WORD, state=tk.DISABLED, bg="grey10", relief="raised", bd=15,
                                fg="#00ff00", font=("Consolas", 10, 'bold'))
        self.terminal.pack(side = tk.LEFT,padx=5, pady=5)
        
        #2b-----calib frame        
        calib_frame = ttk.LabelFrame(self, style="Custom.TLabelframe",text="Calibration Frame", labelanchor ='n')
        calib_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        frame = ttk.Frame(self, relief="sunken", borderwidth=45, width=200, height=10)
        frame.pack(padx=20)
#         self.calib_lbl = tk.Text(calib_frame, wrap=tk.WORD, state=tk.DISABLED, bg="light blue", relief="raised", bd=5,
#                                 fg="#00ff00", font=("Consolas", 10, 'bold'))
#         self.calib_lbl.pack(padx=5, pady=5)
        self.CalCk_lbl = tk.Label(calib_frame, text="UnCalibrated", fg='white', bg = 'red')
        self.CalCk_lbl.pack()
        
        calibhdr_frame = ttk.Frame(calib_frame,relief ='raised',borderwidth=15)        
        calibhdr_frame.pack(fill=tk.X,padx=10, pady=10)
        
        self.calibstart_lbl=tk.Label(calibhdr_frame, text="Start\n(lbs)", bg='pink',fg='blue')
        self.calibstart_lbl.pack(side =tk.LEFT)
        self.calibstart_ent = tk.Entry(calibhdr_frame, width =5,font=("Helvetica", 16, "bold"))
        self.calibstart_ent.insert(0,'10')
        self.calibstart_ent.pack(side=tk.LEFT, padx=(0,10))
        
        self.calibstep_lbl=tk.Label(calibhdr_frame, text="Step\n(lbs)", bg='pink',fg='blue')
        self.calibstep_lbl.pack(side =tk.LEFT)
        self.calibstep_ent = tk.Entry(calibhdr_frame, width =5,font=("Helvetica", 11, "bold"))
        self.calibstep_ent.insert(0,'20')
        self.calibstep_ent.pack(side=tk.LEFT, padx=(0,10))
        
        self.calibnumstep_lbl=tk.Label(calibhdr_frame, text="Num\nSteps", bg='pink',fg='blue')
        self.calibnumstep_lbl.pack(side =tk.LEFT)
        self.calibnumstep_ent = tk.Entry(calibhdr_frame, width =5,font=("Helvetica", 11, "bold"))
        self.calibnumstep_ent.insert(0,'6')
        self.calibnumstep_ent.pack(side=tk.LEFT, padx=(0,10))
        
        self.calibtare_lbl=tk.Label(calibhdr_frame, text="Tare\n----", bg='pink',fg='blue')
        self.calibtare_lbl.pack(side =tk.LEFT)
        
        self.calib_doit_btn = ttk.Button(
            calibhdr_frame,
            style="Warning.TButton",
            text="Do It",
            #command=lambda: asyncio.create_task(self.connect_nus_device()),
            command= lambda: print('Do It(TODO)'))        
        self.calib_doit_btn.pack(side=tk.RIGHT, padx=5)
        
        self.calib_ckcal_btn = ttk.Button(
            calibhdr_frame,
#             style="Warning.TButton",
            text="Check\nCal",
            #command=lambda: asyncio.create_task(self.connect_nus_device()),
            command= lambda: print('check calibration (TODO)'))        
        self.calib_ckcal_btn.pack(side=tk.RIGHT, padx=5)        
        
        calibdata_frame = ttk.LabelFrame(calib_frame, labelanchor = 'n',text = 'calib data',style='Custom.TLabelframe',)        
        calibdata_frame.pack(fill = tk.X, padx=2, pady=2)
        
        # 2. Define Columns
        # Use internal IDs for code management; these do not have to be the text
        columns = ("CalWt", "CalVal")

        # 3. Create Treeview Widget        
        table = ttk.Treeview(calibdata_frame, columns=columns, show="headings", selectmode="browse")
                
        sqfont = tkfont.Font(root=self, font="TkDefaultFont")
        #to calculate column width based on font size

        # 4. Define Headings (What the user sees at the top)
        table.heading("CalWt", text="CalWt")
        table.heading("CalVal", text="CalVal")
        
        # 5. Define Column Properties
        # anchor="w" aligns text left (West), "center" aligns center
        table.column("CalWt", width=sqfont.measure('123.456')+10, minwidth=1, anchor="center")
        table.column("CalVal", width=sqfont.measure('12345.5678')+10, minwidth=1, anchor="center")

        ncalpts=15  #desired number of elements
        data_list = [(str(i * 20 + 10), "{:.2f}".format(10000+random.uniform(-1000,1000))) for i in range(ncalpts)]
        
        # "show='headings'" hides the default hierarchical first column (tree arrow)
        for row in data_list:
            table.insert("", tk.END, values=row)

        # 7. Add a Scrollbar
        scrollbar = ttk.Scrollbar(calibdata_frame, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)

        # 8. Pack layout elements
        table.grid(row=0, column=0, sticky = 'n')
        scrollbar.grid(row=0,column=1,sticky='ns')
        
        self.caldelta_lbl=tk.Label(calibdata_frame, text="Delta", bg='pink',fg='blue')
        self.caldelta_lbl.grid(row = 1, column = 0, sticky = 'w')        
        
    def build_macro_frame(self):
        """Builds the macro commands panel."""
        # --- 3. MULTIPLE SEND BUTTONS PANEL (Macros) ---
        macro_frame = ttk.LabelFrame(self,  text=" Macro Commands ")
        macro_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)

        # Mapping: {"Button Label": "Data to Send"}
        presets = {
            "Batt %": "bp:?",
            'Batt V':'BV:?',
            "Tare": "TR:?",
            "Cal?": "C:?",
            "HWID": "HW:?",
            "SW Rev":"R:?",
            "OFF":"X"
        }

        # Dynamically loop and instantiate macro buttons
        for label, command_string in presets.items():
            btn = ttk.Button(
                macro_frame,
                text=label,
                state=tk.DISABLED,
                # Pass the unique command payload through lambda into our scheduler
                command=lambda cmd=command_string: asyncio.create_task(self.send_payload(cmd)),
            )

            btn.pack(side=tk.LEFT,expand=True)
            self.macro_buttons.append(btn)

        # --- 4. Manual Transmit Panel ---
    def build_manual_transmit_frame(self):
        """Builds the manual transmit panel."""
        bottom_frame = ttk.LabelFrame(self, text=" Manual Custom Send (RX) ")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_entry = ttk.Entry(bottom_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.input_entry.bind("<Return>", lambda event: asyncio.create_task(self.send_manual_input()))

        self.send_btn = ttk.Button(
            bottom_frame,
            text="Send String",
            state=tk.DISABLED,
            command=lambda: asyncio.create_task(self.send_manual_input()),
        )
        self.send_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def log_to_ui(self, message: str):
        """Thread-safe context logging text to UI panel."""
        self.terminal.config(state='normal')
        self.terminal.insert(tk.END, message + "\n")
        self.terminal.see(tk.END)
        self.terminal.config(state='disabled')

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
        logging.info("Starting BLE supervisor loop...")
        if self.is_running:
            logging.info("BLE supervisor loop is running...")
        else:
            logging.info("BLE supervisor loop is not running.")
        while self.is_running:
            if not self.ble_client or not self.ble_client.is_connected:
                if not self.is_scanning:
                    await self.scan_for_ble_devices()
            await asyncio.sleep(1)  # pause between scan cycles / connection checks
    

    async def scan_for_ble_devices(self):
        """Scans for BLE devices and automatically connects if 'Squeezer' is found."""
        self.is_scanning = True
        # self.scan_btn.config(state="disabled")
        # self.ble_dropdown.set("Searching for Squeezer...")
        self.log_to_ui("[BLE]: Scanning for 'Squeezer'...")
        logging.info("[BLE]: Starting scan for Squeezer...")
        # attempt =0
        
        try:
            # Look for devices for up to 4 seconds
            devices = await BleakScanner.discover(timeout=1.0)
            
            self.discovered_devices.clear()
            # dropdown_options = []
            target_mac: Optional[str] = None
            # max_attempts = 5
            target_mac = None

            # for attempt in range(1, max_attempts + 1):
            # self.attempt = 1 + self.attempt
            logging.info(f"[BLE]: Attempt {self.attempt} to discover devices...")
            devices = await BleakScanner.discover(timeout=1.0)
            # logging.info(f"[BLE]: Discovered devices: {[d.address for d in devices]}")
            self.discovered_devices.clear()
            # dropdown_options = []
            target_mac = None

            for d in devices:
                name = d.name if d.name else "Unknown Device"
                display_string = f"{name} ({d.address})"
                # logging.info(f"[BLE]: Discovered device: {display_string}") 
                self.discovered_devices[display_string] = d.address
                # dropdown_options.append(display_string)

                if name == "Squeezer":
                    target_mac = d.address
                    # logging.info(f"[BLE1]: Found 'Squeezer' at {target_mac}")    

                # if dropdown_options:
                #     self.mac_lbl.config(values=dropdown_options)

                if target_mac:
                    break

                            
            # Action path conditional on finding the target device
            if target_mac:
                # self.ble_dropdown.set(f"Squeezer Found! ({target_mac})")
                logging.info(f"[BLE]: Found 'Squeezer' at {target_mac}")
                self.log_to_ui(f"[BLE]: Found 'Squeezer' at {target_mac}. Connecting automatically...")
                
                # Hand control off to the connection manager task
                await self.connect_ble(target_mac)
            else:
                # self.ble_dropdown.set("Squeezer not found.")
                logging.info("[BLE]: 'Squeezer' not found in this scan cycle.")
                self.log_to_ui("[BLE]: Scan finished. 'Squeezer' was not detected in this cycle.")
                # if dropdown_options:
                #     self.connect_btn.config(state="normal")  # Allow fallback manual connect
                
        except Exception as e:
            # self.log_to_ui(f"[BLE Scan Error]: {e}")
            # self.ble_dropdown.set("Scan failed.")
            logging.info(f"[BLE]: Scan failed with error: {e}")
            # logging.info("[BLE]: Scan attempt finished.")
        finally:
            self.is_scanning = False
            # self.scan_btn.config(state="normal")

    async def connect_serial(self):
        """Connects to the background Serial line."""
        if serial_asyncio is None:
            message = "serial_asyncio is unavailable; serial connection skipped."
            self.log_to_ui(f"[Serial Error]: {message}")
            self.status_lbl.config(text="Serial unavailable")
            return

        try:
            self.ser_reader, self.ser_writer = await serial_asyncio.open_serial_connection(
                url=self.serial_port, baudrate=115200
            )
            self.log_to_ui(f"[Serial]: Connected safely to {self.serial_port}")
            asyncio.create_task(self.read_serial_loop())
            self.status_lbl.config(text="System: Serial Connected. Ready to scan BLE.")
        except Exception as e:
            self.log_to_ui(f"[Serial Error]: Connection failed: {e}")
            self.status_lbl.config(text="System: Serial initialization failed.")

    async def read_serial_loop(self):
        """Reads characters streaming from the USB serial device."""
        while self.is_running and self.ser_reader:
            try:
                line = await self.ser_reader.readline()
                if not line:
                    break
                if line.find('HF') == -1:
                    self.log_to_ui(f"[RX Serial]: {line.decode('utf-8', errors='ignore').strip()}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_to_ui(f"[Serial RX Error]: {e}")
                break

    async def connect_ble(self, mac_address: str):
        """Connects to the user-selected Nordic NUS BLE peripheral."""
        self.log_to_ui(f"[BLE]: Connecting to {mac_address}...")
        # logging.info(f"Attempting to connect to Squeezer device at {mac_address}")
        # self.connect_btn.config(state="disabled")
        # self.scan_btn.config(state="disabled")
        
        self.ble_client = BleakClient(mac_address)
        try:
            await self.ble_client.connect()
            # self.log_to_ui("[BLE]: Connected to NUS service successfully!")
            logging.info(f"Connected to Squeezer at {mac_address}")
            self.mac_lbl.config(text=mac_address)   #post the mac address
            # Start notifications from the device TX channel
            await self.ble_client.start_notify(NUS_TX_UUID, self.on_ble_notification)
            await asyncio.sleep(10.1)
            self.status_lbl.config(text="System: Fully Connected (Serial + BLE)")
            logging.info("Fully connected to Squeezer (Serial + BLE)")
            self.send_ble('HW:',0.1)    #HWID
            self.wakeup()
            self.send_btn.config(state="normal")
        except Exception as e:
            self.log_to_ui(f"[BLE Connection Error]: {e}")
            logging.error(f"BLE Connection Error: {e}")
            self.connect_btn.config(state="normal")
            self.scan_btn.config(state="normal")
    
    def wakeup(self):
         #send wakeup stuff
         logging.info("Sending wakeup commands to BLE device")
         asyncio.create_task(self.send_ble('HW:',0.1))	#HWID
         asyncio.create_task(self.send_ble('R:',0.1))
         asyncio.create_task(self.send_ble('BP:',0.1))
         asyncio.create_task(self.send_ble('BV:',0.1))
         asyncio.create_task(self.send_ble('C?:',0.1))
         asyncio.create_task(self.send_ble('TR:',0.1))
        #             await self.send_payload('HW:')
        #             await self.send_payload('HW:')
        #             await self.send_payload('HW:')

    def on_ble_notification(self, characteristic, data: bytearray):
        """Callback processing inbound wireless frames."""
        decoded_text = data.decode('utf-8', errors='ignore').strip()
        # self.log_to_ui(f"[RX BLE]: {decoded_text}")
        try:
            # decoded_text = data.decode("utf-8").strip()
            SQzrlist=decoded_text.split(':')
            if(SQzrlist[0]!='HF'):
                self.log_to_ui(f"[RX]: {decoded_text}")
                
            if SQzrlist[0]=='HF':
                self.HF_lbl.config(text=decoded_text)
            elif SQzrlist[0]=='HW':
                self.HWID_lbl.config(text='HWID:'+SQzrlist[1])
            elif SQzrlist[0]=='BP':
                self.BatPcnt_lbl.config(text='B%:'+SQzrlist[1])
            elif SQzrlist[0]=='BV':
                self.BatVolts_lbl.config(text='BV:'+SQzrlist[1])
            elif SQzrlist[0]=='R':
                self.SWRev_lbl.config(text='SW:'+SQzrlist[1])
            elif SQzrlist[0]=='C?':
                self.CalCk_lbl.config(text='Cal?:'+SQzrlist[1])
            elif SQzrlist[0]=='TR':
                self.calibtare_lbl.config(text='Tare\n'+SQzrlist[1])
            
            else:
                self.log_to_ui(f"[RX]: {decoded_text}")
        except UnicodeDecodeError:
            self.log_to_ui(f"[RX Hex]: {data.hex().upper()}")
        
        
    async def send_serial(self, data: bytes ):
        """Sends data the serial device over USB."""
        if self.ser_writer:
              self.ser_writer.write(data)
              await self.ser_writer.drain()
              self.log_to_ui(f"[TX Serial]: {data.decode().strip()}")    
              
    async def send_ble(self, data: str,wait_time: float):
        """Sends data to the BLE device over the Nordic NUS service."""
        logging.info(f"Sending BLE data: {data}")
        if self.ble_client and self.ble_client.is_connected:
            try:
                encoded = (data + "\r\n").encode("utf-8")
                await self.ble_client.write_gatt_char(NUS_RX_UUID, encoded, response=False)
                self.log_to_ui(f"[TX BLE]: {data}")
                logging.info(f"[BLE_TX]: {data}")
                await asyncio.sleep(wait_time)
            except Exception as e:
                self.log_to_ui(f"[BLE TX Error]: {e}")
                logging.error(f"BLE TX Error: {e}")
                
    async def send_manual_input(self):
            """Extracts text out of input bar and routes it directly to send_payload."""
            payload_string = self.input_entry.get()
            
            if not payload_string:
                return            
            await self.send_ble(bytes(payload_string, 'utf-8'), 0.1)
            self.input_entry.delete(0, tk.END)
                
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
        # logging.info("BLE supervisor loop started.")
        
        try:
            await self.gui_updater_loop()
            logging.info("GUI updater loop exited.")
        finally:
            scan_task.cancel()
            if self.ble_client and self.ble_client.is_connected:
                await self.ble_client.disconnect()
                logging.info("BLE client disconnected.")
        logging.info("Main run context safely closed.")
     
      

# ==========================================
# Application Launch Hook
# ==========================================
if __name__ == "__main__":
    # Point this to the reliable USB alias found on your Pi
    USB_SERIAL_PORT = "/dev/ttyUSB0" 
    
    app = AsyncScannerApp(serial_port=USB_SERIAL_PORT)
    
    try:
        logging.info("Launching application...")
        asyncio.run(app.main_lifecycle())
        logging.info("Application exited normally.")
    except KeyboardInterrupt:
        print("Application stopped via terminal.")
