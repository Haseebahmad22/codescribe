"""
Test configuration and utilities.
"""
import pytest
import sys
import os


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add src directory to Python path
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing"""
    return '''
def calculate_factorial(n: int) -> int:
    """Calculate the factorial of a number.
    
    Args:
        n (int): The number to calculate factorial for
        
    Returns:
        int: The factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * calculate_factorial(n - 1)


class Calculator:
    """A simple calculator class."""
    
    def __init__(self, initial_value: float = 0):
        """Initialize the calculator.
        
        Args:
            initial_value (float): Initial value for the calculator
        """
        self.value = initial_value
        self.history = []
    
    def add(self, number: float) -> float:
        """Add a number to the current value.
        
        Args:
            number (float): Number to add
            
        Returns:
            float: The new current value
        """
        self.value += number
        self.history.append(('add', number))
        return self.value
    
    def multiply(self, number: float) -> float:
        """Multiply the current value by a number.
        
        Args:
            number (float): Number to multiply by
            
        Returns:
            float: The new current value
        """
        self.value *= number
        self.history.append(('multiply', number))
        return self.value
    
    def get_history(self) -> list:
        """Get the calculation history.
        
        Returns:
            list: List of operations performed
        """
        return self.history.copy()
'''


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing"""
    return '''
/**
 * Calculate the factorial of a number
 * @param {number} n - The number to calculate factorial for
 * @returns {number} The factorial of n
 */
function calculateFactorial(n) {
    if (n < 0) {
        throw new Error("Factorial is not defined for negative numbers");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * calculateFactorial(n - 1);
}

/**
 * A simple calculator class
 */
class Calculator {
    /**
     * Create a calculator
     * @param {number} initialValue - Initial value for the calculator
     */
    constructor(initialValue = 0) {
        this.value = initialValue;
        this.history = [];
    }
    
    /**
     * Add a number to the current value
     * @param {number} number - Number to add
     * @returns {number} The new current value
     */
    add(number) {
        this.value += number;
        this.history.push(['add', number]);
        return this.value;
    }
    
    /**
     * Multiply the current value by a number
     * @param {number} number - Number to multiply by
     * @returns {number} The new current value
     */
    multiply(number) {
        this.value *= number;
        this.history.push(['multiply', number]);
        return this.value;
    }
    
    /**
     * Get the calculation history
     * @returns {Array} List of operations performed
     */
    getHistory() {
        return [...this.history];
    }
}
'''


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'ai': {
            'provider': 'openai',
            'openai': {
                'api_key': 'test-key',
                'model': 'gpt-3.5-turbo',
                'max_tokens': 500,
                'temperature': 0.3
            }
        },
        'documentation': {
            'verbosity': 'medium',
            'style': 'google',
            'include_examples': True,
            'include_parameters': True,
            'include_return_values': True,
            'include_exceptions': True
        },
        'processing': {
            'batch_size': 5,
            'max_file_size_mb': 2,
            'skip_files': ['*.pyc', '__pycache__/*'],
            'supported_extensions': ['.py', '.js', '.ts']
        }
    }