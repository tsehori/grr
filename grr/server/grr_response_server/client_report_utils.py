#!/usr/bin/env python
# Lint as: python3
"""Utilities for managing client-report data."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
from typing import Dict, Optional, Text

from grr_response_core.lib import rdfvalue
from grr_response_core.lib import time_utils
from grr_response_core.lib import util
from grr_response_core.lib.rdfvalues import stats as rdf_stats
from grr_response_core.lib.rdfvalues import structs as rdf_structs
from grr_response_core.stats import metrics
from grr_response_server import data_store


OS_RELEASE_BREAKDOWN = metrics.Gauge("os_release_breakdown",
                                     int,
                                     fields=[("client_labels", str)])
OS_TYPE_BREAKDOWN = metrics.Gauge("os_type_breakdown",
                                     int,
                                     fields=[("client_labels", str)])
GRR_VERSION_BREAKDOWN = metrics.Gauge("grr_version_breakdown",
                                     int,
                                     fields=[("client_labels", str)])


def WriteGraphSeries(graph_series: rdf_stats.ClientGraphSeries, label: Text):
  """Writes graph series for a particularb client label to the DB.

  Args:
    graph_series: A series of rdf_stats.Graphs containing aggregated data for a
      particular report-type.
    label: Client label by which data in the graph_series was aggregated.
  """
  data_store.REL_DB.WriteClientGraphSeries(graph_series, label)


def WriteGraphSeriesToStatsCollector(graph_series: rdf_stats.ClientGraphSeries,
                                     label: Text,
                                     report_type: rdf_structs.EnumNamedValue):
  """Writes graph series for a particular client label to the Stats Collector.

  Args:
    graph_series: A series of rdf_stats.Graphs containing aggregated data for a
      particular report-type.
    label: Client label by which data in the graph_series was aggregated.
    report_type: rdf_stats.ClientGraphSeries.ReportType for the client stats.
  """
  # util.precondition.AssertType(graph_series, rdf_stats.ClientGraphSeries)
  metric_to_update = None
  if report_type == rdf_stats.ClientGraphSeries.ReportType.UNKNOWN:
    raise ValueError("Report-type for graph series must be set.")
  elif report_type == rdf_stats.ClientGraphSeries.ReportType.OS_RELEASE:
    metric_to_update = OS_RELEASE_BREAKDOWN
  elif report_type == rdf_stats.ClientGraphSeries.ReportType.OS_TYPE:
    metric_to_update = OS_TYPE_BREAKDOWN
  elif report_type == rdf_stats.ClientGraphSeries.ReportType.GRR_VERSION:
    metric_to_update = GRR_VERSION_BREAKDOWN
  for graph in graph_series.graphs:
    for sample in graph:
      metric_to_update.SetValue(value=sample.y_value, fields=[sample.label])


def FetchAllGraphSeries(
    label: Text,
    report_type: rdf_structs.EnumNamedValue,
    period: Optional[rdfvalue.Duration] = None,
) -> Dict[rdfvalue.RDFDatetime, rdf_stats.ClientGraphSeries]:
  """Fetches graph series for the given label and report-type from the DB.

  Args:
    label: Client label to fetch data for.
    report_type: rdf_stats.ClientGraphSeries.ReportType to fetch data for.
    period: rdfvalue.Duration specifying how far back in time to fetch
      data. If not provided, all data for the given label and report-type will
      be returned.

  Returns:
    A dict mapping timestamps to graph-series. The timestamps
    represent when the graph-series were written to the datastore.
  """
  if period is None:
    time_range = None
  else:
    range_end = rdfvalue.RDFDatetime.Now()
    time_range = time_utils.TimeRange(range_end - period, range_end)
  return data_store.REL_DB.ReadAllClientGraphSeries(
      label, report_type, time_range=time_range)


def FetchMostRecentGraphSeries(label: Text,
                               report_type: rdf_structs.EnumNamedValue,
                              ) -> Optional[rdf_stats.ClientGraphSeries]:
  """Fetches the latest graph series for a client label from the DB.

  Args:
    label: Client label to fetch data for.
    report_type: rdf_stats.ClientGraphSeries.ReportType to fetch data for.

  Returns:
    The graph series for the given label and report type that was last
    written to the DB, or None if no series for that label and report-type
    exist.
  """
  return data_store.REL_DB.ReadMostRecentClientGraphSeries(label, report_type)
