from setuptools import setup, find_packages

# with open('requirements.txt') as f:
#     requirements = f.read()

setup(
    name="iharp_vector_predicate",
    version="0.1.5",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jupyter",
        "xarray",
        "netcdf4",
        "h5py",
        "dask[complete]",
        "pandas",
        "numpy",
        "plotly",
        "cdsapi",
        "shapely",
        "matplotlib",
        "geopandas",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iharp3/iharp-vector-predicate",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)