docker stop cli
docker rm cli
docker build -t alfalfa-bacnet-bridge .
docker run -it --name="cli" -h cli alfalfa-bacnet-bridge poetry run python -i cli_setup.py
