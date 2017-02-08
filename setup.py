from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='hare',
      version='0.4',
      description='A python ORM based on pymysql with ActiveRecord',
      long_description=long_description,
      keywords='python ORM orm ActiveRecord pymysql raw sql',
      url='https://github.com/bingtel/hare',
      author='bingtel Wang',
      author_email='bingtelwang@163.com',
      license='MIT',
      packages=['hare'],
      install_requires=[
          'PyMySQL',
      ],
      zip_safe=True)
