from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in attendance_customization/__init__.py
from attendance_customization import __version__ as version

setup(
	name='attendance_customization',
	version=version,
	description='Application to customize the Employee attendance report',
	author='Chris',
	author_email='christophernjogu@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
