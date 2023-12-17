"""Euclipy - a symbolic Euclidean geometry package
"""
from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='euclipy',
  version='1.1.1',
  description='A Synthetic Euclidean Geometry based library',
  long_description=open('README.md', encoding='utf-8').read(),
  long_description_content_type='text/markdown',
  url='',
  project_urls={
            #"Bug Tracker": "",
            "Documentation": "https://joshuavaron.github.io/euclipy/",
            "Source Code": "https://github.com/joshuavaron/euclipy",
        },
  author='Joshua Varon',
  author_email='32440072+joshuavaron@users.noreply.github.com',
  license='MIT',
  classifiers=classifiers,
  keywords='geometry, math',
  packages=find_packages(include=['euclipy']),
  install_requires=['sympy']
)
