from time import sleep

from adepl.feature_modules.console_merger import ConsoleMerger
from adepl.feature_modules.console_writer import ConsoleWriter
from adepl.loaders.hard_coded_loader import HardCodedLoader

loader = HardCodedLoader()
solutions = list(loader.load_solution_instances())
for solution in solutions:
    solution.add_plugins(
        ConsoleWriter(),
        ConsoleMerger("^worker.*", "merged_workers")
    )

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
