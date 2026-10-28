#!/usr/bin/env python3
"""Quick check that Weaviate is reachable on localhost:8080."""
import weaviate

with weaviate.connect_to_local() as client:
    print("Weaviate ready:", client.is_ready())
    print("Collections:", list(client.collections.list_all()))
