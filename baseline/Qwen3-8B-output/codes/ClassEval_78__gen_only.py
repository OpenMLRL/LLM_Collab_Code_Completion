import re

class SplitSentence:
    """
    The class allows to split sentences, count words in a sentence, and process a text file to find the maximum word count.
    """

    def split_sentences(self, sentences_string):
        """
        Split a string into a list of sentences. Sentences end with . or ? and with a space after that. Please note that Mr. also end with . but are not sentences.
        :param sentences_string: string, string to split
        :return:list, split sentence list
        >>> ss = SplitSentence()
        >>> ss.split_sentences("aaa aaaa. bb bbbb bbb? cccc cccc. dd ddd?")
        ['aaa aaaa.', 'bb bbbb bbb?', 'cccc cccc.', 'dd ddd?']
        """
        # Split the string into sentences using regex to find . or ? followed by space
        # But need to exclude cases like Mr.
        # So we can use a regex that matches . or ? followed by space, but not preceded by a word character
        sentences = re.split(r'(?<!\w)\. |\? ', sentences_string)
        # Filter out any empty strings that may result from splitting
        return [s for s in sentences if s]

    def count_words(self, sentence):
        """
        Count the number of words in a sentence. Note that words are separated by spaces and that punctuation marks and numbers are not counted as words.
        :param sentence:string, sentence to be counted, where words are separated by spaces
        :return:int, number of words in the sentence
        >>> ss.count_words("abc def")
        2
        """
        # Split the sentence into words by spaces
        words = sentence.split()
        # Filter out any words that are purely punctuation or numbers
        # Using regex to check if a word is alphanumeric
        filtered_words = [word for word in words if re.match(r'^\w+$', word)]
        return len(filtered_words)

    def process_text_file(self, sentences_string):
        """
        Given a text, return the number of words in the longest sentence
        :param sentences_string: string, undivided long sentence
        :return:int, the number of words in the longest sentence
        >>> ss.process_text_file("aaa aaaa. bb bbbb bbb? cccc ccccccc cc ccc. dd ddd?")
        4
        """
        # Split the text into sentences
        sentences = self.split_sentences(sentences_string)
        # For each sentence, count the words
        max_words = 0
        for sentence in sentences:
            word_count = self.count_words(sentence)
            if word_count > max_words:
                max_words = word_count
        return max_words