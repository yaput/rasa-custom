from setuptools import setup

setup(name='bl_core',
      version='1.4.12',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa==1.4.5',
          'rasa-sdk==1.4.0',
          'gevent-websocket',
          'waitress',
          'pymessenger'
      ],
      zip_safe=False)