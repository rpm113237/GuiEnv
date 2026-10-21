import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from bleak import BleakScanner, BleakClient
import serial
import random

# Standard Nordic UART Service (NUS) UUIDs
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Notify
NUS_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # Write

TARGET_DEVICE_NAME = "Squeezer"
class MultiSendNusApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("NUS Controller with Macro Presets")
        self.geometry("800x1400")

        self.is_running = True
        self.client = None

        self.style =ttk.Style(self)
        self.style.theme_use('clam')
        
        #mess with styles;
        self.style.configure('TButton', background = 'ivory', width=0,foreground='indigo',padding=(0,5), borderwidth =3, font =('Helvetica',12,'bold'))
        self.style.configure('TLabel', background = 'light blue', foreground='magenta',font =('Helvetica',12,'bold'))
        self.style.configure('TLabelFrame', relief='raised', borderwidth =5)
        self.style.configure("TFrame", background ='light blue', bordercolor='yellow',borderwidth = 50, relief='groove')
        self.style.configure("Warning.TButton", foreground = 'red', background='light blue', font=('Helvetica',16,'bold'))
#      Configure the 'Treeview.Heading' style globally
        self.style.configure("Treeview.Heading",background="light blue",foreground="green",font=("Helvetica", 11, "bold"))
        # Configure the frame container style
        self.style.configure("Custom.TLabelframe",background="#f0f0f0",bordercolor='red',borderwidth=2,relief="raised",)
# Configure the title text inside the labelframe foreground="#2c3e50",
        self.style.configure("Custom.TLabelframe.Label",background="#f0f0f0",foreground = 'magenta',font=("Helvetica", 16, "bold"),)


        self.is_running = True
        self.client = None
        # Get the currently active theme name
#         print("Active theme:", self.style.theme_use())

        
        # Track all dynamically generated preset buttons for mass state tracking
        self.macro_buttons = []

        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self.build_ui()

    def build_ui(self):
        """Builds terminal interface with a macro send frame."""
#         print("Available themes:", self.style.theme_names())
        
        # --- 1. Connection Controls Panel ---
        top_frame = tk.Frame(self, relief='groove',highlightbackground="blue",highlightcolor="blue", highlightthickness=4,borderwidth = 5)        
        top_frame.pack(fill=tk.X,padx=10, pady=10)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)

        self.status_lbl = ttk.Label(top_frame, text="Disconnected")
        self.status_lbl.grid(row=0, column=0, sticky ='n')
        
        self.scan_btn = ttk.Button(top_frame,text="Connect",
            command=lambda: asyncio.create_task(self.connect_nus_device())    )
        #self.scan_btn.pack(side=tk.TOP, anchor='w',)
        self.scan_btn.grid(row=1, column=0, sticky ='n')
        
        self.disconnect_btn = ttk.Button(top_frame,text="Disconnect",state=tk.DISABLED,
            command=lambda: asyncio.create_task(self.disconnect_nus())  )
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
        sqfont= tkfont.Font(font="TkDefaultFont")		#to calc width

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

    def log_to_terminal(self, text: str):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, text + "\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)

    def set_widgets_state(self, state):
        """Toggles operational state across manual entry and macro lists cleanly."""
        self.send_btn.config(state=state)
#         print(f" macrobuttons ={self.macro_buttons}")
        for btn in self.macro_buttons:
            btn.config(state=state)

    async def connect_nus_device(self):
        self.scan_btn.config(state=tk.DISABLED)
        self.log_to_terminal(f"[SYS] Scanning for '{TARGET_DEVICE_NAME}'...")

        try:
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: d.name == TARGET_DEVICE_NAME or TARGET_DEVICE_NAME in (d.name or "")
            )

            if not device:
                self.log_to_terminal("[SYS] Error: NUS device not found.")
                self.scan_btn.config(state=tk.NORMAL)
                return

            self.log_to_terminal(f"[SYS] Connecting to {device.address}...")
            self.mac_lbl.configure(text=device.address)
            self.client = BleakClient(device, disconnected_callback=self.on_nus_disconnect)
            await self.client.connect()

            self.status_lbl.config(text="Connected ✅")
            self.log_to_terminal("[SYS] Connected. Activating Streams...")

            await self.client.start_notify(NUS_TX_UUID, self.nus_notification_handler)
            
            self.disconnect_btn.config(state=tk.NORMAL)
            self.set_widgets_state(tk.NORMAL)  # Wake up all buttons
            
            #send wakeup stuff
            await self.send_payload('HW:')	#HWID
            await asyncio.sleep(0.1)
            await self.send_payload('R:')
            await asyncio.sleep(0.1)
            await self.send_payload('BP:')
            await asyncio.sleep(0.1)
            await self.send_payload('BV:')
            await asyncio.sleep(0.1)
            await self.send_payload('C?:')
            await asyncio.sleep(0.1)
            await self.send_payload('TR:')
            await asyncio.sleep(0.1)
