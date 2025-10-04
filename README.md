<h1 align="center">Evolution of Algebraic Terms (EAT)</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/evolution-of-algebraic-terms.svg)](https://pypi.org/project/evolution-of-algebraic-terms/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## 📖 Overview

Given an *n*-element groupoid *G* and a ternary operation *f* on *G*, **EAT** addresses the problem of finding a ternary term that produces *f*. The difficulty of this problem is that *f* must be found among the (up to) $n^{n^3}$ ternary operations on *G*. For even the small value $n = 3$, that is about ten trillion ($10^{13}$) choices for *f*. For larger values of *n*, that number grows very fast. Using evolutionary computation with 1-parent reproduction, a solution for just the case $n = 3$ was found in 2008 [0] that took a run time of about 5 minutes. **EAT** gives a Python implementation of a new evolutionary algorithm described in [4] *"EAT4: Biological Beam Algorithms"* that uses 2-parent reproduction. It will, for example, find solutions for $n = 7$, with search space sizes up to $10^{290}$, in about 1 minute. In this sense, this is comparable to the transition from 1- to 2-parent reproduction in biological evolution known as the **Cambrian Explosion**.

## 🚀 Installation  
EAT is designed to run as a standalone Command Line Application (CLI). To install it, you'll use **PIP**, the standard package manager for Python, via your computer’s **terminal** (also called “command prompt”).
  
## 🖥️ Opening the Terminal  
### On Windows  
1. Press **Windows key + R**  
2. Type `cmd` and press Enter  
3. You’ll see a black window with a prompt like:  
   `C:\Users\YourName>`  
  
### On Mac  
1. Press **Command + Space** to open Spotlight  
2. Type `terminal` and press Enter  
3. You’ll see a window with a prompt like:  
   `yourname@Your-Mac ~ %`  
   > This is normal! You’re in the terminal. The `%` symbol is just the default prompt in **zsh**, the shell macOS uses.  
  
### On Linux  
1. Press **Ctrl + Alt + T** or search for “Terminal” in your applications  
2. You’ll see a prompt like:  
   `yourname@yourmachine:~$`  
  
## 🧰 Prerequisites  
Before installing EAT, make sure **Python 3.7 or higher** is installed.
  
### ✅ Check Python Installation  
In your terminal, type:  
```bash  
python --version  
```

If that doesn’t work, try:

```bash  
python3 --version  
```

If you see an error like:

```bash
zsh: command not found: python  
```

That means Python isn’t installed or isn’t linked correctly. You can install it by visiting https://www.python.org/downloads and following the instructions for your operating system.

> Mac Tip: After installing Python, you may need to restart your terminal or use `python3` instead of `python`.

> Windows Tip: If you see a message about installing Python from the Microsoft Store, that means Python is not yet installed. You can either visit [python.org](https://www.python.org/downloads) to install it manually (recommended for full control), or [install it directly from the Microsoft Store](https://apps.microsoft.com/detail/9nrwmjp3717k). Be sure to restart your terminal after installation.

## 📦 Installing EAT

Once Python is installed, use PIP to install EAT:

```bash
pip install evolution-of-algebraic-terms
```

If `pip` doesn't work, try:

```bash
python3 -m pip install evolution-of-algebraic-terms
```

If the installation works, your terminal will end with a message like: Successfully installed evolution-of-algebraic-terms. This confirms that EAT is installed. You won’t see a window or icon — just this message in text. That’s normal for command line tools.

From here, you can run EAT by typing:

```bash
eat
```

If that command doesn’t work, try:

```bash
python3 -m eat
```

If successful, EAT will display a help message showing the available options and how to use them. This confirms that the program is installed and ready to accept commands.

## 💡 Usage Examples

> Usage examples placeholder

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions, feedback, or collaboration:

- **David M. Clark** – <a href="mailto:clarkd&#64;newpaltz.edu">clarkd&#64;newpaltz.edu</a>  
- **Nicholas C. Falco** – <a href="mailto:ncfalco&#64;gmail.com">ncfalco&#64;gmail.com</a>

## 📚 References

[0] L. Spector, D. Clark, B. Barr, J. Klein, I. Lindsay, Genetic programming for finite algebras,  
    GECCO 2008 Proceedings, pp 1291-1298.

[1] David M. Clark, Evolution of algebraic terms 1: Term to term operation continuity,  
    International Journal of Algebra and Computation, Vol. 23, No. 5 (2013) 1175–1205.

[2] David M. Clark, Maarten Keijzer, Lee Spector, Evolution of algebraic terms 2: Deep drilling algorithm,  
    International Journal of Algebra and Computation, Vol. 26, No. 6 (2016) 1141–1176.

[3] David M. Clark, Lee Spector, Evolution of algebraic terms 3: evolutionary algorithms,  
    International Journal of Algebra and Computation, Vol. 28, No. 5 (2018).

[4] David M. Clark, Nicholas C. Falco, Evolution of algebraic terms 4: Biological beam algorithms, (in preparation).
