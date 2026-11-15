from setuptools import setup, find_packages
setup(
    name="rat-ctf",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pycryptodome",
        "opencv-python",
        "pynput",
        "mss",
        "pillow",
        "pyinstaller",
    ],
    entry_points={"console_scripts": ["rat=rat.__main__:main"]},
)