import os
import time
from pymodbus.client import ModbusTcpClient







client = ModbusTcpClient("127.0.0.1", port=5020)

if not client.connect():
    print("Could not connect to simulated PLC")
    exit()

try:
    while True:
        result = client.read_holding_registers(0, 6, slave=1)

       
        if result.isError():
            print("Error reading PLC:", result)
            time.sleep(2)
            continue

        registers = result.registers

        setpoint = registers[0]
        actual = registers[1]
        valve = registers[2]
        pump = registers[3]
        flow = registers[4]
        alarm = registers[5]

        # Clear terminal
        os.system("cls" if os.name == "nt" else "clear")

        print("=======================================")
        print(" DISTRICT HEATING - OPERATOR DASHBOARD")
        print("=======================================")
        print()
        print(f" Temperature Setpoint : {setpoint} C")
        print(f" Actual Temperature   : {actual} C")
        print(f" Valve Position       : {valve} %")
        print(f" Pump State           : {'ON' if pump == 1 else 'OFF'}")
        print(f" Flow Rate            : {flow} %")
        print()
        print("---------------------------------------")

        if alarm == 0:
            print(" SYSTEM STATUS: NORMAL")
        else:
            print(" SYSTEM STATUS: LOW TEMPERATURE")

        print("---------------------------------------")
        print()
        print("Monitoring PLC... Press Ctrl+C to stop.")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nDashboard stopped.")

finally:
    client.close()
