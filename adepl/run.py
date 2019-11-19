from time import sleep

from adepl.feature_modules.console_writer import ConsoleWriter
from adepl.loaders.hard_coded_loader import HardCodedLoader

loader = HardCodedLoader()
solutions = list(loader.load_solution_instances())
for solution in solutions:
    writer = ConsoleWriter()
    writer.start(solution)  # todo add call for plugins

    solution.start()
    print(f"Solution {solution.name} started")

try:
    while True:
        sleep(1)
except:
    print("Interrupted")

finally:
    for solution in solutions:
        solution.stop()
