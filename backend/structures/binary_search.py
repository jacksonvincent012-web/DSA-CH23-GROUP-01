"""
PHASE 2 — DSA Structure 7: BinarySearch
Rubric requirement: Searching (at least one searching strategy)

WHY BINARY SEARCH HERE?
  After a stock's price history is sorted by Merge Sort, the client
  often wants to find "the price on a specific date" or "all prices
  between $150 and $160".  Binary Search on the sorted array finds
  the insertion point in O(log n), giving us the start and end
  indices for a range query in just 2 × O(log n) comparisons.

  For n = 100,000 this is ~17 comparisons per search, versus 100,000
  for a linear scan.

COMPLEXITY:
  search(sorted_arr, target)  O(log n) time, O(1) space
  range_search(sorted_arr, low, high)  O(log n) time
"""

from typing import Any


def binary_search(arr: list, target: Any, key=None) -> int:
    """
    Standard binary search on a SORTED list.

    Parameters
    ----------
    arr : list
        Sorted list to search.
    target : Any
        Value to find.
    key : callable, optional
        Extract comparison key from each element.

    Returns
    -------
    int
        Index of the target if found, otherwise -1.

    Time: O(log n)
    Space: O(1)
    """
    if key is None:
        key = lambda x: x

    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = key(arr[mid])
        if mid_val == target:
            return mid
        elif mid_val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(arr: list, target: Any, key=None) -> int:
    """
    Find the leftmost index where the value >= target.
    (First index to insert target while keeping sort order.)

    Parameters
    ----------
    arr : list
        Sorted list.
    target : Any
        Threshold value.
    key : callable, optional
        Extract comparison key.

    Returns
    -------
    int
        Leftmost insertion index.

    Time: O(log n)
    """
    if key is None:
        key = lambda x: x

    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(arr[mid]) < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(arr: list, target: Any, key=None) -> int:
    """
    Find the leftmost index where the value > target.
    (One past the last occurrence of target.)

    Time: O(log n)
    """
    if key is None:
        key = lambda x: x

    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(arr[mid]) <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def range_search(arr: list, low: Any, high: Any, key=None) -> list:
    """
    Return all elements in the sorted list whose key is in [low, high].

    Time: O(log n + k) where k is the number of matching elements.
    """
    if key is None:
        key = lambda x: x

    left = lower_bound(arr, low, key=key)
    right = upper_bound(arr, high, key=key)
    return arr[left:right]
