from setuptools import setup

setup(name='td4a',
      version='2.0.3',
      description='A browser based jinja template renderer',
      url='http://github.com/cidrblock/td4a',
      author='Bradley A. Thornton',
      author_email='brad@thethorntons.net',
      license='MIT',
      include_package_data=True,
      packages=[
          'td4a'
      ],
      scripts=['td4a-server'],
      install_requires=[
          'ansible==2.9.12',
          'Flask==1.1.2',
          'netaddr==0.8.0',
          'Twisted==20.3.0',
          'requests==2.24.0',
          'ruamel.yaml==0.16.10',
          'genson==1.2.1',
          'jsonschema==3.2.0'
      ],
      zip_safe=False)
