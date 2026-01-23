"""GraphStoreAdapter factory."""

import logging

from gptdb.storage.graph_store.base import GraphStoreBase
from gptdb_ext.storage.graph_store.neo4j_store import Neo4jStore
from gptdb_ext.storage.graph_store.tugraph_store import TuGraphStore
from gptdb_ext.storage.knowledge_graph.community.base import GraphStoreAdapter
from gptdb_ext.storage.knowledge_graph.community.neo4j_store_adapter import (
    Neo4jStoreAdapter,
)
from gptdb_ext.storage.knowledge_graph.community.tugraph_store_adapter import (
    TuGraphStoreAdapter,
)

logger = logging.getLogger(__name__)


class GraphStoreAdapterFactory:
    """Factory for community store adapter."""

    @staticmethod
    def create(graph_store: GraphStoreBase) -> GraphStoreAdapter:
        """Create a GraphStoreAdapter instance.

        Args:
            - graph_store_type: graph store type Memory, TuGraph, Neo4j
        """
        if isinstance(graph_store, TuGraphStore):
            return TuGraphStoreAdapter(graph_store)
        elif isinstance(graph_store, Neo4jStore):
            # Neo4j has its own adapter due to different syntax and data model
            return Neo4jStoreAdapter(graph_store)
        else:
            raise Exception(
                "create community store adapter for %s failed",
                graph_store.__class__.__name__,
            )
