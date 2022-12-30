import subprocess
from pathlib import Path

from qephon.create_input import (
    write_epw_input,
)


class EPWProfile:
    def __init__(self, argv):
        self.argv = tuple(argv)

    def run(self, directory, inputfile, outputfile):
        from subprocess import check_call
        import os

        argv = list(self.argv) + ["-in", str(inputfile)]
        with open(directory / outputfile, "wb") as fd:
            check_call(argv, stdout=fd, cwd=directory, env=os.environ)


class EPW:
    def __init__(self, profile: EPWProfile, directory, **kwargs):
        self.profile = profile
        self.directory = directory
        self.kwargs_dict = kwargs

    def run(self):
        write_ph_input(
            directory=self.directory, infilename="iepw.in", **self.kwargs_dict
        )
        self.profile.run(self.directory, "iepw.in", "oepw.out")

    # def final_diagonalize(
    #     self, diagonalize_profile=EspressoPhononsProfile(argv=["epw.x"])
    # ):
    #     diagonalize_profile.run(self.directory, "iph.in", "phdiag.out")

    # @classmethod
    # def from_scf(cls, scf_dir, phonon_dir, profile, copy=True, **kwargs):
    #     """Initializes an EspressoPhonons object from scf and phonon
    #     and directories and ph.x inputs.

    #     Parameters
    #     ----------
    #     scf_dir : str or Path
    #         The directory containing the SCF calculation.
    #     phonon_dir : str or Path
    #         The directory in which the phonons calculation is conducted
    #     profile : EspressoPhononsProfile
    #         [description]

    #     Returns
    #     -------
    #     EspressoPhonons
    #         An EspressoPhonons object initialized with the relevant
    #         directories and ph.x inputs.
    #     """
    #     phonon_dir = Path(phonon_dir)
    #     phonon_dir.mkdir(exist_ok=True)
    #     initialized_file_marker = phonon_dir / "SCFINIT"
    #     if not initialized_file_marker.exists():
    #         from subprocess import check_call

    #         if copy:
    #             check_call(
    #                 f"cp -r '{str(scf_dir)}/'* '{str(phonon_dir)}/'",
    #                 shell=True,
    #                 cwd="./",
    #             )
    #         initialized_file_marker.touch()
    #     return cls(profile, phonon_dir, **kwargs)


postprocess_input_writers = {
    "q2r": write_q2r_input,
    "matdyn": write_matdyn_input,
    "zg": write_zg_input,
}

def q2r(directory, **kwargs):
    common = "q2r"
    postprocess_wrapper(directory, common, **kwargs)

def matdyn(directory, **kwargs):
    common = "matdyn"
    postprocess_wrapper(directory, common, **kwargs)

def ZG(directory, **kwargs):
    common = "ZG"
    postprocess_wrapper(directory, common, **kwargs)

def postprocess_wrapper(directory, common, **kwargs):
    ph_postprocess(directory, common, f"{common}.x", f"i{common}.in", f"o{common}.out", **kwargs)

def ph_postprocess(directory, mode, executable, inputname, outputname, **kwargs):
    input_writer = postprocess_input_writers[mode.lower()]
    command = f"{executable} -in {inputname}"

    directory = Path(directory)
    directory.mkdir(exist_ok=True)
    input_writer(directory=directory, inputname=inputname, **kwargs)
    with open(directory / outputname, "w") as fd:
        from subprocess import check_call

        check_call(command, shell=True, cwd=directory, stdout=fd)
