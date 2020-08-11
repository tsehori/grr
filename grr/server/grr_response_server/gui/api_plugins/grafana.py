#!/usr/bin/env python
# Lint as: python3
"""API handlers for Grafana."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from grr_response_core.lib.rdfvalues import structs as rdf_structs
from grr_response_proto.api import grafana_pb2
from grr_response_server.gui import api_call_handler_base


class ApiCheckConnectionResult(rdf_structs.RDFProtoStruct):
  protobuf = grafana_pb2.ApiCheckConnectionResult
  # rdf_deps = []


class ApiCheckConnectionHandler(api_call_handler_base.ApiCallHandler):
  """Checks whether the connection to Fleetspeak database is established."""

  result_type = ApiCheckConnectionResult

  def Handle(self, args, token):
    return ApiCheckConnectionResult(connection_ok=True)
