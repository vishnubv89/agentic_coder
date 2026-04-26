def analyze_data(data):
    """
    Calculates the mean, median, and mode of a list of numbers.
    """
    if not data:
        return "Error: The list is empty."

    # Mean
    mean = sum(data) / len(data)

    # Median
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 1:
        median = sorted_data[n // 2]
    else:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2

    # Mode
    counts = {}
    for item in data:
        counts[item] = counts.get(item, 0) + 1
    
    max_count = max(counts.values())
    modes = [key for key, val in counts.items() if val == max_count]
    
    # Formatting output
    result = (
        f"Data Analysis Results:\n"
        f"----------------------\n"
        f"Mean: {mean:.2f}\n"
        f"Median: {median}\n"
        f"Mode: {', '.join(map(str, modes))}"
    )
    return result

if __name__ == "__main__":
    test_data = [10, 2, 38, 23, 38, 23, 21]
    print(analyze_data(test_data))
