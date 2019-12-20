from pygost.gost3410 import CURVES
from transaction import Transaction

ELEPTIC_CURVE = CURVES["id-tc26-gost-3410-12-512-paramSetA"]
TARGET = 0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
DEFAULT_PROOF = 100
DEFAULT_TRANSACTION = Transaction('genesys', 'genesys', 0)
FAIL = -1
SUCCESS = 0

candidates_list = ['Владимир',
                   'Путин',
                   'Молодец',
                   'Политик',
                   'Лидер',
                   'И. Борец']
