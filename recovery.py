from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", port=5020)

if client.connect():
    print("---------------------------------------")
    print(" OT Lab - Recovery")
    print("---------------------------------------")
    print("Connected to simulated PLC")

    result = client.write_register(0, 70, slave=1)

    if result.isError():
        print("Recovery write failed:", result)
    else:
        print("Recovery FC06 write accepted")
        print("Temperature setpoint restored to 70 C")

    client.close()
else:
    print("Could not connect to simulated PLC")