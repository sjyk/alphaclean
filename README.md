# alphaclean
In many data science applications, data cleaning is effectively manual with ad-hoc, single-use scripts and programs. 
This practice is highly problematic for reproducibility (sharing analysis between researchers), interpretability (explaining the findings of a particular analysis), and scalability (replicating the analyses on larger corpora).
Most existing relational data cleaning solutions are designed as stand-alone systems, often coupled with a DBMS, with poor language support for Python and R that are widely used in data science.

We designed Python library that declaratively synthesizes data cleaning programs. 
AlphaClean is given a  specification of quality (e.g., integrity constraints or a statistical model the data must conform to) and a language of allowed data transformations, and it searches to find a sequence of transformations that maximizes the quality metric.
The discovered sequence of transformations defines an intermediate representation, which can be easily transferred between languages or optimized with a compiler.

## Installation
