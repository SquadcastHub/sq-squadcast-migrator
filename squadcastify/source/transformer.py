from typing import Protocol


class Transformer(Protocol):
    def transform(self):
        """Run the migration process."""
        raise NotImplementedError("Migrator must implement the run method.")
