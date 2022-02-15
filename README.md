# AlphaClean v0.1 for Python3

In many data science applications, data cleaning is effectively manual with ad-hoc, single-use scripts and programs.
This practice is highly problematic for reproducibility (sharing analysis between researchers), interpretability (explaining the findings of a particular analysis), and scalability (replicating the analyses on larger corpora).
Most existing relational data cleaning solutions are designed as stand-alone systems -- often coupled with a DBMS -- with poor support for languages widely in data science, such as Python and R.

In order to address this problem, we designed a Python 2 library that declaratively synthesizes data cleaning programs.
AlphaClean is given a specification of quality (e.g. integrity constraints or a statistical model the data must conform to) and a language of allowed data transformations, then it searches to find a sequence of transformations that best satisfies the quality specification.
The discovered sequence of transformations defines an intermediate representation, which can be easily transferred between languages or optimized with a compiler.

## Requirements

As an initial research prototype, we have not yet designed AlphaClean for deployment. It is a package that researchers can locally develop and test to evaluate different data cleaning approaches and techniques. The dependencies are:
    pip install -r requirements.txt

## Using the Package

The docs folder contains a number of tutorials on how to use AlphaClean.

0. [Getting Started](https://github.com/sjyk/alphaclean/blob/master/docs/00-GettingStarted.md)
1. [Advanced Features](https://github.com/sjyk/alphaclean/blob/master/docs/01-MakingItHarder.md)
2. [Scaling Up](https://github.com/sjyk/alphaclean/blob/master/docs/02-Scaling.md)
3. [External Knowledge](https://github.com/sjyk/alphaclean/blob/master/docs/03-ExternalInfo.md)
4. [Basic Numerical Cleaning](https://github.com/sjyk/alphaclean/blob/master/docs/04-Numerical.md)
5. [Advanced Numerical Cleaning](https://github.com/sjyk/alphaclean/blob/master/docs/05-AdvancedNumerical.md)
