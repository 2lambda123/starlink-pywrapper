from setuptools import setup, find_packages

setup(name='starlink-pywrapper',
      version='0.1',
      description='Provides a wrapper around the Starlink software suite commands.',
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

