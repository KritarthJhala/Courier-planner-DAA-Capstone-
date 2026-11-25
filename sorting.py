"""Phase 2a - Parcel prioritisation using Merge Sort (O(n log n), stable).

Parcels are ordered by earliest deadline first; ties are broken by higher
priority. Insertion sort is also provided only for the runtime comparison.
"""


def _default_key(p):
    return (p.deadline, -p.priority)


def merge_sort(items, key=_default_key):
    """Return a new sorted list. Time O(n log n), space O(n)."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        # <= keeps the sort stable (equal keys retain original order)
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def insertion_sort(items, key=_default_key):
    """Baseline O(n^2) sort used only to show why merge sort was chosen."""
    a = list(items)
    for i in range(1, len(a)):
        cur, j = a[i], i - 1
        while j >= 0 and key(a[j]) > key(cur):
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = cur
    return a
