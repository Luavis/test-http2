from http2.data_socket import DataFrameIO
import io


f = DataFrameIO()
b = b'\x01\x02\x03\x04\x05\x06\x07'

reader = io.BufferedReader(f)

f.write(b)

print(reader.read())
print(reader.read())

f.write(b'\x01\x02\x03\x04\x05\x06\x07\x08')
print(reader.peek())
print(reader.peek())
print(reader.read())
print(reader.read())
