from typing import List, Protocol

from squadcastify.terraform.models.base import TerraformResource


class Transformer(Protocol):
    def transform(self) -> List[TerraformResource]:
        """Run the migration process."""

        raise NotImplementedError("Migrator must implement the run method.")
