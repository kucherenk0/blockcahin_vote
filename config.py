from pygost.gost3410 import CURVES

ELLIPTIC_CURVE = CURVES["id-tc26-gost-3410-12-512-paramSetA"]
TARGET = 0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
TRUSTED_URL = '0.0.0.0:8000'
TRUSTED_USER = ['332', '332']
AMOUNT_FOR_SERVER = 150000000
DEFAULT_PROOF = 100
DEFAULT_HASH = '12323123123'
FAIL = -1
SUCCESS = 0

CANDIDATES_LIST = ['Владимир',
                   'Путин',
                   'Молодец',
                   'Политик',
                   'Лидер',
                   'И. Борец']

CANDIDATE_PUBLIC_KEYS = [

]

KEY_WORDS = {
    'register': 1,
    'register1': 1,
    'register2': 1,
    'register3': 1
}

NODES = [
    '0.0.0.0:5000'
]
