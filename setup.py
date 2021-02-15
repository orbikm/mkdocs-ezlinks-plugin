from setuptools import setup, find_packages

setup(
  name='mkdocs-ezlinks-plugin',
  version='0.1.0',
  description='A mkdocs plugin that makes linking to other documents EZ.',
  keywords='mkdocs',
  url='https://github.com/orbikm/mkdocs-ezlinks-plugin',
  download_url='https://github.com/orbikm/mkdocs-ezlinks-plugin/archive/v_010.tar.gz',
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
  packages=find_packages(exclude=['*.test']),
  entry_points={
    'mkdocs.plugins': [
      'ezlinks = mkdocs_ezlinks_plugin.plugin:EzLinksPlugin'
    ]
  }
)