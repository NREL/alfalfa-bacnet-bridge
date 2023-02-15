import BAC0

bacnet = BAC0.connect(ip="172.24.0.4/16")

device = BAC0.device("172.24.0.3", 599, bacnet)

print(device.points)