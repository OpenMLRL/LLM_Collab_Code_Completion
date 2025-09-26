import re
import string
import gensim
from bs4 import BeautifulSoup

class HtmlUtil:
    """
    This is a class as util for html, supporting for formatting and extracting code from HTML text, including cleaning up the text and converting certain elements into specific marks.
    """

    def __init__(self):
        """
        Initialize a series of labels
        """
        self.SPACE_MARK = '-SPACE-'
        self.JSON_MARK = '-JSON-'
        self.MARKUP_LANGUAGE_MARK = '-MARKUP_LANGUAGE-'
        self.URL_MARK = '-URL-'
        self.NUMBER_MARK = '-NUMBER-'
        self.TRACE_MARK = '-TRACE-'
        self.COMMAND_MARK = '-COMMAND-'
        self.COMMENT_MARK = '-COMMENT-'
        self.CODE_MARK = '-CODE-'

    @staticmethod
    def __format_line_feed(text):
        """
        Replace consecutive line breaks with a single line break
        :param text: string with consecutive line breaks
        :return:string, replaced text with single line break
        """
        return re.sub(r'\n+', '\n', text)

    def format_line_html_text(self, html_text):
        """
        get the html text without the code, and add the code tag -CODE- where the code is
        :param html_text:string
        :return:string
        """
        soup = BeautifulSoup(html_text, 'html.parser')
        formatted_text = ''
        for tag in soup.find_all():
            if tag.name == 'pre':
                formatted_text += f'{self.CODE_MARK} {tag.text} {self.CODE_MARK}\n'
            else:
                formatted_text += tag.text
        return formatted_text

    def extract_code_from_html_text(self, html_text):
        """
        extract codes from the html body
        :param html_text: string, html text
        :return: the list of code
        """
        soup = BeautifulSoup(html_text, 'html.parser')
        code_tags = soup.find_all('pre')
        codes = [tag.text for tag in code_tags]
        return codes

# Example usage
html_text = """
<html>
<body>
    <h1>Title</h1>
    <p>This is a paragraph.</p>
    <pre>print('Hello, world!')</pre>
    <p>Another paragraph.</p>
    <pre><code>for i in range(5):
    print(i)</code></pre>
</body>
</html>
"""

htmlutil = HtmlUtil()
formatted_text = htmlutil.format_line_html_text(html_text)
print(formatted_text)

codes = htmlutil.extract_code_from_html_text(html_text)
print(codes)