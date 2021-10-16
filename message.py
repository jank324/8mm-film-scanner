import struct

import cv2


def deserialize(serialized):
    type_byte = serialized[4]
    type_code = struct.unpack("B", type_byte)
    
    if type_code == Image._type_code:
        return Image.deserialize(serialized)
    elif type_code == Advance._type_byte:
        return Advance.deserialize(serialized)
    else:
        raise NotImplementedError


class Message:

    @classmethod
    def deserialize(cls, serialized):
        return cls()

    @property
    def _type_byte(self):
        struct.pack("B", self._type_code)
    
    def _wrap(self, content):
        if content is not None:
            length = struct.calcsize(">L") + struct.calcsize("B") + len(content)
            length_bytes = struct.pack(">L", length)

            return length_bytes + self._type_byte + content
        else:
            length = struct.calcsize(">L") + struct.calcsize("B")
            length_bytes = struct.pack(">L", length)

            return length_bytes + self._type_byte
    
    @property
    def serialized(self):
        return self._wrap(None)


class Image(Message):
    
    _type_code = 0

    def __init__(self, image, jpeg_quality=50):
        self.image = image
        self._jpeg_quality = jpeg_quality

    @classmethod
    def deserialize(cls, serialized):
        pass

    @property
    def serialized(self):
        encode_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), self._jpeg_quality]
        _, encoded = cv2.imencode(".jpeg", self.image, params=encode_parameters)
        image_bytes = encoded.tobytes()

        return self._wrap(image_bytes)


class Advance(Message):

    type_code = 1
