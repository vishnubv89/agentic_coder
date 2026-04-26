import math

def analyze_data(data):
    """
    Analyzes a list of numbers and returns a dictionary of statistics.
    
    Args:
        data (list): A list of numeric values.
        
    Returns:
        dict: A dictionary containing count, mean, median, min, max, range, 
              variance, and standard deviation. Returns None if input is invalid.
    """
    if not isinstance(data, list) or not data:
        return None
    
    # Filter out non-numeric values
    numeric_data = [x for x in data if isinstance(x, (int, float))]
    
    if not numeric_data:
        return None
    
    n = len(numeric_data)
    sorted_data = sorted(numeric_data)
    
    # Basic stats
    count = n
    total = sum(numeric_data)
    mean = total / n
    
    # Median
    if n % 2 == 0:
        median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        median = sorted_data[n//2]
        
    # Min/Max/Range
    min_val = sorted_data[0]
    max_val = sorted_data[-1]
    data_range = max_val - min_val
    
    # Variance and Std Dev
    variance = sum((x - mean) ** 2 for x in numeric_data) / n
    std_dev = math.sqrt(variance)
    
    return {
        "count": count,
        "mean": mean,
        "median": median,
        "min": min_val,
        "max": max_val,
        "range": data_range,
        "variance": variance,
        "std_dev": std_dev
    }

if __name__ == '__main__':
    sample_data = [10, 2, 38, 23, 38, 23, 21]
    results = analyze_data(sample_data)
    
    if results:
        print("Statistical Analysis Results:")
        for key, value in results.items():
            print(f"{key.replace('_', ' ').title()}: {value:.4f}")
    else:
        print("Invalid input provided.")
