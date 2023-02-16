import BAC0
import subprocess

result = subprocess.run(["hostname", "-I"], capture_output=True)
address = result.stdout.decode("utf-8").strip()

network = BAC0.connect(f"{address}/16")