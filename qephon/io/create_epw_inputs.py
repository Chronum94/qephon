import numpy as np
import os
from pathlib import Path
import f90nml


def write_epw_inputdef(
    directory,
    infilename: str = "iepw.in",
    require_valid_calculation: bool = True,
    **kwargs,
):