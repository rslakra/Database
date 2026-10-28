#!/usr/bin/env python3
"""Quick check that Pinecone Local is reachable on localhost:5080."""
from pinecone.grpc import PineconeGRPC

pc = PineconeGRPC(api_key="pclocal", host="http://localhost:5080")
indexes = pc.list_indexes()
print("Pinecone Local connected.")
print("Indexes:", [idx.name for idx in indexes])
