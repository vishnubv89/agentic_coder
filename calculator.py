def calculator(a, b, operation):
    """
    A simple calculator function that performs basic arithmetic operations.
    
    :param a: First number
    :param b: Second number
    :param operation: Operation to perform ('+', '-', '*', '/')
    :return: Result of the operation
    """
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Invalid operation"

# Example usage:
if __name__ == "__main__":
    print("10 + 5 =", calculator(10, 5, '+'))
    print("10 - 5 =", calculator(10, 5, '-'))
    print("10 * 5 =", calculator(10, 5, '*'))
    print("10 / 5 =", calculator(10, 5, '/'))
