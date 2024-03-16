import setuptools

extras = {
    'torch': ['torch', 'GitPython', 'gitdb2', 'matplotlib', 'openai'],
    'rlcard': []
}


def _get_version():
    with open('agentpro/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                g = {}
                exec(line, g)
                return g['__version__']
        raise ValueError('`__version__` not defined')


VERSION = _get_version()

setuptools.setup(
    name="agentpro",
    version=VERSION,
    author=
    "Researchers from institutions such as Zhejiang University and the Institute of Software, Chinese Academy of Sciences",
    description=
    "The related environment of Agent-Pro, including Blackjack and Limit Texas Hold`em",
    url="https://github.com/zwq2018/Agent-Pro.git",
    keywords=["NLP", "game", "AI", "RL"],
    include_package_data=True,
    packages=setuptools.find_packages('.'),
    install_requires=[
        'numpy>=1.16.3', 'termcolor', 'dashscope', 'replicate', 'openai'
    ],
    extras_require=extras,
    requires_python='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False)
