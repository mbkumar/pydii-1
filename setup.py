import os

from setuptools import setup

SETUP_PTH = os.path.dirname(os.path.abspath(__file__))

setup(
        name="pydii",
        version="1.0.0",
        install_requires=["pymatgen>=3.0.6", "sympy>=0.7.5", "numpy>=1.8"],
        author="Bharat Medasani",
        author_email="mbkumar@gmail.com",
        url="http://github.com/mbkumar/pydii",
        description="PyDII is a python tool to evaluate point defect " 
                  "concentrations and micro-alloy solute site preference "
                  "in intermetallics",
        classifiers=[
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Development Status :: 1 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Scientific/Engineering :: Chemistry",
            "Topic :: Software Development :: Libraries :: Python Modules"
            ],
        license="MIT",
        scripts=glob.glob(os.path.join(SETUP_PTH, "scripts", "*"))
)
