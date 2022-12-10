from io import TextIOWrapper
import numpy as np
import re


def parse_q(fd) -> dict:
    """Parses the qpoint for the given .dyn file.

    Parameters
    ----------
    fd : File handle
        [description]

    Returns
    -------
    dict
        Dict containing the q-point coordinate
    """

    current_line = ""
    while 'q =' not in current_line:
        current_line = fd.readline()

    # Strip all of the irrelevant characters
    current_line = current_line.strip('q=() \n').split()
    q = np.array(current_line, dtype=np.float64)
    return {"q": q}


def parse_dielectric_tensor(fd) -> dict:
    """Parses the dielectric tensor block from dynamical files.
    The section looks like so:
    
    Dielectric Tensor:

    12.980462097613         -0.000000000000          0.000000000000
    -0.000000000000         12.980462097613          0.000000000000
    0.000000000000          0.000000000000         12.980462097613

    Parameters
    ----------
    fd : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    current_line = ""
    while 'Dielectric Tensor:' not in current_line:
        current_line = fd.readline().strip()
        if "Diagonalizing the dynamical matrix" in current_line:
            return {"epsilon": None}
        continue

    matrix = []
    epsilon_parsing_done: bool = False
    num_matrix_rows_parsed = 0
    while not epsilon_parsing_done:
        current_line = fd.readline().strip()
        if len(current_line) == 0:
            continue
        else:
            matrix.append(current_line.strip().split())
            num_matrix_rows_parsed += 1
        if num_matrix_rows_parsed == 3:
            epsilon_parsing_done = True

    dielectric_tensor = np.array(matrix, dtype = np.float64)
    return {"epsilon": dielectric_tensor}


def parse_z_block(fd, natoms: int) -> dict:
    current_line = ""
    z_block_parsed = False
    z_dict = {}
    natoms_parsed = 0
    while not z_block_parsed:
        current_line = fd.readline()
        if len(current_line.strip()) == 0: # blank line
            continue

        if "atom #" in current_line:
            natoms_parsed += 1
            atom_index = int(current_line.strip().split()[-1])
            z_tensor = []
            for _ in range(3):
                z_tensor.append(np.array(fd.readline().strip().split(), dtype=np.float64))
            z_dict[atom_index] = np.array(z_tensor)

        if natoms_parsed == natoms:
            z_block_parsed = True
    
    return z_dict
            

def parse_effective_charges(fd, natoms: int) -> dict:

    born_charges_data = {}
    born_charges_parsed = False
    zeu_parsed = False
    zue_parsed = False
    while not born_charges_parsed:
        current_line = fd.readline()
        if "Diagonalizing the dynamical matrix" in current_line or "q = (" in current_line:
            break
            

        if "E-U" in current_line:
            born_charges_data["zeu"] = parse_z_block(fd, natoms)
            zeu_parsed = True
        if "U-E" in current_line:
            born_charges_data["zue"] = parse_z_block(fd, natoms)
            zue_parsed = True

        born_charges_parsed = zeu_parsed and zue_parsed

    if zeu_parsed ^ zue_parsed:
        raise Exception("One type of Z parsed but not the other! This should not be happening!")
    if born_charges_data == {}:
        born_charges_data = {"zeu": None, "zue": None}
    return born_charges_data


def parse_ifc_block(fd, natoms: int) -> dict:

    ifc_block_parsed: bool = False
    natom_pairs_parsed = 0
    ifc_dict = {}

    while not ifc_block_parsed:
        current_line: str = fd.readline()
        if len(current_line.strip()) == 0:
            continue

        atom_pair_index_line = re.match(r'\d+\s+\d+', current_line.strip())
        if atom_pair_index_line is not None:
            ifc_matrix = []
            atom_pair_indices = tuple(int(x) for x in atom_pair_index_line.string.split())

            for _ in range(3):
                ifc_matrix.append(fd.readline().strip().split())
            ifc_dict[atom_pair_indices] = np.array(ifc_matrix, dtype=np.float64)

            natom_pairs_parsed += 1

        if natom_pairs_parsed == (natoms ** 2):
            ifc_block_parsed = True

    return {"ifc": ifc_dict}


def parse_frequencies(fd, natoms: int) -> dict:

    frequencies_and_modes_parsed = False
    num_frequencies_parsed = 0
    frequencies = []
    normal_modes = []

    while '************' not in fd.readline():
        continue

    while not frequencies_and_modes_parsed:
        current_line = fd.readline()
        # Regexes bad, but this finds a float, a space, followed by '[THz]'
        frequency_regex_matches = re.findall('[+-]?\d+.\d+\s\[THz\]', current_line)
        if len(frequency_regex_matches) == 0:
            continue
        else:
            frequencies.append(float(frequency_regex_matches[0].strip().split()[0]))
            coordinates_for_this_mode = []
            for _ in range(natoms):
                current_line = fd.readline()
                coordinates_for_this_mode.append(current_line.strip('()\n ').split())
            normal_modes.append(np.array(coordinates_for_this_mode, dtype=np.float64))
            num_frequencies_parsed += 1
        
        if num_frequencies_parsed == natoms * 3:
            frequencies_and_modes_parsed = True

    return {"frequencies_and_modes": (frequencies, normal_modes)}


def read_dynfile(fd):
    for _ in range(2):
        next(fd)
    
    natoms = int(fd.readline().strip().split()[1])
    print(natoms)
    qdict = parse_q(fd)
    yield qdict
    yield parse_ifc_block(fd, natoms=natoms)
    if np.allclose(qdict["q"], 0.0):
        yield parse_dielectric_tensor(fd)
        yield parse_effective_charges(fd, natoms=natoms)
    yield parse_frequencies(fd, natoms=natoms)