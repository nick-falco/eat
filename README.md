<h1 align="center">Evolution of Algebraic Terms (EAT)</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/evolution-of-algebraic-terms.svg)](https://pypi.org/project/evolution-of-algebraic-terms/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*Automated digital circuit design using biological beam algorithms*

</div>

## 📖 Overview

EAT is a Python implementation of the algorithms described in the research paper "Evolution of Algebraic Terms 4: Biological Beam Algorithms." Given an arbitrary performance specification, the program systematically designs digital circuits using binary logic on groupoids of size 3 or larger. The program's success is documented by its ability to consistently find such designs from an incredibly vast search space in fractions of a second.

## 🚀 Installation

EAT designed to be run as a stand alone Command Line Application (CLI). To install it you will
need to open the command line (terminal) on your computer and use PIP, the standard package manager for Python.

### What is a Command Line Application?
A command line application is a program you run by typing commands in a text-based interface called a "terminal" or "command prompt." Instead of clicking buttons with your mouse, you type instructions and press Enter. Think of it like having a conversation with your computer using text commands.

### How to Open the Terminal
#### On Windows:
1. Press Windows key + R
2. Type cmd and press Enter
3. A black window will open - this is your command prompt

#### On Mac:
1. Press Command + Space to open Spotlight
2. Type terminal and press Enter
3. A window will open - this is your terminal

#### On Linux:
1. Press Ctrl + Alt + T or search for "Terminal" in your applications

### Prerequisites

- **Python 3.7 or higher** ([Download Python](https://python.org/downloads/))
- **pip** (usually comes with Python)

Check your Python version by typing the following on the terminal and clicking ENTER on your keyboard:
```bash
python --version
```

### Installation Options

To install choose the option that best suits you and type the commands on the terminal. Submit each command by pressing ENTER on your keyboard.

#### Option 1: Simple Install (Recommended)
```bash
pip install evolution-of-algebraic-terms
```

#### Option 2: Development Install
For modifying the code:
```bash
git clone https://github.com/nick-falco/eat.git
cd eat
pip3 install -e .
```
Or:
```bash
python3 setup.py develop
```

#### Option 3: Virtual Environment (Best Practice)
```bash
# Create virtual environment
python -m venv env

# Activate it
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# Install EAT
pip install evolution-of-algebraic-terms
```

### Verify Installation
```bash
python -c "import eat; print('EAT installed successfully!')"
```

## 💡 Usage

Please see the **📘 [EAT Wiki](https://github.com/nick-falco/eat/wiki)** for detailed program usage examples.

## 🔧 Troubleshooting

### Common Issues

**Import Error:**
```
ModuleNotFoundError: No module named 'eat'
```
*Solution:* `pip install evolution-of-algebraic-terms`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏗️ Project Structure
The source code for this project is organized as follows:
```
eat/
├── README.md                 # Project documentation
├── LICENSE                   # Project usage license
├── setup.py                  # Package installation
└── eat/                      # Main package
    ├── runeat.py             # Main entry point
    ├── core/                 # Core mathematical components
    ├── beam_algorithm/       # Biological beam algorithms
    ├── deep_drilling_algorithm/  # Deep drilling algorithm
    ├── utilities/            # Helper functions
    ├── tests/                # Test suite
```

## 📚 References

[0] L. Spector, D. Clark, B. Barr, J. Klein, I. Lindsay, Genetic programming for finite algebras,  
    GECCO 2008 Proceedings, pp 1291-1298.

[1] David M. Clark, Evolution of algebraic terms 1: Term to term operation continuity,  
    International Journal of Algebra and Computation, Vol. 23, No. 5 (2013) 1175–1205.

[2] David M. Clark, Maarten Keijzer, Lee Spector, Evolution of algebraic terms 2: Deep drilling algorithm,  
    International Journal of Algebra and Computation, Vol. 26, No. 6 (2016) 1141–1176.

[3] David M. Clark, Lee Spector, Evolution of algebraic terms 3: evolutionary algorithms,  
    International Journal of Algebra and Computation, Vol. 28, No. 5 (2018).

[4] David M. Clark, Nicholas C. Falco, Evolution of algebraic terms 4, Biological beam algorithms, (in preparation).
