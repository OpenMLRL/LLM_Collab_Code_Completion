import PyPDF2

class PDFHandler:
    """
    The class allows merging multiple PDF files into one and extracting text from PDFs using PyPDF2 library.
    """

    def __init__(self, filepaths):
        """
        takes a list of file paths filepaths as a parameter.
        It creates a list named readers using PyPDF2, where each reader opens a file from the given paths.
        """
        self.filepaths = filepaths
        self.readers = [PyPDF2.PdfFileReader(fp) for fp in filepaths]

    def merge_pdfs(self, output_filepath):
        """
        Read files in self.readers which stores handles to multiple PDF files.
        Merge them to one pdf and update the page number, then save in disk.
        :param output_filepath: str, ouput file path to save to
        :return: str, "Merged PDFs saved at {output_filepath}" if successfully merged
        >>> handler = PDFHandler(['a.pdf', 'b.pdf'])
        >>> handler.merge_pdfs('out.pdf')
        Merged PDFs saved at out.pdf
        """
        writer = PyPDF2.PdfFileWriter()
        for reader in self.readers:
            for page in reader.pages:
                writer.addPage(page)
        with open(output_filepath, 'wb') as output_file:
            writer.write(output_file)
        return f"Merged PDFs saved at {output_filepath}"

    def extract_text_from_pdfs(self):
        """
        Extract text from pdf files in self.readers
        :return pdf_texts: list of str, each element is the text of one pdf file
        >>> handler = PDFHandler(['a.pdf', 'b.pdf'])
        >>> handler.extract_text_from_pdfs()
        ['Test a.pdf', 'Test b.pdf']
        """
        pdf_texts = []
        for reader in self.readers:
            text = ''
            for page in reader.pages:
                text += page.extractText()
            pdf_texts.append(text)
        return pdf_texts

import os
import unittest
from PyPDF2 import PdfFileReader
from reportlab.pdfgen import canvas


class TestPDFHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_files = ["test1.pdf", "test2.pdf"]
        cls.test_text = ["This is a test1.", "This is a test2."]
        for i in range(2):
            c = canvas.Canvas(cls.test_files[i])
            c.drawString(100, 100, cls.test_text[i])
            c.showPage()
            c.save()

    @classmethod
    def tearDownClass(cls):
        for filename in cls.test_files:
            os.remove(filename)
        os.remove("merged.pdf")



class PDFHandlerTestMergePdfs(unittest.TestCase):
    def setUp(self) -> None:
        TestPDFHandler.setUpClass()

    def tearDown(self) -> None:
        TestPDFHandler.tearDownClass()

    def test_merge_pdfs(self):
        TestPDFHandler.setUpClass()
        handler = PDFHandler(TestPDFHandler.test_files)
        result = handler.merge_pdfs("merged.pdf")
        self.assertEqual("Merged PDFs saved at merged.pdf", result)
        self.assertTrue(os.path.exists("merged.pdf"))



class PDFHandlerTestExtractTextFromPdfs(unittest.TestCase):
    def setUp(self) -> None:
        TestPDFHandler.setUpClass()

    def test_extract_text_from_pdfs(self):
        TestPDFHandler.setUpClass()
        handler = PDFHandler(TestPDFHandler.test_files)
        result = handler.extract_text_from_pdfs()
        self.assertEqual(result, ["This is a test1.\n", "This is a test2.\n"])


class PDFHandlerTestMain(unittest.TestCase):
    def setUp(self) -> None:
        TestPDFHandler.setUpClass()

    def tearDown(self) -> None:
        TestPDFHandler.tearDownClass()

    def test_main(self):
        TestPDFHandler.setUpClass()
        handler = PDFHandler(TestPDFHandler.test_files)
        result = handler.merge_pdfs("merged.pdf")
        self.assertEqual("Merged PDFs saved at merged.pdf", result)
        self.assertTrue(os.path.exists("merged.pdf"))

        result = handler.extract_text_from_pdfs()
        self.assertEqual(result, ["This is a test1.\n", "This is a test2.\n"])