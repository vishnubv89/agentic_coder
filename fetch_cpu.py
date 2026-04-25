import requests
import json
import csv
import time

# Configuration
API_URL = "https://<YOUR_ENVIRONMENT_ID>.live.dynatrace.com"
API_TOKEN = "<YOUR_API_TOKEN>"
HEADERS = {
    "Authorization": f"Api-Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_all_hosts():
    """Fetches all monitored hosts."""
    hosts = []
    next_page_key = None
    
    url = f"{API_URL}/api/v2/entities"
    params = {
        "entitySelector": "type(HOST)",
        "pageSize": 100
    }
    
    while True:
        if next_page_key:
            params["nextPageKey"] = next_page_key
            
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Error fetching hosts: {response.text}")
            break
            
        data = response.json()
        hosts.extend(data.get("entities", []))
        
        next_page_key = data.get("nextPageKey")
        if not next_page_key:
            break
            
    return hosts

def get_cpu_usage_dql(host_ids):
    """Executes DQL to get CPU usage for a list of host IDs."""
    # DQL query to get average CPU usage for the last 5 minutes
    # Note: We filter by the list of host IDs
    host_filter = " OR ".join([f'entity.id == "{hid}"' for hid in host_ids])
    query = f"""
    fetch metrics
    | filter metric.key == "builtin:host.cpu.usage"
    | filter {host_filter}
    | summarize avg = avg(value), by: {{"entity.id"}}
    | sort avg desc
    """
    
    url = f"{API_URL}/api/v2/dql/execute"
    payload = {"query": query}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print(f"Error executing DQL: {response.text}")
        return []

def main():
    print("Fetching hosts...")
    hosts = get_all_hosts()
    if not hosts:
        print("No hosts found.")
        return
    
    host_ids = [h["entityId"] for h in hosts]
    host_map = {h["entityId"]: h.get("displayName", h["entityId"]) for h in hosts}
    
    print(f"Found {len(host_ids)} hosts. Fetching CPU metrics...")
    
    # DQL can handle multiple entities, so we can process in batches if needed
    # For simplicity, we process all in one query if the list isn't too large
    results = get_cpu_usage_dql(host_ids)
    
    # Output to CSV
    with open('host_cpu_usage.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Host Name', 'Host ID', 'Average CPU Usage (%)'])
        
        for row in results:
            host_id = row.get("entity.id")
            avg_cpu = row.get("avg")
            writer.writerow([host_map.get(host_id, host_id), host_id, round(avg_cpu, 2)])
            
    print("Results saved to host_cpu_usage.csv")

if __name__ == "__main__":
    main()
