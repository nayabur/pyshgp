"""The :mod:`evaluation` module defines classes to evaluate program CodeBlocks."""
from abc import ABC, abstractmethod
from typing import Sequence, Union, Callable
from collections import defaultdict
import numpy as np
import pandas as pd

from pyshgp.push.interpreter import PushInterpreter, DEFAULT_INTERPRETER, Program
from pyshgp.tap import tap
from pyshgp.utils import Token


def damerau_levenshtein_distance(a: Union[str, Sequence], b: Union[str, Sequence]) -> int:
    """Damerau Levenshtein Distance that works for both strings and lists.

    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance.
    This implemenation is heavily inspired by the implementation in the
    jellyfish package. https://github.com/jamesturk/jellyfish
    """
    a_is_str = isinstance(a, str)
    b_is_str = isinstance(b, str)
    if a_is_str or b_is_str:
        assert a_is_str and b_is_str

    len1 = len(a)
    len2 = len(b)
    infinite = len1 + len2

    da = defaultdict(int)
    score = [[0] * (len2 + 2) for x in range(len1 + 2)]
    score[0][0] = infinite
    for i in range(0, len1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in range(0, len2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da[b[j - 1]]
            j1 = db
            cost = 1
            if a[i - 1] == b[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(score[i][j] + cost,
                                      score[i + 1][j] + 1,
                                      score[i][j + 1] + 1,
                                      score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1))
        da[a[i - 1]] = i
    return score[len1 + 1][len2 + 1]


class Evaluator(ABC):
    """Base class or evaluators.

    Parameters
    ----------
    interpreter : PushInterpreter, optional
        PushInterpreter used to run program and get their output. Default is
        an interpreter with the default configuration and all core instructions
        registered.
    penalty : float, optional
        When a program's output cannot be evaluated on a particular case, the
        penalty error is assigned. Default is 5e5.
    verbosity_config : Optional[VerbosityConfig] (default = None)
        A VerbosityConfig controlling what is logged during evaluation.
        Default is no verbosity.

    """

    def __init__(self,
                 interpreter: PushInterpreter = "default",
                 penalty: float = 1e6):
        self.penalty = penalty
        if interpreter == "default":
            self.interpreter = DEFAULT_INTERPRETER
        else:
            self.interpreter = interpreter

    def default_error_function(self, actuals, expecteds) -> np.array:
        """Produce errors of actual program output given expected program output.

        The default error function is intended to be a universal error function
        for Push programs which only output a subset of the standard data types.

        Parameters
        ----------
        actuals : list
            The values produced by running a Push program on a sequences of cases.

        expecteds: list
            The ground truth values for the sequence of cases used to produce the actuals.

        Returns
        -------
        np.array
            An array of error values describing the program's performance.

        """
        errors = []
        for ndx, actual in enumerate(actuals):
            expected = expecteds[ndx]
            if actual is Token.no_stack_item:
                errors.append(self.penalty)
            elif isinstance(expected, (bool, np.bool_)):
                errors.append(int(not (bool(actual) == expected)))
            elif isinstance(expected, (int, np.int64, float, np.float64)):
                try:
                    errors.append(abs(float(actual) - expected))
                except OverflowError:
                    errors.append(self.penalty)
            elif isinstance(expected, str):
                errors.append(damerau_levenshtein_distance(str(actual), expected))
            elif isinstance(expected, list):
                errors += list(self.default_error_function(list(actual), expected))
            else:
                raise ValueError("Unknown expected type for {e}".format(e=expected))
        return np.array(errors)

    @tap
    @abstractmethod
    def evaluate(self, program: Program) -> np.ndarray:
        """Evaluate the program and return the error vector.

        Parameters
        ----------
        program
            Program (CodeBlock of Push code) to evaluate.

        Returns
        -------
        np.ndarray
            The error vector of the program.

        """
        pass


class DatasetEvaluator(Evaluator):
    """Evaluator driven by a labeled dataset."""

    def __init__(self,
                 X, y,
                 penalize_no_input_instructions: bool = False,
                 penalize_same_outputs: bool = False,
                 interpreter: PushInterpreter = "default",
                 penalty: float = 1e6,
                 ):
        """Create Evaluator based on a labeled dataset. Inspired by sklearn.

        Parameters
        ----------
        X : list, array-like, or pandas dataframe of shape = [n_samples, n_features]
            The inputs to evaluate each program on.

        y : list, array-like, or pandas dataframe.
            The target values. Shape = [n_samples] or [n_samples, n_outputs]

        penalize_same_outputs: bool, optional
            Creates an additional penalty for programs that return the same value for every output. Increases the
            program error value five times to try suppressing these programs during evolution. Default is False.

        penalize_no_input_instructions: bool, optional
            Creates an additional penalty for programs with no input instructions. Increases the program
            error value five times to try suppressing these programs during evolution. Default is False.

        interpreter : PushInterpreter or {"default"}
            The interpreter used to run the push programs.

        penalty : float
            If no response is given by the program on a given input, assign this
            error as the error.

        """
        super().__init__(interpreter, penalty)
        self.penalize_no_input_instructions = penalize_no_input_instructions
        self.penalize_same_outputs = penalize_same_outputs
        self.penalize_no_input_instructions = penalize_no_input_instruc
        self.penalize_same_outputs = penalize_same_outs
        self.X = pd.DataFrame(X)
        self.y = pd.DataFrame(y)

    @tap
    def evaluate(self, program: Program) -> np.array:
        """Evaluate the program and return the error vector.

        Parameters
        ----------
        program
            Program (CodeBlock of Push code) to evaluate.

        Returns
        -------
        np.ndarray
            The error vector of the program.

        """
        super().evaluate(program)

        # penalize no input instructions
        has_inputs = False
        multiplicand = 1
        if self.penalize_no_input_instructions:
            from pyshgp.push.atoms import Input
            for codeblock in program.code:
                if isinstance(codeblock, Input):
                    has_inputs = True
                    break
            if not has_inputs:
                multiplicand *= 10

        errors = []
        actuals=[]
        for ndx in range(self.X.shape[0]):
            inputs = self.X.iloc[ndx].to_list()
            expected = self.y.iloc[ndx].to_list()
            actual = self.interpreter.run(program, inputs)
            actuals.append(actual)
            errors.append(self.default_error_function(actual, expected))

        # penalize same constant output
        if actuals.count(actuals[0]) == len(actuals):
            multiplicand *= 5

        return np.array(errors).flatten() * multiplicand


class FunctionEvaluator(Evaluator):
    """Evaluator driven by an error function."""

    def __init__(self, error_function: Callable):
        """Create Evaluator driven by an error function.

        The given error function must take a push program in the form of a
        CodeBlock and then return an np.ndarray of numeric errors. These errors
        will be used as the program's error vector.

        The error functions will typically instansiate its own PushInterpreter
        an run the given program as needed.

        Parameters
        ----------
        error_function : Callable
            A function which takes a program to evaluate and returns a
            np.ndarray of errors.

        """
        super().__init__()
        self.error_function = error_function

    @tap
    def evaluate(self, program: Program) -> np.ndarray:
        """Evaluate the program and return the error vector.

        Parameters
        ----------
        program
            Program (CodeBlock of Push code) to evaluate.

        Returns
        -------
        np.ndarray
            The error vector of the program.

        """
        super().evaluate(program)
        return self.error_function(program)
