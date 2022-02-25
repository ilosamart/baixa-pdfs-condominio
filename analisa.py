import os

import tabula


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

dfs = tabula.read_pdf(f'{ROOT_DIR}/downloads/EXTRATO-2021-01', lattice=True, guess=True, pages='all')

print(dfs[5])

tabula.convert_into_by_batch(f"{ROOT_DIR}/downloads/", output_format='csv', pages='all')