import typing
import collections


def topological_sort(graph: typing.Dict[str, typing.List[str]]) -> typing.List[str]:
    """toplogical sort
    
    Args:
        graph: DAG
            {
                "node_name_1": [predecessor_0, predecessor_1, ...],
                "node_name_2": [predecessor_0, predecessor_1, ...],
                ...
            }
    
    Examples:
        graph = {
            "ClassA": ["ClassD"],
            "ClassB": ["ClassA"],
            "ClassC": ["ClassA"],
            "ClassD": [],
            "ClassE": ["ClassB", "ClassC"],
            "ClassF": ["ClassA"],
        }
        sorted = topological_sort(graph)
    """
    node_map: dict = {}
    for _node_name, _predecessors in graph.items():
        node_map[_node_name] = {
            "name": _node_name,
            "indegree": len(_predecessors),
            "next_node_names": []
        }
    for _node_name, _predecessors in graph.items():
        for _predecessor in _predecessors:
            if _node_name not in node_map[_predecessor]['next_node_names']:
                node_map[_predecessor]['next_node_names'].append(_node_name)

    queue: typing.Deque = collections.deque()
    for node in node_map.values():
        if node['indegree'] == 0:
            queue.append(node)

    sorted_node_names = []
    while len(queue) > 0:
        node = queue.popleft()
        sorted_node_names.append(node['name'])
        for next_node_name in node['next_node_names']:
            next_node = node_map[next_node_name]
            next_node['indegree'] = next_node['indegree'] - 1
            if next_node['indegree'] == 0:
                queue.append(next_node)

    if len(sorted_node_names) != len(node_map):
        raise ValueError(f"Cycles detected: {str(graph)}")

    return sorted_node_names
