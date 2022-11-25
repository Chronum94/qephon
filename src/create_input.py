"""Input file creator for ph.x that works as closely as possible to Atomic Simulation Environment conventions.
The following arguments are not implemented:
    "dvscf_star",
    "drho_star",
"""
import numpy as np
import os
import multimethod
from pathlib import Path

@multimethod
def fortranformat(x: bool):
    if x:
        return ".true."
    elif not x:
        return ".false."
    else:
        raise Exception

@multimethod
def fortranformat(x: float):
    return f"{x:0.07e}".replace("e", "d")

# def write_ph_input(directory, infilename: str = 'phonon.in', require_valid_calculation: bool = True, **kwargs):
#     """Writes a ph.x input file when using the .write() method.
#     All input arguments except STRUCTURE types are supported,
#     but the input sanitation/validation is currently weak.

#     Parameters
#     ----------
#     directory : str
#         The directory in which the pw.x calculation has been done.
#     infilename : str, optional
#         The ph.x input file, by default "phonon.in"
#     require_valid_calculation: bool, optional
#         If True, throws an error if a valid SCF calculation directory does not exist, by default True
#     """
#     inputfile_name: str = directory / infilename
#     if not os.path.exists(directory) and require_valid_calculation:
#         raise FileNotFoundError(
#             r"The calculation directory does not exist! \
#             Make sure you have carried out a pw.x calculation before this, \
#             and that the directory names are exactly equal."
#         )

#     with open(inputfile_name, "w") as fd:
#         fd.write("&inputph\n")

#         for key, value in kwargs.items():
#             if type(key) == bool:
#                 fd.write("=".join([key, bool_to_fortbool(value)]) + ",\n")

#             if type(key) == float:
#                 assert type(value) == float
#                 fd.write("=".join([key, float_to_fortstring(value)]) + ",\n")

#             if type(key) == int:
#                 assert type(value) == int
#                 fd.write(key + "=" + f"{value}" + ",\n")

#             if key in str_keys:
#                 assert type(value) == str
#                 fd.write(key + "=" + f"'{value}'" + ",\n")

#             if key in list_float_keys:
#                 assert type(value) == list
#                 for i, value in enumerate(value):
#                     fd.write(
#                         "=".join([key + f"({i+1})", float_to_fortstring(value)])
#                         + ",\n"
#                     )

#         fd.write("/\n")
#         try:
#             qpoints = kwargs["qpoints"]
#             fd.write(f"{len(qpoints)}\n")
#             for q in qpoints:
#                 fd.write(f"   {q[0]} {q[1]} {q[2]}  1\n")
#         except KeyError:
#             pass


def write_ph_input(directory, infilename: str = 'phonon.in', require_valid_calculation: bool = True, **kwargs):
    """Writes a ph.x input file when using the .write() method.
    All input arguments except STRUCTURE types are supported,
    but the input sanitation/validation is currently weak.

    Parameters
    ----------
    directory : str
        The directory in which the pw.x calculation has been done.
    infilename : str, optional
        The ph.x input file, by default "phonon.in"
    require_valid_calculation: bool, optional
        If True, throws an error if a valid SCF calculation directory does not exist, by default True
    """
    inputfile_name: str = Path(directory) / infilename
    if not os.path.exists(directory) and require_valid_calculation:
        raise FileNotFoundError(
            r"The calculation directory does not exist! \
            Make sure you have carried out a pw.x calculation before this, \
            and that the directory names are exactly equal."
        )
    try:    
        qpoints = kwargs.pop("qpoints")
    except KeyError:
        qpoints = None
        pass

    input_nml = f90nml.Namelist({"inputph": kwargs})
    with open(infilename, 'w') as fd:
        input_nml.write(fd)
        
        if qpoints is not None:
            fd.write(f"{len(qpoints)}\n")
            for q in qpoints:
                fd.write(f"   {q[0]} {q[1]} {q[2]}  1\n")

        
def write_q2r_input(directory, inputname: str = 'iq2r.in', **kwargs):
    inputfile_name = directory / inputname
    print(inputfile_name)

    with open (inputfile_name, "w") as fd:
        fd.write("&input\n")
        
        for key, value in kwargs.items():
            if type(value) == bool:
                fd.write("=".join([key, bool_to_fortbool(value)]) + ",\n")
            
            if type(value) == str:
                fd.write(key + "=" + f"'{value}'" + ",\n")
                
        fd.write("/\n")

        
def write_matdyn_input(directory, inputname: str = 'imdyn.in', **kwargs):
    inputfile_name = directory / inputname
    print(inputfile_name)
    
    try:
        qpoints = kwargs["qpoints"]
    except KeyError:
        qpoints = np.array([[0.0, 0.0, 0.0]])
    with open (inputfile_name, "w") as fd:
        fd.write("&input\n")
        
        for key, value in kwargs.items():
            if type(value) == bool:
                fd.write("=".join([key, bool_to_fortbool(value)]) + ",\n")
            
            if type(value) == str:
                fd.write(key + "=" + f"'{value}'" + ",\n")
                
        fd.write(f"/\n{len(qpoints)}\n")
        for q in qpoints:
            fd.write(f"   {q[0]} {q[1]} {q[2]}\n")
            
def write_zg_input(directory, inputname: str = 'izg.in', **kwargs):
    inputfile_name = directory / inputname
    print(inputfile_name)
    with open (inputfile_name, "w") as fd:
        fd.write("&input\n")
        
        for key, value in kwargs.items():
            if type(value) == bool:
                fd.write("=".join([key, bool_to_fortbool(value)]) + ",\n")
                
            if type(value) == int:
                fd.write("=".join([key, str(value)]) + ",\n")
            
            if type(value) == str:
                fd.write(key + "=" + f"'{value}'" + ",\n")
            if type(value) == list:
                for i, element in enumerate(value):
                    fd.write(key + f"({i + 1})=" + f"'{element}'" + ",\n")
                
        fd.write(f"/\n")