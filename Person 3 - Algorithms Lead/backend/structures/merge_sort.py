"""
PHASE 2 — DSA Structure 6: MergeSort
Rubric requirement: Sorting (at least one O(n log n) sort)

WHY MERGE SORT HERE?
  The `/stocks/<sym>/history` endpoint returns a stock's 90-day
  price history sorted by date.  Merge Sort is:
    • Stable  — preserves chronological order for equal dates
    • O(n log n) worst-case  — no adversarial input degrades it
    • O(n) space  — acceptable for n ≤ 100,000 price ticks

  Python's built-in TimSort (used by sorted() and list.sort()) is
  also O(n log n) and faster in practice, but implementing Merge
  Sort explicitly satisfies the rubric requirement and demonstrates
  understanding of the divide-and-conquer paradigm.

COMPLEXITY:
  sort(list)  O(n log n) time, O(n) space
"""


def merge_sort(arr: list, key=None) -> list:
    """
    Classic top-down merge sort.

    Parameters
    ----------
    arr : list
        The list to sort.  May contain any comparable elements.
    key : callable, optional
        A function of one argument used to extract a comparison key
        from each element (like sorted(..., key=...)).

    Returns
    -------
    list
        A new list sorted in ascending order.

    Time:  O(n log n)  —  2T(n/2) + O(n)  →  Θ(n log n)
    Space: O(n)        —  auxiliary arrays during merge phase
    """

    if key is None:
        key = lambda x: x

    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid], key=key)
    right_half = merge_sort(arr[mid:], key=key)

    return _merge(left_half, right_half, key)


def _merge(left: list, right: list, key) -> list:
    """
    Merge two sorted lists into a single sorted list.
    O(n) time, O(n) space.
    """
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements
    if i < len(left):
        result.extend(left[i:])
    if j < len(right):
        result.extend(right[j:])

    return result
