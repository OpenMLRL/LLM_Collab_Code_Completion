class URLHandler:
    """
    The class supports to handle URLs, including extracting the scheme, host, path, query parameters, and fragment.
    """

    def __init__(self, url):
        """
        Initialize URLHandler's URL
        """
        self.url = url

    def get_scheme(self):
        """
        get the scheme of the URL
        :return: string, If successful, return the scheme of the URL
        >>> urlhandler = URLHandler("https://www.baidu.com/s?wd=aaa&rsv_spt=1#page")
        >>> urlhandler.get_scheme()
        "https"
        """
        parts = self.url.split("://")
        if len(parts) < 2:
            return None
        return parts[0]

    def get_host(self):
        """
        Get the second part of the URL, which is the host domain name
        :return: string, If successful, return the host domain name of the URL
        >>> urlhandler = URLHandler("https://www.baidu.com/s?wd=aaa&rsv_spt=1#page")
        >>> urlhandler.get_host()
        "www.baidu.com"
        """
        parts = self.url.split("://")
        if len(parts) < 2:
            return None
        url_part = parts[1]
        fragment_index = url_part.find("#")
        if fragment_index != -1:
            url_part = url_part[:fragment_index]
        query_index = url_part.find("?")
        if query_index != -1:
            url_part = url_part[:query_index]
        return url_part

    def get_path(self):
        """
        Get the third part of the URL, which is the address of the resource
        :return: string, If successful, return the address of the resource of the URL
        >>> urlhandler = URLHandler("https://www.baidu.com/s?wd=aaa&rsv_spt=1#page")
        >>> urlhandler.get_path()
        "/s?wd=aaa&rsv_spt=1#page"
        """
        parts = self.url.split("://")
        if len(parts) < 2:
            return None
        url_part = parts[1]
        fragment_index = url_part.find("#")
        if fragment_index != -1:
            url_part = url_part[fragment_index:]
        return url_part

    def get_query_params(self):
        """
        Get the request parameters for the URL
        :return: dict, If successful, return the request parameters of the URL
        >>> urlhandler = URLHandler("https://www.baidu.com/s?wd=aaa&rsv_spt=1#page")
        >>> urlhandler.get_query_params()
        {"wd": "aaa", "rsv_spt": "1"}
        """
        parts = self.url.split("://")
        if len(parts) < 2:
            return {}
        url_part = parts[1]
        fragment_index = url_part.find("#")
        if fragment_index != -1:
            url_part = url_part[:fragment_index]
        query_index = url_part.find("?")
        if query_index != -1:
            query_str = url_part[query_index+1:]
            url_part = url_part[:query_index]
        else:
            query_str = ""
        params = {}
        for param in query_str.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
            else:
                key, value = param, ""
            params[key] = value
        return params

    def get_fragment(self):
        """
        Get the fragment after '#' in the URL
        :return: string, If successful, return the fragment after '#' of the URL
        >>> urlhandler = URLHandler("https://www.baidu.com/s?wd=aaa&rsv_spt=1#page")
        >>> urlhandler.get_fragment()
        "page"
        """
        parts = self.url.split("#")
        if len(parts) < 2:
            return None
        return parts[1]