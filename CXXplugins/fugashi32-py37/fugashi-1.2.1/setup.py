import pathlib
import setuptools
import subprocess
from setuptools import setup
from distutils.extension import Extension
import sys

from fugashi_util import check_libmecab

# get the build parameters
if sys.argv[1] == "sdist":
    # hack for automated builds
    output, data_files = [], []
else:
    output, data_files = check_libmecab()

# pad the list in case something's missing
mecab_config = list(output) + ([''] * 5)
include_dirs = mecab_config[0].split()
library_dirs = mecab_config[1].split()
libraries = mecab_config[2].split()
extra_objects = mecab_config[3].split()
extra_link_args = mecab_config[4].split()

extensions = Extension('fugashi.fugashi', 
        ['fugashi/fugashi.pyx'], 
        libraries=libraries,
        library_dirs=library_dirs,
        include_dirs=include_dirs,
        extra_objects=extra_objects,
        extra_link_args=extra_link_args)

setup(name='fugashi', 
      use_scm_version=True,
      author="Paul O'Leary McCann",
      author_email="polm@dampfkraft.com",
      description="A Cython MeCab wrapper for fast, pythonic Japanese tokenization.",
      long_description=pathlib.Path('README.md').read_text('utf8'),
      long_description_content_type="text/markdown",
      url="https://github.com/polm/fugashi",
      packages=setuptools.find_packages(),
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Natural Language :: Japanese",
          ],
      python_requires='>=3.7',
      ext_modules=[extensions],
      data_files=data_files,
      entry_points={
          'console_scripts': [
              'fugashi = fugashi.cli:main',
              'fugashi-info = fugashi.cli:info',
              'fugashi-build-dict = fugashi.cli:build_dict',
      ]},
      extras_require={
          'unidic': ['unidic'],
          'unidic-lite': ['unidic-lite'],
      },
      setup_requires=['wheel', 'Cython', 'setuptools_scm'])
