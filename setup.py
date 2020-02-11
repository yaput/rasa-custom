from setuptools import setup

setup(name='bl_core',
      version='1.4.2',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa==1.7.0',
          'rasa-sdk==1.7.0',
          'gevent-websocket',
          'waitress'
      ],
      zip_safe=False)