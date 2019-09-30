from setuptools import setup

setup(name='bl_core',
      version='0.5.7',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa==1.1.8',
          'rasa-sdk==1.3.3',
          'flask',
          'gevent-websocket',
          'waitress'
      ],
      zip_safe=False)