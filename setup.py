from setuptools import setup, find_packages

description = 'A mkdocs plugin that makes linking to other documents easy.'
long_description = description

with open("README.md", 'r') as f:
  long_description = f.read()

setup(
  name='mkdocs-ezlinks-plugin',
  version='0.1.3',
  description=description,
  long_description=long_description,
  long_description_content_type='text/markdown',
  keywords='mkdocs',
  url='https://github.com/orbikm/mkdocs-ezlinks-plugin',
  download_url='https://github.com/orbikm/mkdocs-ezlinks-plugin/archive/v_0.1.3.tar.gz',
  author='Mick Orbik',
  author_email='mick.orbik@gmail.com',
  license='MIT',
  python_requires='>=3.6',
  install_requires=[
    'mkdocs>=1.1.0',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only'
  ],
  packages=find_packages(exclude=['test.*']),
  entry_points={
    'mkdocs.plugins': [
      'ezlinks = mkdocs_ezlinks_plugin.plugin:EzLinksPlugin'
    ]
  }
)
