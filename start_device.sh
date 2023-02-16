docker stop device
docker rm device
docker build -t alfalfa-bacnet-bridge .
docker run -it --env-file=.env -p 47808:47808/udp --name="device" -h device alfalfa-bacnet-bridge poetry run python alfalfa_bacnet_bridge/alfalfa_bacnet_bridge.py
