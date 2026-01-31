# devices.py

class Device:
    def __init__(self, name, dev_eui, dev_addr, app_eui, gateway_eui):
        self.name = name
        self.dev_eui = dev_eui
        self.dev_addr = dev_addr
        self.app_eui = app_eui
        self.gateway_eui = gateway_eui

# List of supported devices
devices = [
    Device("Dragino DDS75-LB Ultrasonic Distance Sensor", "64-bit-DevEUI-1", "32-bit-DevAddr-1", "64-bit-AppEUI-1", "64-bit-GatewayEUI-1"),
    Device("Makerfabs Soil Moisture Sensor", "64-bit-DevEUI-2", "32-bit-DevAddr-2", "64-bit-AppEUI-2", "64-bit-GatewayEUI-2"),
    Device("SW3L Water Meter", "64-bit-DevEUI-3", "32-bit-DevAddr-3", "64-bit-AppEUI-3", "64-bit-GatewayEUI-3"),
    Device("EM500-UDL", "64-bit-DevEUI-4", "32-bit-DevAddr-4", "64-bit-AppEUI-4", "64-bit-GatewayEUI-4"),
    Device("Multitech RBS301 Temp Sensor", "64-bit-DevEUI-5", "32-bit-DevAddr-5", "64-bit-AppEUI-5", "64-bit-GatewayEUI-5"),
    Device("rbs305-ath", "64-bit-DevEUI-6", "32-bit-DevAddr-6", "64-bit-AppEUI-6", "64-bit-GatewayEUI-6"),
    Device("rbs301-dws", "64-bit-DevEUI-7", "32-bit-DevAddr-7", "64-bit-AppEUI-7", "64-bit-GatewayEUI-7"),
]

def get_device_info(device_name):
    for device in devices:
        if device.name == device_name:
            return {
                "DevEUI": device.dev_eui,
                "DevAddr": device.dev_addr,
                "AppEUI": device.app_eui,
                "GatewayEUI": device.gateway_eui
            }
    return None