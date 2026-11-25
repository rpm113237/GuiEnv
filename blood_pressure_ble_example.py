import argparse
import asyncio
import struct

from bleak import BleakClient, BleakScanner


BLOOD_PRESSURE_SERVICE = "00001810-0000-1000-8000-00805f9b34fb"
BLOOD_PRESSURE_MEASUREMENT = "00002a35-0000-1000-8000-00805f9b34fb"


def decode_sfloat(raw):
    special_values = {
        0x07FE: "+infinity",
        0x07FF: "NaN",
        0x0800: "not at this resolution",
        0x0801: "reserved",
        0x0802: "-infinity",
    }
    if raw in special_values:
        return special_values[raw]
    mantissa = raw & 0x0FFF
    exponent = raw >> 12
    if mantissa & 0x0800:
        mantissa -= 0x1000
    if exponent & 0x08:
        exponent -= 0x10
    return mantissa * 10**exponent


def decode_measurement(data):
    if not data:
        raise ValueError("empty measurement")
    flags = data[0]
    offset = 1

    def take(fmt):
        nonlocal offset
        size = struct.calcsize(fmt)
        if offset + size > len(data):
            raise ValueError(f"truncated measurement at byte {offset}")
        values = struct.unpack_from(fmt, data, offset)
        offset += size
        return values

    systolic, diastolic, mean = (decode_sfloat(v) for v in take("<HHH"))
    result = {
        "unit": "kPa" if flags & 0x01 else "mmHg",
        "systolic": systolic,
        "diastolic": diastolic,
        "mean arterial pressure": mean,
    }
    if flags & 0x02:
        year, month, day, hour, minute, second = take("<HBBBBB")
        result["timestamp"] = (
            f"{year:04d}-{month:02d}-{day:02d} "
            f"{hour:02d}:{minute:02d}:{second:02d}"
        )
    if flags & 0x04:
        result["pulse (beats/min)"] = decode_sfloat(take("<H")[0])
    if flags & 0x08:
        result["user ID"] = take("<B")[0]
    if flags & 0x10:
        result["measurement status bits"] = f"0x{take('<H')[0]:04x}"
    return result


def on_measurement(_characteristic, data):
    print(f"\nRaw measurement: {data.hex(' ')}")
    try:
        measurement = decode_measurement(data)
    except ValueError as exc:
        print(f"Could not decode measurement: {exc}")
        return
    for name, value in measurement.items():
        print(f"  {name}: {value}")


async def main():
    parser = argparse.ArgumentParser(description="Receive BLE blood pressure measurements")
    parser.add_argument("address", nargs="?", help="Bluetooth address shown by a scan")
    parser.add_argument("--pair", action="store_true", help="pair before connecting (Bleak 1.0+)")
    args = parser.parse_args()

    if not args.address:
        print("Scanning for 15 seconds...")
        for device in await BleakScanner.discover(timeout=15):
            print(f"{device.address}  {device.name or '(no name)'}")
        return

    print(f"Looking for {args.address} for up to 30 seconds...")
    device = await BleakScanner.find_device_by_address(args.address, timeout=30)
    if device is None:
        raise SystemExit("Device not found. Make sure it is advertising, then try again.")

    disconnected = asyncio.Event()
    async with BleakClient(
        device,
        disconnected_callback=lambda _client: disconnected.set(),
        pair=args.pair,
        timeout=60,
    ) as client:
        service = client.services.get_service(BLOOD_PRESSURE_SERVICE)
        if service is None:
            raise RuntimeError("The device does not expose the standard Blood Pressure service (0x1810).")
        characteristic = service.get_characteristic(BLOOD_PRESSURE_MEASUREMENT)
        if characteristic is None or "indicate" not in characteristic.properties:
            raise RuntimeError("Blood Pressure Measurement (0x2A35) with indications was not found.")

        await client.start_notify(characteristic, on_measurement)
        print("Connected and subscribed. Waiting for readings or device disconnect (up to 3 minutes)...")
        try:
            await asyncio.wait_for(disconnected.wait(), timeout=180)
            print("Device disconnected.")
        except asyncio.TimeoutError:
            print("Timed out waiting for the device to disconnect.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
