from setuptools import setup

setup(name='td4a',
      version='1.7',
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
          'ansible==2.4.1.0',
          'Flask==0.12.2',
          'netaddr==0.7.19',
          'Twisted==17.9.0',
          'requests==2.18.4',
          'ruamel.yaml==0.15.35'
      ],
      zip_safe=False)
