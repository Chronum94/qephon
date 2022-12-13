# qephon

To install:

```
git clone https://github.com/Chronum94/qephon.git
cd qephon
poetry install
```

This package provides a thin [ASE](https://gitlab.com/ase/ase/)-like wrapper around Quantum Espresso's `ph.x` executable.

```python
from qephon import EspressoPhonons, EspressoPhononsProfile

# This example assumes you've done an SCF calculation right before this on some small
# tutorial-worthy system.
ph = EspressoPhonons.from_scf("scf_directory", # The directory where you've carried out the scf.
                              "phonon_directory", # The directory where you will carry out the phonon calculation.
                              profile=EspressoPhononsProfile("mpirun -np 2 ph.x".split()),
                              ldisp=True,
                              nq1=1,nq2=1,nq3=1 # Gamma point phonons
                              )
ph.run()
# Run the line below if you've used image parallelism in the ph.x call.
# ph.final_diagonalize()
```
