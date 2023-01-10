import qephon.read_output as qro
from io import StringIO

def test_parse_epsilon_block():
    fd = StringIO(
    """Dielectric Tensor:

    10.000000000005         -0.000000000000          0.000000000000
    -0.000000000000         10.000000000005          0.000000000000
    0.000000000000          0.000000000000         10.000000000005
    """
    )

    res = parse_dielectric_tensor(fd)
    return np.allclose(np.diag(res['epsilon']), 10.0 + 5e-12, atol=1e-14)
