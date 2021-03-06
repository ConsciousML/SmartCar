import os

from random import randint
from tqdm import tqdm

from ..layers.draw import Background, DrawLines
from ..layers.utils.symmetric import Symmetric
from ..layers.layer import Layer


class Simulator():
    '''The simulator is composed by a list of transforming layers

    Attributes:
        layers: A list of Layer objects.
        input_images: A list of input images.
    '''

    def __init__(self, layers=None):
        """Sets the layers attribute"""
        if layers is None:
            layers = []
        if not isinstance(layers, list):
            raise ValueError('')
        if layers != [] and not all([isinstance(l, Layer) for l in layers]):
            raise ValueError('')

        self.layers = layers
        self.input_images = None

    def add(self, layer):
        """Adds a layer to the layer list"""
        self.layers.append(layer)

    def generate(self, n_examples, path):
        """Generates the images

        Args:
            n_examples: A positive integer for the number of images to generate.
            path: A string for the output path.
        """
        if n_examples <= 0:
            raise ValueError('n_examples must be strictly positive, not {}'.format(n_examples))
        if len(self.layers) == 0:
            raise ValueError('there are no layers in the simulator model')
        if not isinstance(self.layers[0], Background):
            raise ValueError('')
        if len(self.layers[0].backgrounds) == 0:
            raise ValueError('')

        self.input_images = self.layers[0].backgrounds

        if os.path.exists(path):
            print('The path `{}` already exists !'.format(path))
        else:
            os.makedirs(path)

        for i in tqdm(range(n_examples)):
            index = randint(0, len(self.input_images)-1)
            ii = self.input_images[index].copy()
            new_img, new_name, new_img2, new_name2= self.generate_one_image(ii)
            new_img.save(os.path.join(path, 'frame_' + str(i) + new_name))
            new_img2.save(os.path.join(path, 'frame_' + str(i) + new_name2))

    def generate_one_image(self, img):
        """Generates one image

        Args:
            img: A PIL image.
        """
        if img is None:
            raise ValueError('img must be different from None')

        sym = False

        gas = 0.5
        angle = 0
        im = img.copy()
        for layer in self.layers:
            if not isinstance(layer, Background):
                if isinstance(layer, DrawLines):
                    im, angle, gas = layer.call(im)
                elif isinstance(layer, Symmetric):
                    im, sym = layer.call(im)
                else:
                    im = layer.call(im)

        im2 = im.copy()
        im2, s= Symmetric(proba=1).call(im2)

        if sym:
            angle = -angle
        name = '_gas_' + str(gas) + '_dir_' +  str(angle) + '.jpg'
        name2 = '_gas_' + str(gas) + '_dir_' +  str(-angle) + '.jpg'
        return im, name, im2, name2


    def summary(self):
        """Prints the summary of the generation"""
        summaries = [layer.summary() for layer in self.layers]
        s = 'Summary:\nNumber of layers: {}\n{}'.format(len(self.layers), '\n'.join(summaries))
        return s
