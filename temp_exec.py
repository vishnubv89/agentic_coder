def analyze_data(numbers):
    if not numbers:
        return "Error: The list is empty."

    # Mean
    mean = sum(numbers) / len(numbers)

    # Median
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 1:
        median = sorted_numbers[n // 2]
    else:
        median = (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2

    # Mode
    counts = {}
    for num in numbers:
        counts[num] = counts.get(num, 0) + 1
    
    max_count = max(counts.values())
    modes = [num for num, count in counts.items() if count == max_count]
    
    # Format results
    mode_str = ", ".join(map(str, modes)) if len(modes) < len(counts) else "No unique mode"
    
    return f"Mean: {mean:.2f}, Median: {median}, Mode: {mode_str}"

if __name__ == "__main__":
    sample_data = [10, 2, 38, 23, 38, 23, 21]
    result = analyze_data(sample_data)
    print(f"Data: {sample_data}")
    print(result)
