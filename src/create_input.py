"""Input file creator for ph.x that works as closely as possible to Atomic Simulation Environment conventions.
The following arguments are not implemented:
    "dvscf_star",
    "drho_star",
"""
import numpy as np
import os


str_keys = {
    "title_line",
    "outdir",
    "prefix",
    "verbosity",
    "fildyn",
    "fildrho",
    "fildvscf",
    "electron_phonon",
    "ahc_dir",
    "diagonalization",
    "wpot_dir",
}

int_keys = {
    "niter_ph",
    "nmix_ph",
    "el_ph_nsigma",
    "ahc_nbnd",
    "ahc_nbndskip",
    "nq1",
    "nq2",
    "nq3",
    "nk1",
    "nk2",
    "nk3",
    "k1",
    "k2",
    "k3",
    "start_irr",
    "last_irr",
    "nat_todo",
    "modenum",
    "start_q",
    "last_q",
}

float_keys = {
    "tr2_ph",
    "eth_rps",
    "eth_ns",
    "dek",
    "el_ph_sigma",
}

list_float_keys = {
    "amass",
    "alpha_mix",
}

bool_keys = {
    "reduce_io",
    "epsil",
    "lrpa",
    "lnoloc",
    "trans",
    "lraman",
    "recover",
    "low_directory_check",
    "only_init",
    "qplot",
    "q2d",
    "q_in_band_form",
    "skip_upperfan",
    "shift_q",
    "zeu",
    "zue",
    "elop",
    "fpol",
    "ldisp",
    "nogg",
    "asr",
    "ldiag",
    "lqdir",
    "search_sym",
    "read_dns_bare",
    "ldvscf_interpolate",
    "do_long_range",
    "do_charge_neutral",
}


def bool_to_fortbool(x):
    if x:
        return ".true."
    elif not x:
        return ".false."
    else:
        raise Exception


def float_to_fortstring(x):
    return f"{x:0.07e}".replace("e", "d")


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
    inputfile_name: str = directory / infilename
    if not os.path.exists(directory) and require_valid_calculation:
        raise FileNotFoundError(
            r"The calculation directory does not exist! \
            Make sure you have carried out a pw.x calculation before this, \
            and that the directory names are exactly equal."
        )

    with open(inputfile_name, "w") as fd:
        fd.write("&inputph\n")

        for key, value in kwargs.items():
            if key in bool_keys:
                assert type(value) == bool
                fd.write("=".join([key, bool_to_fortbool(value)]) + ",\n")

            if key in float_keys:
                assert type(value) == float
                fd.write("=".join([key, float_to_fortstring(value)]) + ",\n")

            if key in int_keys:
                assert type(value) == int
                fd.write(key + "=" + f"{value}" + ",\n")

            if key in str_keys:
                assert type(value) == str
                fd.write(key + "=" + f"'{value}'" + ",\n")

            if key in list_float_keys:
                assert type(value) == list
                for i, value in enumerate(value):
                    fd.write(
                        "=".join([key + f"({i+1})", float_to_fortstring(value)])
                        + ",\n"
                    )

        fd.write("/\n")
        try:
            qpoints = kwargs["qpoints"]
            fd.write(f"{len(qpoints)}\n")
            for q in qpoints:
                fd.write(f"   {q[0]} {q[1]} {q[2]}  1\n")
        except KeyError:
            pass

        
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