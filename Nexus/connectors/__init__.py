"""Backward-compatible re-export of ``dataio``."""

from dataio import *  # noqa: F403
from dataio import (
    CSVConnector,
    ConnectorError,
    DataConnector,
    DataPort,
    ExcelConnector,
    JSONConnector,
    JSONLConnector,
    get_connector,
    get_connector_for_path,
    register_connector,
)

__all__ = [
    "CSVConnector",
    "ConnectorError",
    "DataConnector",
    "DataPort",
    "ExcelConnector",
    "JSONConnector",
    "JSONLConnector",
    "get_connector",
    "get_connector_for_path",
    "register_connector",
]
