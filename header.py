from http2.hpack.hpack import Decoder

d = Decoder()

print(d.decode(b"A\x8a\xa0\xe4\x1d\x13\x9d\t\xb8\xf0\x00\x0f\x82\x84\x87S\xb8I|\xa5\x89\xd3M\x1fC\xae\xba\x0cA\xa4\xc7\xa9\x8f3\xa6\x9a?\xdf\x9ah\xfa\x1du\xd0b\r&=Ly\xa6\x8f\xbe\xd0\x01w\xfe\x8dH\xe6+\x1e\x0b\x1d\x7f_,|\xfd\xf6\x80\x0b\xbdP\x8e\x9b\xd9\xab\xfaRB\xcb@\xd2_\xa5\x11!'Q\xa4\xeau\xb3m\xfa\xea\x7f\xbe\xd0\x01w\xbe\x8bR\xdc7}\xf6\x80\x0b\xb9\xf4Z\xbe\xfb@\x05\xda\xfa\xe8?\xbe\xd0\x01q\x7fX\x87\xa4~V\x1c\xc5\x80\x1f`\x97\x8aa\xc1\x8a\x10\xae\x15\xc2\xe0\x9cd,\x89\xe6\xd7\x0bL\xbc'\x1ey\xb6\xff@\x92\xb6\xb9\xac\x1c\x85X\xd5 \xa4\xb6\xc2\xada{ZT%\x1f\x011z\xdc\xd0\x7ff\xa2\x81\xb0\xda\xe0S\xfa\xd02\x1a\xa4\x9d\x13\xfd\xa9\x92\xa4\x96\x854\x0c\x8aj\xdc\xa7\xe2\x81\x04A\x04M\x7fjC]t\x17\x91c\xccd\xb0\xdb.\xae\xcb\x8a\x7fY\xb1\xef\xd1\x9f\xe9J\r\xd4\xaab):\x9f\xfbR\xf4\xf6\x1e\x92\xb0\xd3K\x81q4\x06W\x08\x9bSp\xe5\x1d\x86a\xb6]]\x97?"))

print(d.decode(b'\xc5\x82\x00\x84\xb9X\xd3?\x89bQ\xf71\x0fR\xe6!\xff\x87S\x03*/*\xc4\xc3X\x86\xa8\xeb\x10d\x9c\xbf\xc2@\x85\xae\xc1\xcdH\xff\x86\xa8\xeb\x10d\x9c\xbfs\x90\x9d)\xad\x17\x18b\x83\x90tNt&\xe3\xc0\x00\x18\xc2'))
