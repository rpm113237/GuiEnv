import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import serial
from serial.tools import list_ports


class SerialApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Serial Port Monitor")
		self.connection = None
		self.messages = queue.Queue()

		controls = ttk.Frame(root, padding=10)
		controls.pack(fill="x")

		ttk.Label(controls, text="Port:").grid(row=0, column=0, padx=4)
		self.port = tk.StringVar()
		self.port_box = ttk.Combobox(
			controls, textvariable=self.port, state="readonly", width=18
		)
		self.port_box.grid(row=0, column=1, padx=4)
		ttk.Button(controls, text="Refresh", command=self.refresh_ports).grid(
			row=0, column=2, padx=4
		)

		ttk.Label(controls, text="Baud rate:").grid(row=0, column=3, padx=4)
		self.baud = tk.StringVar(value="9600")
		ttk.Entry(controls, textvariable=self.baud, width=9).grid(
			row=0, column=4, padx=4
		)
		self.connect_button = ttk.Button(
			controls, text="Connect", command=self.toggle_connection
		)
		self.connect_button.grid(row=0, column=5, padx=4)

		self.output = tk.Text(root, height=18, width=80, state="disabled")
		self.output.pack(fill="both", expand=True, padx=10, pady=(0, 8))

		send_row = ttk.Frame(root, padding=(10, 0, 10, 10))
		send_row.pack(fill="x")
		self.message = tk.StringVar()
		self.entry = ttk.Entry(send_row, textvariable=self.message)
		self.entry.pack(side="left", fill="x", expand=True)
		self.entry.bind("<Return>", self.send_message)
		ttk.Button(send_row, text="Send", command=self.send_message).pack(
			side="left", padx=(6, 0)
		)

		self.refresh_ports()
		self.root.after(100, self.process_messages)
		self.root.protocol("WM_DELETE_WINDOW", self.close)

	def refresh_ports(self):
		ports = [item.device for item in list_ports.comports()]
		self.port_box["values"] = ports
		if ports and self.port.get() not in ports:
			self.port.set(ports[0])

	def toggle_connection(self):
		if self.connection and self.connection.is_open:
			self.disconnect()
			return
		try:
			baud_rate = int(self.baud.get())
			if not self.port.get():
				raise ValueError("Select a serial port first.")
			self.connection = serial.Serial(self.port.get(), baud_rate, timeout=0.1)
		except (ValueError, serial.SerialException) as error:
			messagebox.showerror("Connection error", str(error))
			return

		self.connect_button.configure(text="Disconnect")
		self.port_box.configure(state="disabled")
		threading.Thread(
			target=self.read_serial, args=(self.connection,), daemon=True
		).start()
		self.write_output(f"Connected to {self.connection.port}\n")

	def read_serial(self, connection):
		while connection.is_open:
			try:
				data = connection.readline()
				if data:
					self.messages.put(data.decode("utf-8", errors="replace"))
			except (serial.SerialException, OSError) as error:
				self.messages.put(f"Serial error: {error}\n")
				break

	def send_message(self, event=None):
		if not self.connection or not self.connection.is_open:
			messagebox.showwarning("Not connected", "Connect to a serial port first.")
			return
		try:
			self.connection.write((self.message.get() + "\n").encode("utf-8"))
			self.message.set("")
		except (serial.SerialException, OSError) as error:
			messagebox.showerror("Send error", str(error))

	def process_messages(self):
		while True:
			try:
				text = self.messages.get_nowait()
			except queue.Empty:
				break
			self.write_output(text)
		self.root.after(100, self.process_messages)

	def write_output(self, text):
		self.output.configure(state="normal")
		self.output.insert("end", text)
		self.output.see("end")
		self.output.configure(state="disabled")

	def disconnect(self):
		connection = self.connection
		self.connection = None
		if connection and connection.is_open:
			connection.close()
		self.connect_button.configure(text="Connect")
		self.port_box.configure(state="readonly")
		self.write_output("Disconnected\n")

	def close(self):
		if self.connection and self.connection.is_open:
			self.connection.close()
		self.root.destroy()


if __name__ == "__main__":
	root = tk.Tk()
	SerialApp(root)
	root.mainloop()
