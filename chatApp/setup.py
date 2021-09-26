from setuptools import setup

setup(name='chatapp',
      version='0.1',
      description='A module containing all required code for chatApp',
      url='https://github.com/Mark-Suckau/ChatApp',
      author='Mark Suckau',
      author_email='mark.suckau.coding@gmail.com',
      license='MIT',
      packages=['client', 'server', 'shared'],
      zip_safe=False)