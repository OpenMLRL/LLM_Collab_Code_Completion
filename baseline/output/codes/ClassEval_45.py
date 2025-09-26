from PIL import Image, ImageEnhance

class ImageProcessor:
    """
    This is a class to process image, including loading, saving, resizing, rotating, and adjusting the brightness of images.
    """

    def __init__(self):
        """
        Initialize self.image
        """
        self.image = None

    def load_image(self, image_path):
        """
        Use Image util in PIL to open a image
        :param image_path: str, path of image that is to be
        >>> processor.load_image('test.jpg')
        >>> processor.image
        <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=3072x4096 at 0x194F2412A48>
        """
        self.image = Image.open(image_path)

    def save_image(self, save_path):
        """
        Save image to a path if image has opened
        :param save_path: str, the path that the image will be saved
        >>> processor.load_image('test.jpg')
        >>> processor.save_image('test2.jpg')
        """
        self.image.save(save_path)

    def resize_image(self, width, height):
        """
        Risize the image if image has opened.
        :param width: int, the target width of image
        :param height: int, the target height of image
        >>> processor.load_image('test.jpg')
        >>> processor.resize_image(300, 300)
        >>> processor.image.width
        300
        >>> processor.image.height
        300
        """
        self.image = self.image.resize((width, height))

    def rotate_image(self, degrees):
        """
        rotate image if image has opened
        :param degrees: float, the degrees that the image will be rotated
        >>> processor.load_image('test.jpg')
        >>> processor.resize_image(90)
        """
        self.image = self.image.rotate(degrees)

    def adjust_brightness(self, factor):
        """
        Adjust the brightness of image if image has opened.
        :param factor: float, brightness of an image. A factor of 0.0 gives a black image. A factor of 1.0 gives the original image.
        >>> processor.load_image('test.jpg')
        >>> processor.adjust_brightness(0.5)
        """
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(factor)

import unittest
import os


class ImageProcessorTestLoadImage(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()
        # if os.path.exists(self.image_path):
        #     os.remove(self.image_path)

    def test_load_image(self):
        self.processor.load_image(self.image_path)
        self.assertIsNotNone(self.processor.image)

    def test_load_image_2(self):
        self.processor.load_image(self.image_path)
        self.assertEqual(self.processor.image.size, (100, 100))

    def test_load_image_3(self):
        self.processor.load_image(self.image_path)
        self.assertEqual(self.processor.image.mode, "RGB")

    def test_load_image_4(self):
        self.processor.load_image(self.image_path)
        self.assertEqual(self.processor.image.format, "PNG")

    def test_load_image_5(self):
        self.processor.load_image(self.image_path)
        self.assertEqual(self.processor.image.filename, self.image_path)


class ImageProcessorTestSaveImage(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()

    def test_save_image(self):
        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.load_image(self.image_path)
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertIsNotNone(saved_image)

    def test_save_image_2(self):
        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.load_image(self.image_path)
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertEqual(saved_image.size, (100, 100))

    def test_save_image_3(self):
        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.load_image(self.image_path)
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertEqual(saved_image.mode, "RGB")

    def test_save_image_4(self):
        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.load_image(self.image_path)
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertEqual(saved_image.format, "PNG")

    def test_save_image_5(self):
        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.load_image(self.image_path)
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertEqual(saved_image.filename, save_path)


class ImageProcessorTestResizeImage(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()

    def test_resize_image(self):
        self.processor.load_image(self.image_path)
        self.processor.resize_image(30, 15)
        self.assertEqual(self.processor.image.size, (30, 15))

    def test_resize_image_2(self):
        self.processor.load_image(self.image_path)
        self.processor.resize_image(30, 15)
        self.assertEqual(self.processor.image.mode, "RGB")

    def test_resize_image_3(self):
        self.processor.load_image(self.image_path)
        self.processor.resize_image(30, 15)
        self.assertEqual(self.processor.image.format, None)

    def test_resize_image_4(self):
        self.processor.load_image(self.image_path)
        self.processor.resize_image(40, 20)
        self.assertEqual(self.processor.image.mode, "RGB")

    def test_resize_image_5(self):
        self.processor.load_image(self.image_path)
        self.processor.resize_image(50, 25)
        self.assertEqual(self.processor.image.format, None)


class ImageProcessorTestRotateImage(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()

    def test_rotate_image(self):
        self.processor.load_image(self.image_path)
        original_image = self.processor.image
        self.processor.rotate_image(90)
        self.assertTrue(ImageChops.difference(original_image.rotate(90), self.processor.image).getbbox() is None)

    def test_rotate_image_2(self):
        self.processor.load_image(self.image_path)
        original_image = self.processor.image
        self.processor.rotate_image(180)
        self.assertTrue(ImageChops.difference(original_image.rotate(180), self.processor.image).getbbox() is None)

    def test_rotate_image_3(self):
        self.processor.load_image(self.image_path)
        original_image = self.processor.image
        self.processor.rotate_image(270)
        self.assertTrue(ImageChops.difference(original_image.rotate(270), self.processor.image).getbbox() is None)

    def test_rotate_image_4(self):
        self.processor.load_image(self.image_path)
        original_image = self.processor.image
        self.processor.rotate_image(360)
        self.assertTrue(ImageChops.difference(original_image.rotate(360), self.processor.image).getbbox() is None)

    def test_rotate_image_5(self):
        self.processor.load_image(self.image_path)
        original_image = self.processor.image
        self.processor.rotate_image(45)
        self.assertTrue(ImageChops.difference(original_image.rotate(45), self.processor.image).getbbox() is None)


class ImageProcessorTestAdjustBrightness(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()

    def test_adjust_brightness(self):
        self.processor.load_image(self.image_path)
        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(0.3)
        self.processor.adjust_brightness(0.3)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)

    def test_adjust_brightness_2(self):
        self.processor.load_image(self.image_path)
        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(0.5)
        self.processor.adjust_brightness(0.5)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)

    def test_adjust_brightness_3(self):
        self.processor.load_image(self.image_path)
        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(0.7)
        self.processor.adjust_brightness(0.7)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)

    def test_adjust_brightness_4(self):
        self.processor.load_image(self.image_path)
        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(1.0)
        self.processor.adjust_brightness(1.0)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)

    def test_adjust_brightness_5(self):
        self.processor.load_image(self.image_path)
        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(1.5)
        self.processor.adjust_brightness(1.5)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)


class ImageProcessorTestMain(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.image_path = os.path.join(os.path.dirname(__file__), "test.png")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        image.save(self.image_path)

    def tearDown(self):
        self.processor.image.close()

    def test_main(self):
        self.processor.load_image(self.image_path)
        self.assertIsNotNone(self.processor.image)

        enhancer = ImageEnhance.Brightness(Image.open(self.image_path))
        expected_image = enhancer.enhance(0.4)
        self.processor.adjust_brightness(0.4)
        self.assertTrue(ImageChops.difference(expected_image, self.processor.image).getbbox() is None)

        self.processor.resize_image(30, 15)
        self.assertEqual(self.processor.image.size, (30, 15))

        original_image = self.processor.image
        self.processor.rotate_image(90)
        self.assertTrue(ImageChops.difference(original_image.rotate(90), self.processor.image).getbbox() is None)

        save_path = os.path.join(os.path.dirname(__file__), "test_save.png")
        self.processor.save_image(save_path)
        saved_image = Image.open(save_path)
        self.assertIsNotNone(saved_image)
        saved_image.close()