#             await self.send_payload('HW:')
#             await self.send_payload('HW:')
#             await self.send_payload('HW:')


        except Exception as e:
            messagebox.showerror("NUS Connection Error", str(e))
            self.scan_btn.config(state=tk.NORMAL)

    def nus_notification_handler(self, sender, data: bytearray):
        try:
            decoded_text = data.decode("utf-8").strip()
            SQzrlist=decoded_text.split(':')
            if(SQzrlist[0]!='HF'):
               self.log_to_terminal(f"[RX]: {decoded_text}")
               
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
               self.log_to_terminal(f"[RX]: {decoded_text}")
        except UnicodeDecodeError:
            self.log_to_terminal(f"[RX Hex]: {data.hex().upper()}")
#         asyncio.create_task(self.send_payload('123'))

#         print(' notification handler, can we do stuff here?')            

    async def send_payload(self, text_payload: str):
        """Core async transmit pipeline utilized by both manual text entry and macro triggers."""
        if not self.client or not self.client.is_connected:
            return

        try:
            # Append standard serial termination characters
#             print(f'text payload: {text_payload}')
            encoded = (text_payload + "\r\n").encode("utf-8")
#             print(f'encoded in send_payload ={encoded}')
            await self.client.write_gatt_char(NUS_RX_UUID, encoded, response=False)
            self.log_to_terminal(f"[TX]: {text_payload}")
#             await asyncio.sleep(0.01)	#give it some time?

        except Exception as e:
            self.log_to_terminal(f"[SYS ERROR]: Failed payload write: {e}")

    async def send_manual_input(self):
        """Extracts text out of input bar and routes it directly to send_payload."""
        payload_string = self.input_entry.get()
        if not payload_string:
            return
        
        await self.send_payload(payload_string)
        self.input_entry.delete(0, tk.END)

    def on_nus_disconnect(self, client):
        self.status_lbl.config(text="Disconnected ❌")
        self.mac_lbl.configure(text="00:00:00:00:00:00")
        self.HF_lbl.configure(text="HF:--.--")
        self.log_to_terminal("[SYS] BLE Disconnected")
        self.scan_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.set_widgets_state(tk.DISABLED)  # Gray out all macros

    async def disconnect_nus(self):
        if self.client and self.client.is_connected:
            await self.client.stop_notify(NUS_TX_UUID)
            await self.client.disconnect()
        self.on_nus_disconnect(None)

    def close_application(self):
        self.is_running = False
        if self.client and self.client.is_connected:
            print('application closed')
            asyncio.create_task(self.send_payload('X:'))
#             self.send_payload('X:')
#         asyncio.create_task(self.disconnect_nus())
        self.destroy()


class AsyncLoopEngine:
    @staticmethod
    async def run_application():
        print("are we here?")
        app = MultiSendNusApp()
#         app.macro_buttons[1].invoke()
        while app.is_running:
            try:
                app.update()
                # bewlow works, can call self stuff
#                 app.input_entry.delete(0,tk.END)
#                 app.input_entry.insert(0,"bp:?")
#                 app.send_btn.invoke()
#                 await app.send_payload("Hello")
#                 app.macro_buttons[1].invoke()
#                 print(f"print HF = {app.HF_lbl['text']}") #(yes we can)
#                 app.log_to_terminal("log to terminal")
                await asyncio.sleep(0.02)
            except tk.TclError:
                break


if __name__ == "__main__":
    asyncio.run(AsyncLoopEngine.run_application())
