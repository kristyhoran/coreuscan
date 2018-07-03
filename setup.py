from setuptools import setup


setup(name = 'coreuscan',
      version = '0.1',
      description = 'A tool to download MLST schemes for bacterial genomics',
      url = 'https://github.com/kristyhoran/coreuscan.git',
      author = 'Kristy Horan',
      author_email= 'kristyhoran15@gmail.com',
      license= ' ',
      packages = ['coreuscan'],
      install_requires = ['requests', 'argparse',  'bs4', 'wget'],
      entry_points={'console_scripts': ['coreuscan = coreuscan.coreuscan:main']}
      )