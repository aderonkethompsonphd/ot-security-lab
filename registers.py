from pymodbus.client  import ModbusTcpClient
client = ModbusTcpClient("127.0.0.1", port=5020)
client.connect()
result = client.read_holding_registers(0,6, slave=1)
print(result)
client.close()
print(result.registers)

print("Temperature setpoint:", result.registers[0], "C")
print("Actual temperature:", result.registers[1], "C")
print("Valve position:", result.registers[2], "%")
print("Pump state:", "ON" if result.registers[3] == 1 else "OFF")
print("Flow rate:", result.registers[4], "%")
print("Alarm state:", "NORMAL" if result.registers[5] == 0 else "ALARM")

