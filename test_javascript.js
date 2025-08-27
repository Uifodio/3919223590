// Test JavaScript file
function greet(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(value) {
        this.result += value;
        return this;
    }
    
    getResult() {
        return this.result;
    }
}

// Usage
const calc = new Calculator();
console.log(calc.add(5).add(3).getResult());
