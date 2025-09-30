import urllib.parse

class UrlPath:
    """
    The  class is a utility for encapsulating and manipulating the path component of a URL, including adding nodes, parsing path strings, and building path strings with optional encoding.
    """

    def __init__(self):
        """
        Initializes the UrlPath object with an empty list of segments and a flag indicating the presence of an end tag.
        """
        self.segments = []
        self.with_end_tag = False

    def add(self, segment):
        """
        Adds a segment to the list of segments in the UrlPath.
        :param segment: str, the segment to add.
        >>> url_path = UrlPath()
        >>> url_path.add('foo')
        >>> url_path.add('bar')

        url_path.segments = ['foo', 'bar']
        """
        self.segments.append(segment)

    def parse(self, path, charset):
        """
        Parses a given path string and populates the list of segments in the UrlPath.
        :param path: str, the path string to parse.
        :param charset: str, the character encoding of the path string.
        >>> url_path = UrlPath()
        >>> url_path.parse('/foo/bar/', 'utf-8')

        url_path.segments = ['foo', 'bar']
        """
        # Fix the path by removing leading and trailing slashes
        fixed_path = self.fix_path(path)
        # Split the path into segments
        segments = fixed_path.split('/')
        # Filter out any empty strings from the split
        self.segments = [seg for seg in segments if seg]
        # Check if the original path ended with a slash to determine the end tag
        self.with_end_tag = path.endswith('/')

    @staticmethod
    def fix_path(path):
        """
        Fixes the given path string by removing leading and trailing slashes.
        :param path: str, the path string to fix.
        :return: str, the fixed path string.
        >>> url_path = UrlPath()
        >>> url_path.fix_path('/foo/bar/')
        'foo/bar'

        """
        # Remove leading and trailing slashes
        if not path:
            return ''
        # Check if the path starts with a slash
        starts_with_slash = path.startswith('/')
        # Check if the path ends with a slash
        ends_with_slash = path.endswith('/')
        # Strip the slashes
        stripped_path = path.strip('/')
        # If the path was originally empty, return it as is
        if stripped_path == '':
            return ''
        # Re-add the slashes if necessary
        if starts_with_slash or ends_with_slash:
            # If both start and end with slash, we need to add one at the end
            if starts_with_slash and ends_with_slash:
                stripped_path += '/'
            # If only starts with slash, add one at the end
            elif starts_with_slash:
                stripped_path += '/'
            # If only ends with slash, add one at the start
            elif ends_with_slash:
                stripped_path = '/' + stripped_path
        return stripped_path