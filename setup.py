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
  version='0.1.0',
  description='A Euclidean Geometry based library',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='',
  project_urls={
            #"Bug Tracker": "",
            #"Documentation": ,
            "Source Code": "https://github.com/joshuavaron/euclipy",
        },
  author='Joshua Varon',    
  author_email='joshuavaron@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='geometry, math',
  packages=find_packages(include=['euclipy']),
  install_requires=[''] 
)