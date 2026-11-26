# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""Interval algebra on sorted, disjoint float64 arrays, measured in microseconds."""

import numpy as np
from numpy.typing import NDArray

IntervalSet = tuple[NDArray[np.float64], NDArray[np.float64]]
TimeValues = NDArray[np.float64] | list[float] | tuple[float, ...]
EMPTY: IntervalSet = (np.zeros(0), np.zeros(0))


def union(starts_us: TimeValues, ends_us: TimeValues) -> IntervalSet:
    """Merge overlapping or adjacent intervals into a sorted, disjoint set."""
    starts_us = np.asarray(starts_us, dtype=np.float64)
    ends_us = np.asarray(ends_us, dtype=np.float64)
    positive_duration = ends_us > starts_us
    starts_us, ends_us = starts_us[positive_duration], ends_us[positive_duration]
    if starts_us.size == 0:
        return EMPTY
    else:
        order = np.argsort(starts_us, kind="mergesort")
        starts_us, ends_us = starts_us[order], ends_us[order]
        running_end_us = np.maximum.accumulate(ends_us)
        new_interval = np.empty(starts_us.size, dtype=bool)
        new_interval[0] = True
        new_interval[1:] = starts_us[1:] > running_end_us[:-1]
        first_indices = np.flatnonzero(new_interval)
        last_indices = np.append(first_indices[1:] - 1, starts_us.size - 1)
        return starts_us[first_indices], running_end_us[last_indices]


def total(intervals_us: IntervalSet) -> float:
    """Return the total duration in microseconds."""
    starts_us, ends_us = intervals_us
    return float(np.sum(ends_us - starts_us))


def clip(intervals_us: IntervalSet, start_us: float, end_us: float) -> IntervalSet:
    starts_us, ends_us = intervals_us
    clipped_starts_us = np.maximum(starts_us, start_us)
    clipped_ends_us = np.minimum(ends_us, end_us)
    positive_duration = clipped_ends_us > clipped_starts_us
    return clipped_starts_us[positive_duration], clipped_ends_us[positive_duration]


def complement(
    intervals_us: IntervalSet, start_us: float, end_us: float
) -> IntervalSet:
    """Return gaps inside the half-open measurement window."""
    starts_us, ends_us = clip(intervals_us, start_us, end_us)
    gap_starts_us = np.concatenate(([start_us], ends_us))
    gap_ends_us = np.concatenate((starts_us, [end_us]))
    positive_duration = gap_ends_us > gap_starts_us
    return gap_starts_us[positive_duration], gap_ends_us[positive_duration]


def intersect(first_us: IntervalSet, second_us: IntervalSet) -> IntervalSet:
    first_starts_us, first_ends_us = first_us
    second_starts_us, second_ends_us = second_us
    if first_starts_us.size == 0 or second_starts_us.size == 0:
        return EMPTY
    else:
        lower_indices = np.searchsorted(second_ends_us, first_starts_us, side="right")
        upper_indices = np.searchsorted(second_starts_us, first_ends_us, side="left")
        overlap_counts = np.maximum(upper_indices - lower_indices, 0)
        first_indices = np.repeat(np.arange(first_starts_us.size), overlap_counts)
        offsets = np.arange(overlap_counts.sum()) - np.repeat(
            np.cumsum(overlap_counts) - overlap_counts, overlap_counts
        )
        second_indices = np.repeat(lower_indices, overlap_counts) + offsets
        starts_us = np.maximum(
            first_starts_us[first_indices], second_starts_us[second_indices]
        )
        ends_us = np.minimum(
            first_ends_us[first_indices], second_ends_us[second_indices]
        )
        positive_duration = ends_us > starts_us
        return starts_us[positive_duration], ends_us[positive_duration]


def subtract(first_us: IntervalSet, second_us: IntervalSet) -> IntervalSet:
    if first_us[0].size == 0:
        return EMPTY
    elif second_us[0].size == 0:
        return first_us
    else:
        start_us = min(first_us[0][0], second_us[0][0])
        end_us = max(first_us[1][-1], second_us[1][-1])
        return intersect(first_us, complement(second_us, start_us, end_us))


def overlap_total(first_us: IntervalSet, second_us: IntervalSet) -> float:
    return total(intersect(first_us, second_us))


def contains_points(
    intervals_us: IntervalSet, timestamps_us: TimeValues
) -> NDArray[np.bool_]:
    """Test timestamps against half-open intervals."""
    starts_us, ends_us = intervals_us
    timestamps_us = np.asarray(timestamps_us, dtype=np.float64)
    if starts_us.size == 0:
        return np.zeros(timestamps_us.shape, dtype=bool)
    else:
        interval_indices = np.searchsorted(starts_us, timestamps_us, side="right") - 1
        valid_indices = interval_indices >= 0
        contained = np.zeros(timestamps_us.shape, dtype=bool)
        contained[valid_indices] = (
            timestamps_us[valid_indices] < ends_us[interval_indices[valid_indices]]
        )
        return contained


def segment_active(
    intervals_us: IntervalSet,
    segment_starts_us: NDArray[np.float64],
    segment_ends_us: NDArray[np.float64],
) -> NDArray[np.bool_]:
    """Test segments that do not straddle any interval boundary."""
    starts_us, ends_us = intervals_us
    if starts_us.size == 0:
        return np.zeros(segment_starts_us.shape, dtype=bool)
    else:
        interval_indices = (
            np.searchsorted(starts_us, segment_starts_us, side="right") - 1
        )
        valid_indices = interval_indices >= 0
        active = np.zeros(segment_starts_us.shape, dtype=bool)
        active[valid_indices] = (
            ends_us[interval_indices[valid_indices]] >= segment_ends_us[valid_indices]
        )
        return active


def elementary(
    boundaries_us: TimeValues, start_us: float, end_us: float
) -> IntervalSet:
    boundaries_us = np.asarray(boundaries_us, dtype=np.float64)
    interior = boundaries_us[(boundaries_us > start_us) & (boundaries_us < end_us)]
    boundaries_us = np.unique(np.concatenate(([start_us], interior, [end_us])))
    return boundaries_us[:-1], boundaries_us[1:]


def runs(
    active_segments: NDArray[np.bool_],
    segment_starts_us: NDArray[np.float64],
    segment_ends_us: NDArray[np.float64],
) -> IntervalSet:
    """Merge consecutive active segments into intervals."""
    if not active_segments.any():
        return EMPTY
    else:
        starts_us = segment_starts_us[active_segments]
        ends_us = segment_ends_us[active_segments]
        new_interval = np.empty(starts_us.size, dtype=bool)
        new_interval[0] = True
        new_interval[1:] = starts_us[1:] > ends_us[:-1]
        first_indices = np.flatnonzero(new_interval)
        last_indices = np.append(first_indices[1:] - 1, starts_us.size - 1)
        return starts_us[first_indices], ends_us[last_indices]
