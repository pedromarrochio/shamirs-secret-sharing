"""
Ponto de entrada da aplicação: menu de terminal do esquema de Shamir.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# src/ contém o pacote shamir; a raiz contém a pasta experiments/.
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from shamir.interface.cli import ShamirCLI  # noqa: E402


def main():
    ShamirCLI().run()


if __name__ == "__main__":
    main()