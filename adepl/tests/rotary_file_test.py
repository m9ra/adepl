from time import sleep

from adepl.utils.rotary_files.reader import Reader
from adepl.utils.rotary_files.writer import Writer

writer = Writer("/tmp/rotary_test", 5)
reader = Reader("/tmp/rotary_test")


def data_reader(data: bytes):
    print(f"R: {data.decode('utf8')}")


reader.subscribe(data_reader)
writer.write("1234567")
writer.flush()

for i in range(10):
    sleep(1)

    m = f"X{i}Y"
    print(f"W: {m}")
    writer.write(m)
    writer.flush()

reader.close()
writer.write("NNNN")
writer.flush()

writer.close()

sleep(5)
