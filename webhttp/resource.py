"""Resources

This module contains a handler class for resources.
"""

import os
import mimetypes
import urlparse
import hashlib
import gzip
import zlib

class FileExistError(Exception):
    """Exception which is raised when file does not exist"""
    

class FileAccessError(Exception):
    """Exception which is raised when file exists, but cannot be accessed"""


class Resource:
    """Class for representing a Resource (file)"""

    def __init__(self, uri):
        """Initialize the resource"

        Raises:
            FileExistError: if resource does not exist
            FileAccessError: if resource exists, but cannot be accessed

        Args:
            uri (str): Uniform Resource Identifier
        """
        self.uri = uri
        out = urlparse.urlparse(uri)
        self.path = os.path.join("content/", out.path.lstrip("/"))
        if os.path.isdir(self.path):
            self.path = os.path.join(self.path, "index.html")
        if not os.path.isfile(self.path):
            raise FileExistError
        if not os.access(self.path, os.R_OK):
            raise FileAccessError

    def get_content(self):
        """Get the contents of the resource
        
        Returns:
            str: Contents of the resource
        """
        return open(self.path).read()

    def get_content_type(self):
        """Get the content type, i.e "text/html"

        Returns:
            str: type of content in the resource
        """
        mimetype = mimetypes.guess_type(self.path)
        return mimetype[0]

    def get_content_length(self):
        """Get the length of the resource

        Returns:
            int: length of resource in bytes
        """
        return os.path.getsize(self.path)
    
    # Caching
    def generate_etag(self):
        """Generate the ETag for the resource

        Returns:
            str: ETag for the resource
        """
        h = hashlib.sha224()
        h.update(self.get_content())
        etag = h.hexdigest()
        return etag

	# Encoding
    def get_content_encoding(self):
        """Get the content encoding, i.e "gzip"

        Returns:
            str: encoding used for the resource
        """
        mimetype = mimetypes.guess_type(self.path)
        return mimetype[1]

    def gzip_content(self):
        """Compress the content using gzip

        Returns:
            str: content encoded with gzip
        """
        with open(self.path, "rb") as f_in, gzip.open(self.path + ".gz", "wb") as f_out:
            f_out.writelines(f_in)
        self.path = self.path + ".gz"

    def ungzip_content(self, compressed):
        """Decompress gzip encoded content

        Returns:
            str: content decoded with gzip
        """
        decompressed = zlib.decompress(compressed, 16 + zlib.MAX_WBITS)
        return decompressed
