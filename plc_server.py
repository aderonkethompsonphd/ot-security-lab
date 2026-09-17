import logging
import threading
import time

from datetime import datetime
from pymodbus.server import StartTcpServer
from pymodbus.datastore import (
            ModbusSequentialDataBlock,
               ModbusSlaveContext,
                    ModbusServerContext,
  )

logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------
# Simulated district-heating PLC
#
# Our lab register map:
# 40001 -> Temperature setpoint
# 40002 -> Actual temperature
# 40003 -> Valve position
# 40004 -> Pump state
# 40005 -> Flow rate
# 40006 -> Alarm state
# --------------------------------------------------

holding_registers = ModbusSequentialDataBlock(
            0,
                [
                            70,  # 40001 Temperature setpoint: 70 C
                                    68,  # 40002 Actual temperature: 68 C
                                            42,  # 40003 Valve position: 42 %
                                                    1,   # 40004 Pump state: ON
                                                            75,  # 40005 Flow rate: 75 %
                                                                    0,   # 40006 Alarm state: NORMAL
                                                                        ],
                )

slave= ModbusSlaveContext(
            hr=holding_registers,
            zero_mode=True
            )

context = ModbusServerContext(
            slaves=slave,
                single=True
                )

# --------------------------------------------------
# Investigator event log
# --------------------------------------------------

event_log = []
previous_setpoint = 70
previous_alarm = 0


def record_event(event_type, message):
    timestamp = datetime.now().strftime("%H:%M:%S")

    event = {
        "time": timestamp,
        "type": event_type,
        "message": message,
    }

    event_log.append(event)

    print(
        f"[EVENT] {timestamp} | "
        f"{event_type:<12} | {message}"
    )

    # Write event to local forensic log
    with open("events.log", "a", encoding="utf-8") as log_file:
        log_file.write(
            f"{timestamp}|{event_type}|{message}\n"
        )

def process_simulation():
    global previous_setpoint, previous_alarm

    while True:
        setpoint = holding_registers.getValues(0, 1)[0]

        # Detect a setpoint change
        if setpoint != previous_setpoint:
            record_event(
                "SETPOINT",
                f"40001 changed: {previous_setpoint} C -> {setpoint} C"
            )

            previous_setpoint = setpoint

        actual = holding_registers.getValues(1, 1)[0]
        valve = holding_registers.getValues(2, 1)[0]

        # 1. Temperature responds to setpoint
        if actual < setpoint:
            actual += 1
        elif actual > setpoint:
            actual -= 1

        holding_registers.setValues(1, [actual])

        # 2. Valve responds to temperature error
        if actual < setpoint:
            valve += 5
        elif actual > setpoint:
            valve -= 5

        # Keep valve between 0% and 100%
        valve = max(0, min(100, valve))
        holding_registers.setValues(2, [valve])

        # 3. Flow follows valve position
        flow = int(valve * 0.9)
        holding_registers.setValues(4, [flow])

        # 4. Alarm logic
        if actual < 50:
            alarm = 1
        else:
            alarm = 0

        holding_registers.setValues(5, [alarm])

        # Record alarm state changes
        if alarm != previous_alarm:
            if alarm == 1:
                record_event(
                    "ALARM",
                    f"LOW TEMPERATURE triggered at {actual} C"
                )
            else:
                record_event(
                    "ALARM",
                    f"LOW TEMPERATURE cleared at {actual} C"
                )

            previous_alarm = alarm

        print(
            f"[PROCESS] "
            f"Setpoint: {setpoint} C | "
            f"Actual: {actual} C | "
            f"Valve: {valve} % | "
            f"Flow: {flow} % | "
            f"Alarm: {'LOW TEMP' if alarm == 1 else 'NORMAL'}"
        )

        time.sleep(2)

simulation_thread = threading.Thread(
    target=process_simulation,
    daemon=True
)

simulation_thread.start()

print("---------------------------------------")
print(" OT Lab - Simulated PLC")
print("---------------------------------------")
print("PLC address : 127.0.0.1")
print("Modbus port : 5020")
print("")
print("40001 Temperature setpoint : 70 C")
print("40002 Actual temperature   : 68 C")
print("40003 Valve position       : 42 %")
print("40004 Pump state           : ON")
print("40005 Flow rate            : 75 %")
print("40006 Alarm state          : NORMAL")
print("")
print("Waiting for Modbus TCP connections...")
print("---------------------------------------")

StartTcpServer(
            context=context,
                address=("127.0.0.1", 5020),
                )
