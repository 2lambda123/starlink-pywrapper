from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='starlink-pywrapper',
      version='0.3',
      description='Provides a wrapper around the Starlink software suite commands.',
      long_description=readme(),
      classifiers=[
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      ],
      url='http://github.com/Starlink/starlink-pywrapper',
      author='SF Graves',
      author_email='s.graves@eaobservatory.org',
      license='GPLv3+',
      packages=find_packages(),
      include_package_data=True,
      install_requires = [
        'starlink-pyhds',
        ],
      )

