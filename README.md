<h3 align="center">Evolution of Algebraic Terms</h3>

<p>
EAT is software implementation of the algorithms described in papers Evolution of Algebraic Terms (EAT) [1][2][3]. Given an arbitrary performance specification, the program systematically designs a digital ciruit using binary logic on groupoids of size 3 or larger. The program's success is documented by its ability to consistently find such designs from an incredibly vast search space in fractions of
a second. It has applications in both the fields of Mathematics and Computer Engineering.
</p>

<h4>Installation</h4>

For a development install first download the project and then run
```
pip install -e .
```
in the root project directory, or run
```
python setup.py develop
```

<h4>How to use</h4>

To run the program, run the `eat` command in the console.

```
>>> eat
xz*zx*zy**xy*zyzz***y**xzy*y**zxz*x*zyz**y*zy*y*xzy*y*xzx**y*yxx**xzzxzx***z***zy*zzy*zx*yyx*yyz*zz
**********************zxzzz**x**y*yyx**zy****yzxz**xzzxz*z**zxzy*xyyx*z*****zxxzyyxxz*zx*z***xz*y*y
zzz***yz***yz*xy*****************yzy*yzzy*zyy*****yxx**xzzzz*y***x******zzy*x*z*x*yy*y**xy*xy*z*zxx
xzzy*zzzy*zyy*y*zzy*z*****************xxxx**xz***zxzyx*x*z*z****yzx*xy*zx**xxxyz*zyz*********yyxzxz
yx****yyyxz*xyxxyz**zz*x*yz****xzyyyyzyxy**zy**y*x**xz********yyxx*y*yxxz*xxxyzy*yxyy*yy***yxyzz*x*
*xxz*x**y*y****yzzx*xxz*z*zz****************************************
```

To view a the help text displaying all options, run `eat -h`.

<h4>Examples</h4>

<b>1.)</b> Find a term using the Deep Drilling Algorithm (DDA) with

3 element primal groupoid:

| * | 0 | 1 | 2 |
|---|---|---|---|
| 0 | 1 | 1 | 2 |
| 1 | 0 | 2 | 0 |
| 2 | 0 | 2 | 1 |

and custom target array:

[[0], [2], [2], [2], [0], [2], [1], [2], [2], [2], [0], [2], [1], [2], [0], [2], [1], [0], [2], [2], [0], [2], [2], [0], [0], [0], [1]]

run:
```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target 0 2 2 2 0 2 1 2 2 2 0 2 1 2 0 2 1 0 2 2 0 2 2 0 0 0 1
```

<b>2.)</b> Run DDA using the same groupoid as in example 1, but with a random target:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random
```

inlcude a summary print out:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random --print-summary
```

include a verbose table print out :

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random --verbose
```

<b>3.)</b> Run DDA using the same groupoid as in example 1, but with a ternary descriminator target:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-ternary-descriminator
```

<b>5.)</b> Run DDA using the same groupoid as in example 1, but with a random target and
using the Gamblers Ruin Algorithm construct random male terms:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random --male-term-generation-method random
```

<b>6.)</b> Run DDA using the same groupoid as in example 1, but with a random target and
using a randomly selection of the 12 one and two variable terms `["x", "y", "z", "xx*", "xy*",
"xz*", "yx*", "yy*", "yz*", "zx*", "zy*", "zz*"]` to construct male terms:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random --male-term-generation-method random-12-terms
```

<b>7.)</b> Run DDA using the same groupoid as in example 1, but specify custom term variables:

```
eat -a DDA --groupoid 1 1 2 0 2 0 0 2 1 --target-random --term-variables a b c d
```

<b>8.)</b> Find a term using the DDA with

4 element primal groupoid:

| * | 0 | 1 | 2 | 3 |   
|---|---|---|---|---|
| 0 | 1 | 3 | 1 | 2 |
| 1 | 1 | 2 | 2 | 3 |
| 2 | 2 | 0 | 0 | 3 |
| 3 | 2 | 2 | 1 | 2 |

and a ternary descriminator target operation:

[[0], [1], [2], [3], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [1], [1], [1], [1], [0], [1], [2], [3], [1], [1], [1],
 [1], [1], [1], [1], [1], [2], [2], [2], [2], [2], [2], [2], [2], [0], [1], [2], [3], [2], [2], [2], [2], [3], [3], [3], [3], [3], [3],
 [3], [3], [3], [3], [3], [3], [0], [1], [2], [3]]

run:
```
eat -a DDA --groupoid 1 3 1 2 1 2 2 3 2 0 0 3 2 2 1 2 --target-ternary-descriminator
```

<h4>References</h4>

[1] David M. Clark, Evolution of algebraic terms 1: Term to term operation continuity,<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;International Journal of Algebra and Computation, Vol. 23, No. 5 (2013) 1175–1205.<br/>
[2] David M. Clark, Maarten Keijzer, Lee Spector, Evolution of algebraic terms 2: Deep drilling algorithm,<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;International Journal of Algebra and Computation, Vol. 26, No. 6 (2016) 1141–1176.<br/>
[3] David M. Clark, Lee Spector, Evolution of algebraic terms 3: evolutionary algorithms,<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;International Journal of Algebra and Computation, Vol. 28, No. 5 (2018).<br/>

