<h1 align="center">Evolution of Algebraic Terms (EAT)</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/evolution-of-algebraic-terms.svg)](https://pypi.org/project/evolution-of-algebraic-terms/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*Automated digital circuit design using biological beam algorithms*

</div>

## 📖 Overview

EAT is a Python implementation of the algorithms described in the research paper "Evolution of Algebraic Terms 4: Biological Beam Algorithms." Given an arbitrary performance specification, the program systematically designs digital circuits using binary logic on groupoids of size 3 or larger. The program's success is documented by its ability to consistently find such designs from an incredibly vast search space in fractions of a second.

## 🏗️ Project Structure
```
eat/
├── README.md                 # Project documentation
├── setup.py                  # Package installation
└── eat/                      # Main package
    ├── runeat.py             # Main entry point
    ├── core/                 # Core mathematical components
    ├── beam_algorithm/       # Biological beam algorithms
    ├── deep_drilling_algorithm/  # Deep drilling algorithms
    ├── utilities/            # Helper functions
    ├── tests/                # Test suite
    └── static/               # Static resources
```


## 🚀 Installation

### Prerequisites

- **Python 3.7 or higher** ([Download Python](https://python.org/downloads/))
- **pip** (usually comes with Python)

Check your Python version:
```bash
python --version
```

### Installation Options

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

For usage examples please see https://github.com/nick-falco/eat/wiki.

## 🔧 Troubleshooting

### Common Issues

**Import Error:**
```
ModuleNotFoundError: No module named 'eat'
```
*Solution:* `pip install evolution-of-algebraic-terms`


## 📖 Documentation

- **📘 [EAT Wiki](https://github.com/nick-falco/eat/wiki)** - Comprehensive program documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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


---

