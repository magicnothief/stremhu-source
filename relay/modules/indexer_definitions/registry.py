from typing import Dict, List, Optional

from modules.indexer_definitions.base import BaseIndexerIntegration


class IndexerRegistry:
    """Registry to keep track of dynamically added tracker indexers."""

    def __init__(self):
        self._registry: Dict[str, BaseIndexerIntegration] = {}

    def register(self, indexer: BaseIndexerIntegration) -> BaseIndexerIntegration:
        """Register an indexer instance."""
        self._registry[indexer.id] = indexer
        return indexer

    def get(self, id: str) -> Optional[BaseIndexerIntegration]:
        """Retrieve a registered indexer by its ID."""
        return self._registry.get(id)

    def list(self) -> List[BaseIndexerIntegration]:
        """List all registered indexers."""
        return list(self._registry.values())


indexer_registry = IndexerRegistry()
