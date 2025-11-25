"""
Utility functions for PyOptimal.
"""

from typing import List, Set, Any


def is_acyclic(edges: List[tuple]) -> bool:
    """Check if a directed graph represented by edges is acyclic."""
    from collections import defaultdict, deque
    
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set()
    
    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1
        nodes.add(src)
        nodes.add(dst)
    
    queue = deque([n for n in nodes if in_degree[n] == 0])
    count = 0
    
    while queue:
        node = queue.popleft()
        count += 1
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return count == len(nodes)


def topological_sort(edges: List[tuple]) -> List[Any]:
    """Perform topological sort on a directed acyclic graph."""
    from collections import defaultdict, deque
    
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set()
    
    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1
        nodes.add(src)
        nodes.add(dst)
    
    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == len(nodes) else []
