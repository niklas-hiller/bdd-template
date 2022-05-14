import os
from pytest_bdd import scenarios

# To include all steps that exist in step_defs.sample_steps
# in the steps discovery of the scenario file
from step_defs.sample_steps import *

scenarios(os.environ["FEATURE_FILE"])
