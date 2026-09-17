
from pymodbus.client import ModbusTcpClient

client =ModbusTcpClient("127.0.0.1", port=5020)

if client.connect():
    print("Connected to simulated PLC")

    #register 4001 / address 0 = temperature
    result = client.write_register(0, 72, slave=1)

    if result.isError():
        print("Write failed:", result)
    else:
        print("Operator changed temperature setpoint to 72 C")

    client.close()
else:
    print("Could not connect to siulated PLC")
