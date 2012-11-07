''' Stack a set of images into a set of stacks with no more than a certain number and write a selection file for each stack 

Download to edit and run: :download:`stack_images.py <../../arachnid/snippets/stack_images.py>`

To run:

.. sourcecode:: sh
    
    $ python stack_images.py

.. literalinclude:: ../../arachnid/snippets/stack_images.py
   :language: python
   :lines: 16-
   :linenos:
'''
from arachnid.core.metadata import format, format_utility, spider_utility
from arachnid.core.image import ndimage_file
import glob, numpy


if __name__ == '__main__':

    # Parameters
    
    input_file = "mic_*.spi"
    output_file = "mic_stack_000.spi"
    stack_size = 500
    
    selection = numpy.zeros(stack_size)
    index = 0
    stack_id = 1
    output_file = spider_utility.spider_filename(output_file, stack_id)
    for filename in glob.glob(input_file):
        ndimage_file.write_image(output_file, ndimage_file.read_image(filename), index)
        selection[index] = spider_utility.spider_id(filename)
        index += 1
        if index == stack_size:
            format.write(format_utility.add_prefix(output_file, 'sel'), selection, header=['id'])
            stack_id += 1
            index = 0
            output_file = spider_utility.spider_filename(output_file, stack_id)
    
    if index > 0:
        format.write(format_utility.add_prefix(output_file, 'sel'), selection[:index], header=['id'])
    