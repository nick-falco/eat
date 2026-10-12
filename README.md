<h1 align="center">Evolution of Algebraic Terms (EAT)</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/evolution-of-algebraic-terms.svg)](https://pypi.org/project/evolution-of-algebraic-terms/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**David M. Clark** (<a href="mailto:clarkd&#64;newpaltz.edu">clarkd&#64;newpaltz.edu</a>)<br/>
**Nickolas C. Falco** (<a href="mailto:ncfalco&#64;gmail.com">ncfalco&#64;gmail.com</a>)

</div>

Given an $n$-element groupoid **$G = \langle G, \ast \rangle$** and a ternary operation $f$ on $G$, EAT addresses the problem of finding a ternary term $t(x, y, z)$ whose term operation is $f$. The term $t(x, y, z)$ can be viewed as a design for a switching circuit that calculates the values of $f$. The difficulty of this problem is that $f$ must be found from among the (up to) $n^{n^3}$ ternary operations on $G$. For even the small value $n = 3$, that is about ten trillion ($10^{13}$) choices for $f$. For larger values of $n$, the search space is so large that finding $t(x, y, z)$ by any conventional search is computationally unfeasible. Using evolutionary computation with 1-parent reproduction, a solution for just the case $n = 3$ was found in 2008 [7] that took a run time of about 5 minutes. EAT gives a Python implementation of a new evolutionary algorithm, the **Male-Female Beam Algorithm (MFBA)** of [4], that is modeled after biological evolution using 2-parent reproduction. It will, for example, evolve solutions for $n = 7$, with search space sizes up to $10^{290}$, in about a minute. In this sense, the advent of the MFBA parallels the transition from 1- to 2-parent reproduction in biological evolution that was firmly in place during the Cambrian Explosion.

# 1. Installations

EAT is a standalone Command Line Application. To install it, you need a command line **terminal** and a current version of Python.

## Install the Terminal

### On Windows

1. Press Windows key + R.
2. Type `cmd` and press Enter.
3. You'll see a black window with: `C:\Users\YourName>`.

### On Mac

1. Press Command + Space to open Spotlight.
2. Type `terminal` and press Enter.
3. You will see a window with: `yourname@Your-Mac ~ %`.

### On Linux

1. Press Ctrl + Alt + T or search for Terminal in your applications.
2. You will see a prompt like: `yourname@yourmachine:~$`.

## Install Python

If your computer does not already have **Python 3.7 or higher** installed, you will need to install it. To find out what version, if any, you already have, enter either `python --version` or `python3 --version`, (return). To install a current version, go to <https://www.python.org/downloads> and following the instructions for your operating system.

For Mac: After installing Python, you may need to restart your terminal or use python3 instead of python.

For Windows: A message about installing Python from the Microsoft Store means Python is not yet installed. You can either visit python.org to install it manually (recommended) or install it directly from the Microsoft Store. Be sure to restart your terminal after installation.

## Install EAT

Once Python is installed, you can install EAT by entering

```text
pip install evolution-of-algebraic-terms
```

If that doesn't work, try

```text
python3 -m pip install evolution-of-algebraic-terms
```

If the instillation is successful, you will get a confirmation message. You can then activate EAT by entering either

```text
eat or python3 -m eat
```

Once EAT is installed you will be ready to use the EAT programs.

# 2. EAT Programs

The algorithms for the EAT programs that evolve terms were developed in the publications [1], [2], [3] and [4], culminating in the

<p align="center"><strong>Male-Female Beam Algorithm (MFBA)</strong></p>

of [4], which builds on and summarizes the Deep Drilling Algorithm (**DDA**) of [2], the Beam Enumeration Algorithm (**BEA**) of [3] and The Female Beam Algorithm (**FBA**) of [4].

The MFBA takes as input a **finite groupoid** and a **target operation** that is a term operation of that groupoid. It then tries to find a term that has that target operation as its term operation. For example, consider the 3-element primal groupoid **$A$** with rows $212$, $100$ and $001$ from top to bottom in its $\ast$-table. You can enter the **target command -t** at the terminal:

```text
eat -g 2 1 2 1 0 0 0 0 1 -a MFBA -t 2 0 1 1 2 . . . . . . 2 0 2 0 1
```

This command will invoke the (**-a**) MFBA to use the (**-g**) groupoid **$A = 212\ 100\ 001$** to try to evolve a (**-t**) target groupoid term whose term operation is the operation with values

```text
(0, 0, 0)→2, (0, 0, 1)→0, (0, 0, 2)→1, (0, 1, 0)→1, (0, 1, 1)→2, . . . ,(2, 2, 2)→1.
```

Here "MFBA" can be replaced by either "FBA" or "DDA" and **-t** can be followed by any 27 values from {0, 1, 2} that you choose. If you find entering 27 random values tedious, you can instead use the **random target command** **-trg**. Just enter

```text
eat -g 2 1 2 1 0 0 0 0 1 -a MFBA -trg
```

and let the program produce a randomly generated target operation for you.

# 3. Choice of Groupoids and Target Operations

In order to use our programs effectively you will need to know something about which groupoids will yield terms with them and which target operations are term operations of those groupoids. Answering these questions is a central theme of the EAT publications referenced below, summarized in [4]. We do not have an absolute test that is guaranteed to identify the groupoids that yield terms. But it appears that almost all do and that two simple tests will usually identify those groupoids.

**Asymptotic Completeness Test.** Our first test is done by using the algorithm from [2] that runs on our program **ACA**. Given a triple $\vec{d} = (a, b, c)$ of elements of a groupoid **$G$**, the ACA will calculate, for each positive integer $H$ and each $g \in G$, the probability that $g$ will be the value of a term of height at most $H$ when $a$, $b$ and $c$ are substituted for the variables $x$, $y$ and $z$, respectively. For example, if you use $\vec{d} = (2, 3, 0)$ and enter

```text
eat -g 2 1 1 3 3 0 2 1 1 3 2 0 2 2 1 2 -a ACA -d 2 3 0
```

it will return a sequence of probability distributions from the 4-element groupoid **$D = 2113\ 3021\ 1320\ 2212$** for successive values of $H$, starting with $0.25\ 0.00\ 0.25\ 0.25$ at $H = 1$. For $H = 27$, you will see

```text
27 0.147766 0.278100 0.396522 0.177612
```

giving the probabilities that a term of height at most $27$ will give value $0$, $1$, $2$ or $3$, respectively, when $2$, $3$ and $0$ are substituted for $x$, $y$ and $z$. By default, you will get probability distributions up to $H = 700$.

As another example, an element $e$ of a groupoid $G$ is an **idempotent** if $e \ast e = e$. A ternary operation $f$ on a groupoid **$G$ preserves idempotents** if $f(e, e, e) = e$ for every idempotent $e$ in **$G$**. Notice that every term operation must preserve idempotents. It follows that, if $e$ is idempotent, then every distribution for $\vec{d} = (e, e, e)$ will have value $1$ at $e$ and value $0$ for all other elements. In particular, if you use $\vec{d} = (2, 2, 2)$, every distribution for **$D$** will be $0\ 0\ 1\ 0$ since $2$ is idempotent in **$D$**. For this reason the **-trg** command is written to only give target operations that preserve idempotents. If you use **-t** and give a target operation that does not preserve idempotents, you will get an error message. We say that $(e, e, e)$ is an **idempotent triple** if $e$ is an idempotent.

A finite groupoid **$G$** passes the **Asymptotic Completeness Test** if, for every non-idempotent triple $\vec{d}$ of $G$, there is a number $h > 0$ and an integer $H > 0$ such that all the resulting probability values are greater than $h$ beyond level $H$. For example, with the groupoid **$D$** you will see that all probabilities beyond $H = 40$ are the same as the ones above for $H = 27$, so we can use $h = 0.14$. You can find ample evidence that a groupoid is or is not AC by testing it with a small assortment of different choices of triples $\vec{d}$. If there is any doubt about an outcome of the AC test, you can increase the terminal **term height**. For example, if you add the instruction "-th 10000", it will give back probabilities up to $H = 10{,}000$.

**No Subgroupoid Test.** The second test is to see that every non-idempotent element $g$ of **$G$** generates the entire groupoid. You can easily check this with a paper and pencil. For example, for the groupoid **$D$**, try $g = 0$. From $0$ you have $0 \ast 0 = 2$, then $0 \ast 2 = 1$ and $1 \ast 0 = 3$. Thus $0$ generates **$G$**. Now try $g = 1$. You have $1 \ast 1 = 0$. So $1$ generates $0$ and $0$ generates everything. Therefore $1$ generates everything. Since $2$ is idempotent, it just remains to check $g = 3$. Since $3 \ast 3 = 2$ and $2$ generates everything, so does $3$. Thus **$D$** has no non-trivial subgroupoids.

**Discriminator Term Test.** If **$G$** passes the AC Test and the NS Test, the MFBA is very likely to be able to find terms for **$G$**. It turns out that there is one special operation that must be a term operation on **$G$** in order for any of our programs to work on **$G$**. This is the **ternary discriminator operation**

$$
f(a, b, c) =
\begin{cases}
c & \text{if } a = b, \\
a & \text{if } a \ne b.
\end{cases}
$$

The final test is to use the MFBA to see if it can find a term representing the ternary discriminator operation. For example, try entering the groupoid **$D$** with

```text
eat -g 2 1 1 3 3 0 2 1 1 3 2 0 2 2 1 2 -a MFBA -ttd
```

The MFBA will quickly return a discriminator term, showing that **$D$** passes this test as well. If your groupoid finds a discriminator term for **$G$**, it is almost certain to be able to find terms for any idempotent preserving operation you choose. If it fails the DT Test, it is unlikely that it will find terms for other operations.

# 4. Interpreting the Test Results

In [4] a detailed study of the MFBA shows that, with rare exceptions, it will find terms for a groupoid if and only if the groupoid is **term continuous (TC)** and **idemprimal (IPr)**. By the theorem of [1], it is TC if it has no separating relations (NSR) and passes the AC Test. By the theorems of [6] and [8], it is IPr if and only if it passes the NS Test, has no congruences (NC) or automorphisms (NA), and passes the DT Test.

While all six of these requirements are necessary, two of them seem to screen out almost all of the groupoids that fail either TC or IPr. In [4] 30 randomly generated groupoids of sizes 3, 5 and 7 were examined. It was found that 17 of them were both TC and IPr. Of those 30, only 21 passed the AC Test and 20 passed the NS Test. But it was exactly the 17 TC and IPr groupoids that passed both the AC and NS Tests.

# 5. References

[1] David M. Clark, *Evolution of algebraic terms 1: Term to term operation continuity*, International Journal of Algebra and Computation, Vol. 23, No. 5 (2013) 1175-1205.

[2] David M. Clark, Maarten Keijzer, Lee Spector, *Evolution of algebraic terms 2: Deep drilling algorithm*, International Journal of Algebra and Computation, Vol. 26, No. 6 (2016) 1141-1176.

[3] David M. Clark, Lee Spector, *Evolution of algebraic terms 3: evolutionary algorithms*, International Journal of Algebra and Computation, Vol. 28, No. 5 (2018).

[4] David M. Clark, Nickolas C. Falco, *Evolution of algebraic terms 4: Biological beam algorithms*, International Journal of Algebra and Computation, (to appear).

[5] V. L. Murskii, *A finite basis of identities and other properties of “almost all” finite algebras*, Problemy Kibernetiki **30** (1975), 43-56.

[6] A. Pixley, *Functionally complete algebras generating distributive and permutable classes*, Math. Z. **114** (1970), 361-372.

[7] L. Spector, D. Clark, B. Barr, J. Klein, I. Lindsay, *Genetic programming for finite algebras*, GECCO 2008 Proceedings, pp. 1291-1298. (First place winner in the 2008 Hummie Competition.)

[8] H. Werner, *Eine Charakterisierung funktional vollständiger Algebren*, Arch. Math. (Basel) **21** (1970), 381-385.
