from distutils.core import setup

setup(
 name='csv2ofx',
 author = "Dennis Muhlestein",
 version='0.2',
 packages=['csv2ofx'],
 package_dir={'csv2ofx':'src/csv2ofx'},
 scripts=['csv2ofx'],
 package_data={'csv2ofx':['*.xrc']}
)

