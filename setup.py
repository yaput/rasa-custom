from setuptools import setup

setup(name='bl_core',
      version='1.0.0',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa==1.3.7',
          'rasa-sdk==1.3.3',
      ],
      zip_safe=False)