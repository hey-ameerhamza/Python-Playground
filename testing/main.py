from datetime import datetime
from time import sleep


def main() -> None:
	try:
		while True:
			current_time = datetime.now().strftime("%I:%M:%S %p")
			print(f"\r{current_time}", end="", flush=True)
			sleep(1)
	except KeyboardInterrupt:
		print()


if __name__ == "__main__":
	main()
