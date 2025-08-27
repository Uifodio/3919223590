#!/usr/bin/env python3
"""
Test Python file for Anora Editor
"""

def hello_world():
    """Simple hello world function"""
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
    test = TestClass()
    print(f"Value: {test.get_value()}")
