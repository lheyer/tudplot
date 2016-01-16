from setuptools import setup

setup(
    name='tudplot',
    description='Matplotlib styling in TU Darmstadt corporate design',
    author_email='niels.mueller@physik.tu-darmstadt.de',

    packages=['tudplot', ],
    version='1.0.0',
    requires=['matplotlib', 'seaborn'],
)
