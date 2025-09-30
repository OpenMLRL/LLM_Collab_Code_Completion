import xml.etree.ElementTree as ET


class XMLProcessor:
    """
    This is a class as XML files handler, including reading, writing, processing as well as finding elements in a XML file.
    """

    def __init__(self, file_name):
        """
        Initialize the XMLProcessor object with the given file name.
        :param file_name:string, the name of the XML file to be processed.
        """
        self.file_name = file_name
        self.root = None

    def read_xml(self):
        """
        Reads the XML file and returns the root element.
        :return: Element, the root element of the XML file.
        >>> xml_processor = XMLProcessor('test.xml')
        >>> root_element = xml_processor.read_xml()
        >>> print(root_element)
        <Element 'root' at 0x7f8e3b7eb180>
        """
        tree = ET.parse(self.file_name)
        self.root = tree.getroot()
        return self.root

    def write_xml(self, file_name):
        """
        Writes the XML data to the specified file.
        :param file_name: string, the name of the file to write the XML data.
        :return: bool, True if the write operation is successful, False otherwise.
        >>> xml_processor = XMLProcessor('test.xml')
        >>> root = xml_processor.read_xml()
        >>> success = xml_processor.write_xml('output.xml')
        >>> print(success)
        True
        """
        try:
            tree = ET.ElementTree(self.root)
            tree.write(file_name, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error writing XML: {e}")
            return False

    def process_xml_data(self, file_name):
        """
        Modifies the data in XML elements and writes the updated XML data to a new file.
        :param file_name: string, the name of the file to write the modified XML data.
        :return: bool, True if the write operation is successful, False otherwise.
        >>> xml_processor = XMLProcessor('test.xml')
        >>> root = xml_processor.read_xml()
        >>> success = xml_processor.process_xml_data('processed.xml')
        >>> print(success)
        True
        """
        try:
            # Example modification: add a new element
            new_element = ET.SubElement(self.root, 'processed')
            new_element.text = 'Modified data'
            tree = ET.ElementTree(self.root)
            tree.write(file_name, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error processing XML: {e}")
            return False

    def find_element(self, element_name):
        """
        Finds the XML elements with the specified name.
        :param element_name: string, the name of the elements to find.
        :return: list, a list of found elements with the specified name.
        >>> xml_processor = XMLProcessor('test.xml')
        >>> root = xml_processor.read_xml()
        >>> items = xml_processor.find_element('item')
        >>> for item in items:
        >>>     print(item.text)
        apple
        banana
        orange
        """
        found_elements = self.root.findall(f'.//{element_name}')
        return found_elements

import unittest
import os


class XMLProcessorTestReadXml(unittest.TestCase):
    def test_read_xml_1(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')
        self.assertEqual(lst[2].text, 'orange')

        os.remove('test.xml')

    def test_read_xml_2(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>aaa</item>\n    <item>bbb</item>\n    <item>ccc</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'aaa')
        self.assertEqual(lst[1].text, 'bbb')
        self.assertEqual(lst[2].text, 'ccc')

        os.remove('test.xml')

    def test_read_xml_3(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'apple')

        os.remove('test.xml')

    def test_read_xml_4(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')

        os.remove('test.xml')

    def test_read_xml_5(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'orange')

        os.remove('test.xml')

    def test_read_xml_6(self):
        self.xml_file = ''
        self.processor = XMLProcessor(self.xml_file)

        root = self.processor.read_xml()
        self.assertIsNone(root)


class XMLProcessorTestWriteXml(unittest.TestCase):
    def test_write_xml_1(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')
        self.assertEqual(lst[2].text, 'orange')

        os.remove('output.xml')
        os.remove('test.xml')

    def test_write_xml_2(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')

        os.remove('output.xml')
        os.remove('test.xml')

    def test_write_xml_3(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'apple')

        os.remove('output.xml')
        os.remove('test.xml')

    def test_write_xml_4(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>aaa</item>\n    <item>bbb</item>\n    <item>ccc</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'aaa')
        self.assertEqual(lst[1].text, 'bbb')
        self.assertEqual(lst[2].text, 'ccc')

        os.remove('output.xml')
        os.remove('test.xml')

    def test_write_xml_5(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'orange')

        os.remove('output.xml')
        os.remove('test.xml')

    def test_write_xml_6(self):
        self.xml_file = ''
        self.processor = XMLProcessor(self.xml_file)

        result = self.processor.write_xml("")
        self.assertFalse(result)


class XMLProcessorTestProcessXmlData(unittest.TestCase):
    def test_process_xml_data_1(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'APPLE')
        self.assertEqual(lst[1].text, 'BANANA')
        self.assertEqual(lst[2].text, 'ORANGE')

        os.remove('processed.xml')
        os.remove('test.xml')

    def test_process_xml_data_2(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'APPLE')
        self.assertEqual(lst[1].text, 'BANANA')

        os.remove('processed.xml')
        os.remove('test.xml')

    def test_process_xml_data_3(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'APPLE')

        os.remove('processed.xml')
        os.remove('test.xml')

    def test_process_xml_data_4(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'APPLE')
        self.assertEqual(lst[1].text, 'ORANGE')

        os.remove('processed.xml')
        os.remove('test.xml')

    def test_process_xml_data_5(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>aaa</item>\n    <item>bbb</item>\n    <item>ccc</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'AAA')
        self.assertEqual(lst[1].text, 'BBB')
        self.assertEqual(lst[2].text, 'CCC')

        os.remove('processed.xml')
        os.remove('test.xml')


class XMLProcessorTestFindElement(unittest.TestCase):
    def test_find_element_1(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0].text, 'apple')
        self.assertEqual(elements[1].text, 'banana')
        self.assertEqual(elements[2].text, 'orange')

        os.remove('test.xml')

    def test_find_element_2(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0].text, 'apple')
        self.assertEqual(elements[1].text, 'banana')

        os.remove('test.xml')

    def test_find_element_3(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].text, 'apple')

        os.remove('test.xml')

    def test_find_element_4(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0].text, 'apple')
        self.assertEqual(elements[1].text, 'orange')

        os.remove('test.xml')

    def test_find_element_5(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>aaa</item>\n    <item>bbb</item>\n    <item>ccc</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0].text, 'aaa')
        self.assertEqual(elements[1].text, 'bbb')
        self.assertEqual(elements[2].text, 'ccc')

        os.remove('test.xml')


class XMLProcessorTest(unittest.TestCase):
    def test_XMLProcessor(self):
        with open('test.xml', 'w') as f:
            f.write('<root>\n    <item>apple</item>\n    <item>banana</item>\n    <item>orange</item>\n</root>')
        self.xml_file = 'test.xml'
        self.processor = XMLProcessor(self.xml_file)
        tree = ET.parse(self.processor.file_name)
        self.processor.root = tree.getroot()

        root = self.processor.read_xml()
        self.assertIsNotNone(root)
        lst = root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')
        self.assertEqual(lst[2].text, 'orange')

        file_name = 'output.xml'
        result = self.processor.write_xml(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'apple')
        self.assertEqual(lst[1].text, 'banana')
        self.assertEqual(lst[2].text, 'orange')

        os.remove('output.xml')

        file_name = 'processed.xml'
        result = self.processor.process_xml_data(file_name)
        self.assertTrue(result)

        processor1 = XMLProcessor(file_name)
        tree1 = ET.parse(processor1.file_name)
        processor1.root = tree1.getroot()

        self.assertIsNotNone(processor1.root)
        lst = processor1.root.findall('item')
        self.assertEqual(lst[0].text, 'APPLE')
        self.assertEqual(lst[1].text, 'BANANA')
        self.assertEqual(lst[2].text, 'ORANGE')

        os.remove('processed.xml')

        element_name = 'item'
        root = self.processor.read_xml()
        elements = self.processor.find_element(element_name)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0].text, 'apple')
        self.assertEqual(elements[1].text, 'banana')
        self.assertEqual(elements[2].text, 'orange')

        os.remove('test.xml')