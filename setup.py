from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['PySide2']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Jean-Francois Bouchard",
    author_email='bouchard.jfrancois@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description="GUI wrapper of spleeter separate command.",
    entry_points={
        'console_scripts': [
            'vspleeter=vspleeter.__main__:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='vspleeter',
    name='vspleeter',
    packages=find_packages(include=['vspleeter', 'vspleeter.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/djieff/vspleeter',
    version='1.0.1',
    zip_safe=False,
)
