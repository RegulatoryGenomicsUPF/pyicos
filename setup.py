from distutils.core import setup

setup(name='Pyicos',
      version='0.8.5.2',
      description='Mapped reads analysis tool and library',
      author=u'Juan Gonzalez_Vallinas',
      author_email='juanramon.gonzalezvallinas@upf.edu',
      url='http://regulatorygenomics.upf.edu/pyicos',
      packages = ['pyicoslib.lib', 'chrdesc'],
      data_files = [('chrdesc', ['chrdesc/mm8', 'chrdesc/mm9', 'chrdesc/hg18', 'chrdesc/hg19']), ('test_files', ['test_files/p300.bed', 'test_files/control.bed'])],
      scripts = ['pyicos'],
      py_modules = ['pyicoslib.core', 'pyicoslib.operations', 'pyicoslib.parser', 'pyicoslib.defaults']
     )

