# Alfalfa-BACnet-Bridge
 A simple utility which exposes [alfalfa](https://github.com/NREL/alfalfa) points as BACnet points 


## Installing
Alfalfa-BACnet-Bridge only requires [docker](https://www.docker.com/)

## Usage

### Running the Bridge
The following command will run the BACnet Alfalfa Bridge using the image from the github package.
```bash
# Pull latest image
docker pull ghcr.io/nrel/alfalfa-bacnet-bridge:latest
# Run Image
docker run \
    --detach \
    -e ALFALFA_SITE=<alfalfa_site> \
    -e ALFALFA_HOST=<alfalfa_host> \
    -p 47808:47808/udp \
    ghcr.io/nrel/alfalfa-bacnet-bridge:latest
```

### Environment Variables
These are variables used to describe the bridge's connection to Alfalfa.
| Variable | Description | Default |
| --- | -------- | --- |
| `ALFALFA_SITE` | The Alfalfa Site ID of the model of interest or an alias which points to a site of interest | MUST BE SET |
| `ALFALFA_HOST` | The URL of the Alfalfa instance | MUST BE SET |
| `ALFALFA_DEVICE_NAME` | The name of the BACnet device | `AlfalfaProxy` |
| `ALFALFA_DEVICE_ID` | The ID of the BACnet device | `599` |

When the specified `ALFALFA_SITE` is an alias the bridge will automatically switch sites when the alias is updated.

## Development

### Building and Starting Device
1. Edit `.env` to reflect desired Alfalfa `host` and `site_id`
1. Start device `./start_device.sh`

### Using CLI
For development it is useful to be able to connect to your device from the same computer. 
The CLI is a python REPL with precreates a [BAC0](https://bac0.readthedocs.io/en/latest/) `network` which the user can interact with.

1. Start cli `./start_cli.sh`
#### Example: Getting points from device
```2023-02-16 00:14:06,844 - INFO    | Starting BAC0 version 22.9.21 (Lite)
2023-02-16 00:14:06,845 - INFO    | Use BAC0.log_level to adjust verbosity of the app.
2023-02-16 00:14:06,845 - INFO    | Ex. BAC0.log_level('silence') or BAC0.log_level('error')
2023-02-16 00:14:06,845 - INFO    | Starting TaskManager
2023-02-16 00:14:06,846 - INFO    | Using ip : 172.17.0.3
2023-02-16 00:14:06,877 - INFO    | Starting app...
2023-02-16 00:14:06,878 - INFO    | BAC0 started
2023-02-16 00:14:06,878 - INFO    | Registered as Simple BACnet/IP App
2023-02-16 00:14:06,881 - INFO    | Update Local COV Task started
>>> device = BAC0.device("<device address>", <device_id>, network)
2023-02-16 00:14:24,958 - INFO    | Changing device state to DeviceDisconnected'>
2023-02-16 00:14:24,978 - INFO    | Changing device state to RPMDeviceConnected'>
2023-02-16 00:14:25,000 - INFO    | Device 599:[AlfalfaProxy] found... building points list
2023-02-16 00:14:25,289 - INFO    | Ready!
2023-02-16 00:14:25,289 - INFO    | Device defined for normal polling with a delay of 10sec
2023-02-16 00:14:25,289 - INFO    | Polling started, values read every 10 seconds
>>> device.points
[AlfalfaProxy/OfficeSmall HTGSETP_SCH_NO_OPTIMUM : 10.00 None, AlfalfaProxy/OfficeSmall CLGSETP_SCH_NO_OPTIMUM : 12.00 None, AlfalfaProxy/Core_ZN_ZN_PSZ_AC_1_Outside_Air_Damper_CMD : 0.00 None, AlfalfaProxy/MasterEnable : 0.00 None, AlfalfaProxy/Perimeter_ZN_1_ZN_PSZ_AC_2_Outside_Air_Damper_CMD : 0.00 None, AlfalfaProxy/Perimeter_ZN_2_ZN_PSZ_AC_3_Outside_Air_Damper_CMD : 0.00 None, AlfalfaProxy/Perimeter_ZN_3_ZN_PSZ_AC_4_Outside_Air_Damper_CMD : 0.00 None, AlfalfaProxy/Perimeter_ZN_4_ZN_PSZ_AC_5_Outside_Air_Damper_CMD : 0.00 None, AlfalfaProxy/Whole Building Electricity : 205783.22 None, AlfalfaProxy/Whole Building NaturalGas : 0.00 None, AlfalfaProxy/Perimeter_ZN_4 ZN Air Temperature : 17.06 None, AlfalfaProxy/Perimeter_ZN_4 ZN Humidity : 37.02 None, AlfalfaProxy/Perimeter_ZN_4 ZN Temperature Setpoint : 12.00 None, AlfalfaProxy/Perimeter_ZN_3 ZN Air Temperature : 17.28 None, AlfalfaProxy/Perimeter_ZN_3 ZN Humidity : 32.61 None, AlfalfaProxy/Perimeter_ZN_3 ZN Temperature Setpoint : 12.00 None, AlfalfaProxy/Perimeter_ZN_2 ZN Air Temperature : 17.02 None, AlfalfaProxy/Perimeter_ZN_2 ZN Humidity : 37.24 None, AlfalfaProxy/Perimeter_ZN_2 ZN Temperature Setpoint : 12.00 None, AlfalfaProxy/Perimeter_ZN_1 ZN Air Temperature : 17.49 None, AlfalfaProxy/Perimeter_ZN_1 ZN Humidity : 34.49 None, AlfalfaProxy/Perimeter_ZN_1 ZN Temperature Setpoint : 12.00 None, AlfalfaProxy/Core_ZN ZN Air Temperature : 18.89 None, AlfalfaProxy/Core_ZN ZN Humidity : 23.15 ...