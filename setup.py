from setuptools import setup

setup(name='bl_core',
      version='0.5.7',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa==1.3.7',
          'rasa-sdk==1.3.3',
          'rasa-nlu==0.15.1',
          'rasa-core==0.14.4',
          'flask',
          'gevent-websocket',
          'waitress'
      ],
      zip_safe=False)