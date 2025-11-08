<h1 align="center">Evolution of Algebraic Terms (EAT)</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/evolution-of-algebraic-terms.svg)](https://pypi.org/project/evolution-of-algebraic-terms/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**David M. Clark** (<a href="mailto:clarkd&#64;newpaltz.edu">clarkd&#64;newpaltz.edu</a>)<br/>
**Nicholas C. Falco** (<a href="mailto:ncfalco&#64;gmail.com">ncfalco&#64;gmail.com</a>)

</div>

Given an n-element groupoid **G** $= ⟨G, ∗⟩$ and a ternary operation $f$ on $G$, EAT addresses the problem of finding a ternary term $t(x, y, z)$ whose term operation is $f$. The difficulty of this problem is that $f$ must be found among the (up to) $n^{n^3}$ ternary operations on **G**. For even the small value $n = 3$, that is about ten trillion ($10^{13}$) choices for $f$. For larger values of $n$, the search space is so large that finding $t(x, y, z)$ by any conventional search is computationally unfeasible. Using evolutionary computation with 1-parent reproduction, a solution for just the case
$n = 3$ was found in 2008 [6] that took a run time of about 5 minutes. EAT gives a Python implementation of a new evolutionary algorithm described in [4] “EAT4: Biological Beam Algorithms” that uses 2-parent reproduction. It will, for example, evolve solutions for $n = 7$, with search space sizes up to $10^{290}$, in about a minute. In this sense, this is comparable to the transition from 1- to 2-parent reproduction in biological evolution known as the **Cambrian Explosion**.

# 1. Installation  
**EAT** is a standalone Command Line Application. To install it, you need a command line **terminal** and a current version of **Python**.

## Install the Terminal
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
  
### On Linux  
1. Press **Ctrl + Alt + T** or search for “Terminal” in your applications  
2. You’ll see a prompt like:  
   `yourname@yourmachine:~$`  

## Install Python
If your computer does not already have **Python 3.7 or higher** installed, you will need to install it. To find out what version, if any, you already have,
enter either “python –version” or “python3 –version”, (return). To install a current version, go to https://www.python.org/downloads and following the
instructions for your operating system.

- **For Mac and Linux:** After installing Python, you may need to restart your terminal
or use python3 instead of python.
- **For Windows:** A message about installing Python from the Microsoft Store means Python is not yet installed. You can either visit python.org to
install it manually (recommended) or install it directly from the Microsoft Store. Be sure to restart your terminal after installation.

## Install EAT

Once Python is installed, you can install EAT by entering:

```bash
pip install evolution-of-algebraic-terms
```

If that doesn’t work, try:

```bash
python3 -m pip install evolution-of-algebraic-terms
```

If the instillation is successful, you will get a confirmation message. You can then activate EAT by entering either `eat` or `python3 -m eat`.

Once EAT is installed you will be ready to use the EAT programs.

# 2. EAT Programs

The algorithms for the EAT programs were developed in the publications [1], [2], [3], [4] and [5], culminating in [4] that includes a summary of the others. EAT offers access to the three most successful programs:

- the Deep Drilling Algorithm (**DDA**) of [2],  
- the Female Beam Algorithm (**FBA**) of [4] and  
- the Male-Female Beam Algorithm (**MFBA**) of [4].  

An EAT program takes, as input, a **groupoid**, a **target operation** that is a term operation of that groupoid and one of the three **algorithms**. An n-element groupoid is specified by listing the entries in its table from left to right and then top to bottom. EAT has three ways to specify a target operation:  

- `-tdt` the ternary discriminator operation $d(a, b, c) = c$ if $a = b$, else $a$
- `-trt` a random operation, by listing its values at each triple 
- `-t` a user chosen operation, by listing its values at each triple.  

For example, try entering `eat -g 2 1 2 1 0 0 0 0 1 -a MFBA -tdt, (return)`. EAT will use the 3-element groupoid $A_1 = 2 1 2 1 0 0 0 0 1$ and run the MFBA with the ternary discriminator operation as target. Well within a second it will find a term that represents the discriminator operation from among the $10^{13}$ operations represented by terms in the variables $x$, $y$ and $z$. Under that it will report the variable length of that term and the run time in seconds. After that it will confirm that it found a discriminator term by calculating the ternary discriminator operation and the term operation of that term to show that they are the same. You can replace `-a MFBA` with either `-a FBA` or `-a DDA` and replace `-tdt` with either `-trt` or your own chosen ternary operation to get similar results. For example, try entering `eat -g 1 2 0 1 2 2 0 1 0  -a DDA  -t 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1`.

A central theme of the EAT publications referenced below, summarized in [4], is to determine which finite groupoids will yield terms with these algorithms. Experimental and theoretical evidence indicates that the proportion of n-element groupoids that do grows quickly with n and appears to approach one as n gets large, but takes rapidly more run time as n grows larger. Figure 17 in [4] gives a sense of this by looking at ten random groupoids of sizes 3, 5 and 7. Using the MFBA, 30% were successful for n = 3, 60% for n = 5 and 90% for n = 7. Using the DDA the percents are slightly smaller and the term sizes much larger. The FBA, a stepping stone to the MFBA, could not find terms for n > 4 in an acceptable time frame. Entering just `eat <return>` will give other command line options that can be used.

# 3. Choice of Targets

Given a finite groupoid **G** $= ⟨G, ∗⟩$ and a ternary operation $f$ on $G$, it is often the case that there is _no_ term $t(x, y, z)$ that represents $f$ on **G**. But it turns out that a simple observation allows us to avoid almost all of these cases. An element $e \in G$ is an **idempotent** of **G** if $e ∗ e = e$. If $e$ is an idempotent, then, for every term $t(x, y, z)$, we have $t(e, e, e) = e$. Consequently, if $f(e, e, e) \neq e$, then there is _no_ term representing $f$ on **G**.

We say that $f$ **preserves idempotents** on **G** if $f(e, e, e) = e$ for every idempotent $e$. A famous theorem of V. L. Murskı̆ı [5] says that, for almost all finite groupoids, every operation that preserves idempotents is represented by some term. This is not true of many 3-element groupoids. But the proportion of groupoids for which it is true grows rapidly with their size. It is true for about $90\%$ of 7-element groupoids and the proportion for which it is true grows rapidly toward $100\%$ beyond size 7. As a result, it is easy to find groupoids **G** and operations $f$ that are represented by some term on **G**.

The EAT programs use this idea with the three methods of specifying target operations. Using `-tdt`, the discriminator operation $d$ preserves idempotents since $d(a, a, a) = a$ for all $a \in G$. When `-trt` is used, random values are assigned to all triples except idempotent triples $(e, e, e)$, which are assigned value $e$. When `−t` is used, an error message is produced if some idempotent triple $(e, e, e)$ is assigned something other than e. In this way users will usually be looking at groupoids **G** with target operations $f$ that are represented by some term and almost always when the they are looking at larger groupoids.

# 4. References

[1] David M. Clark. *Evolution of algebraic terms 1: Term to term operation continuity*. International Journal of Algebra and Computation, Vol. 23, No. 5 (2013), pp. 1175–1205.

[2] David M. Clark, Maarten Keijzer, Lee Spector. *Evolution of algebraic terms 2: Deep drilling algorithm*. International Journal of Algebra and Computation, Vol. 26, No. 6 (2016), pp. 1141–1176.

[3] David M. Clark, Lee Spector. *Evolution of algebraic terms 3: Term continuity and beam algorithms*. International Journal of Algebra and Computation, Vol. 28, No. 5 (2018).

[4] David M. Clark, Nicholas C. Falco. *Evolution of algebraic terms 4: Biological beam algorithms*. (in preparation).

[5] V. L. Murskı̆ı. *A finite basis of identities and other properties of “almost all” finite algebras*. Problémy Kibérnetiki, Vol. 30 (1975), pp. 43–56.

[6] L. Spector, D. Clark, B. Barr, J. Klein, I. Lindsay. *Genetic programming for finite algebras*. GECCO 2008 Proceedings, pp. 1291–1298. (First place winner in 2008 Hummie Competition.)
