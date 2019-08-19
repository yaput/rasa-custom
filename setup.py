from setuptools import setup

setup(name='bl_core',
      version='0.5.3',
      description='Blue Logic Core Bot Package',
      url='',
      author='Blue Logic',
      author_email='anton@bluelogic.ae',
      license='MIT',
      packages=['bl_core'],
      install_requires=[
          'rasa-core==0.14.4',
          'rasa-core-sdk==0.14.0',
          'flask',
          'gevent-websocket',
          'waitress'
      ],
      zip_safe=False)