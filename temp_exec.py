import psutil
import time

# We will run the function once to verify it works, 
# instead of running the infinite loop.
def get_cpu_usage():
    return psutil.cpu_percent(interval=0.1)

try:
    usage = get_cpu_usage()
    print(f"CPU Usage: {usage}%")
except Exception as e:
    print(f"An error occurred: {e}")
