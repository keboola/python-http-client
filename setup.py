import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

project_urls = {
    'Documentation': 'https://htmlpreview.github.io/?https://raw.githubusercontent.com/keboola/'
                     'python-http-client/main/docs/html/keboola/http_client/index.html'
}

setuptools.setup(
    name="keboola.http_client",
    version="1.0.1",
    author="Keboola KDS Team",
    project_urls=project_urls,
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest', 'responses'],
    install_requires=[
        'requests'
    ],
    author_email="support@keboola.com",
    description="General HTTP requests library for Python applications running in Keboola Connection environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keboola/python-http-client",
    packages=['keboola.http_client'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.7'
)
