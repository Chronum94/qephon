import subprocess
from pathlib import Path


from ase.calculators.phx.create_input import write_ph_input, write_q2r_input, write_matdyn_input, write_zg_input

class EspressoPhononsProfile:
    def __init__(self, argv):
        self.argv = tuple(argv)

    def run(self, directory, inputfile, outputfile):
        from subprocess import check_call
        argv = list(self.argv) + ['-in', str(inputfile)]
        with open(directory / outputfile, 'wb') as fd:
            check_call(argv, stdout=fd, cwd=directory)


# class EspressoPhononTemplate(CalculatorTemplate):
#     def __init__(self):
#         # super().__init__(
#         #     'espresso',
#         #     ['energy', 'free_energy', 'forces', 'stress', 'magmoms'])
#         self.inputname = 'ph.in'
#         self.outputname = 'ph.out'

#     def write_input(self, directory, atoms, parameters, properties):
#         directory.mkdir(exist_ok=True, parents=True)
#         dst = directory / self.inputname
#         write(dst, atoms, format='espresso-in', properties=properties,
#               **parameters)

#     def execute(self, directory, profile):
#         profile.run(directory,
#                     self.inputname,
#                     self.outputname)

#     def read_results(self, directory):
#         path = directory / self.outputname
#         atoms = read(path, format='espresso-out')
#         return dict(atoms.calc.properties())


class EspressoPhonons:
    def __init__(self, profile: EspressoPhononsProfile, directory, **kwargs):
        self.profile = profile
        self.directory = directory
        self.kwargs_dict = kwargs
    
    def run(self):
        write_ph_input(directory=self.directory, infilename='ph.in', **self.kwargs_dict)
        # subprocess.run(command, shell=True, cwd=self.directory)
        # check_call(f"{self.profile.argv} -in {self.profile.}' '{phonon_dir}'",cwd="./")
        self.profile.run(self.directory, 'ph.in', 'ph.out')

    def final_diagonalize(self, diagonalize_profile=EspressoPhononsProfile(argv=['ph.x'])):
        diagonalize_profile.run(self.directory, 'ph.in', 'phdiag.out')
        

    @classmethod
    def from_scf(cls, scf_dir, phonon_dir, profile, **kwargs):
        """Initializes an EspressoPhonons object from scf and phonon
        and directories and ph.x inputs.

        Parameters
        ----------
        scf_dir : str or Path
            The directory containing the SCF calculation.
        phonon_dir : str or Path
            The directory in which the phonons calculation is conducted
        profile : EspressoPhononsProfile
            [description]

        Returns
        -------
        EspressoPhonons
            An EspressoPhonons object initialized with the relevant 
            directories and ph.x inputs.
        """
        phonon_dir = Path(phonon_dir)
        phonon_dir.mkdir(exist_ok=True)
        initialized_file_marker = phonon_dir / "SCFINIT"
        if not initialized_file_marker.exists():
            from subprocess import check_call
            check_call(f"cp -r '{str(scf_dir)}/'* '{str(phonon_dir)}/'", shell=True, cwd="./")
            initialized_file_marker.touch()
        return cls(profile, phonon_dir, **kwargs)

    
postprocess_input_writers = {"q2r": write_q2r_input,
                            "matdyn": write_matdyn_input,
                            "ZG": write_zg_input}

def ph_postprocess(directory, mode, executable, inputname, outputname, **kwargs):
    input_writer = postprocess_input_writers[mode]
    command = f"{executable} -in {inputname}"
    
    directory = Path(directory)
    directory.mkdir(exist_ok=True)
    input_writer(directory=directory, inputname=inputname, **kwargs)
    with open(directory / outputname, "w") as fd:
        from subprocess import check_call
        check_call(command, shell=True, cwd=directory, stdout=fd)
