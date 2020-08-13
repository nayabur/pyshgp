import numpy as np
import random

from pyshgp.gp.estimators import PushEstimator
from pyshgp.gp.genome import GeneSpawner
# import cli module
import cli


def target_function(a):
    s1 = a[0]
    s2 = a[1]
    isAnagram = True
    if len(s1) != len(s2):
        isAnagram = False
    if s1.isalpha() != s2.isalpha():
        isAnagram = False
    if sorted(s1) != sorted(s2):
        isAnagram = False
    if s1 == s2:
        isAnagram = False
    return isAnagram


X = [["race", "care"], ["heart", "earth"], ["knee", "keen"], ["soccer", "pauper"], ["e720", "H2flow"],
     [" ", " "], ["", "4"], ["listen", "silent"], ["ship", "star"], ["seed", "deed"], ["123", "123"],
     ["456", "654"], ["acd123", "abc123"], ["h3ll0", "h3ll0"], ["smile", "simile"]]
y = np.array([[target_function(s)] for s in X])

"""import pandas as pd
X = pd.Series(X)
print(X)
print(X[1])"""

# create a GeneSpawner as normal
spawner = GeneSpawner(
    n_inputs=2,
    instruction_set="core",
    literals=[],
    erc_generators=[
        lambda: random.randint(0, 10),
    ]
)

# add the GeneSpawner created above as parameter spawner
# unpack the dictionary of command line arguments est_dict
# this will add any command line arguments entered, and the rest will default
if __name__ == "__main__":
    # call cli.pysh_parser() to parse through the command line
    est_dict = cli.pysh_parser()

    # if there are no command line arguments

    est = PushEstimator(
        spawner=spawner,
        **est_dict
    )

    est.fit(X=X, y=y)
    print("Best program found:")
    print(est.solution.program.pretty_str())
    print("Errors:")
    print(est.score(X, y))
