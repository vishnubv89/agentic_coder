import psutil
import time

def get_cpu_usage():
    """
    Retrieves the current CPU utilization percentage.
    psutil.cpu_percent(interval=1) blocks for 1 second to calculate the usage.
    """
    return psutil.cpu_percent(interval=1)

if __name__ == "__main__":
    try:
        print("Monitoring CPU usage... (Press Ctrl+C to stop)")
        while True:
            usage = get_cpu_usage()
            print(f"CPU Usage: {usage}%")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
