import time
from pymodbus.client import ModbusTcpClient

HOST = "127.0.0.1"
PORT = 5020
TARGET_ADDRESS = 0
TARGET_VALUE = 30


def verify_state():
    """Reconnect and verify the current value of register 40001."""
    time.sleep(1)

    verify_client = ModbusTcpClient(HOST, port=PORT)

    try:
        if not verify_client.connect():
            print("Could not reconnect to verify PLC state.")
            return False

        result = verify_client.read_holding_registers(
            TARGET_ADDRESS,
            1,
            slave=1
        )

        if result.isError():
            print("Could not verify PLC state:", result)
            return False

        current_value = result.registers[0]

        print(f"Verification read: 40001 = {current_value} C")

        return current_value == TARGET_VALUE

    except Exception as error:
        print("Verification error:", error)
        return False

    finally:
        verify_client.close()


print("---------------------------------------")
print(" OT Lab - Controlled Injector")
print("---------------------------------------")

client = ModbusTcpClient(HOST, port=PORT)

try:
    if not client.connect():
        print("Could not connect to simulated PLC")
        exit()

    print("Connected to simulated PLC")
    print("Sending controlled FC06 write...")
    print("Target: 40001 -> 30 C")
    print()

    try:
        result = client.write_register(
            TARGET_ADDRESS,
            TARGET_VALUE,
            slave=1
        )

        if not result.isError():
            print("FC06 response received.")
            print("Temperature setpoint changed to 30 C.")
        else:
            print("FC06 response reported an error:")
            print(result)
            print()
            print("Checking resulting PLC state...")

            if verify_state():
                print("State verification confirms 40001 = 30 C.")
                print("Write took effect, but acknowledgement was unavailable.")
            else:
                print("Write could not be confirmed.")

    except Exception as error:
        print("FC06 acknowledgement was not received.")
        print(f"Client error: {error}")
        print()
        print("Checking resulting PLC state...")

        if verify_state():
            print("State verification confirms 40001 = 30 C.")
            print("Write took effect, but acknowledgement was unavailable.")
        else:
            print("Write could not be confirmed.")

finally:
    client.close()