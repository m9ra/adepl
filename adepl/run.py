from time import sleep

from adepl.loaders.hard_coded_loader import HardCodedLoader

loader = HardCodedLoader()
for solution in loader.load_solution_instances():
    solution.start()

while True:
    sleep(1)
