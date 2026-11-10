import pytest

from src.graph import DependencyGraph
from src.maven_parser import MavenParser


class MockParser(MavenParser):
    def __init__(self):
        super().__init__("./test_repo", test_mode=True)

    def fetch_dependencies(self, group_id, artifact_id, version):
        if artifact_id == "A":
            return ["X:Y:1.0", "Z:W:2.0"]
        if artifact_id == "Y":
            return ["Z:W:2.0"]
        return []


def test_bfs_builds_transitive_graph():
    graph = DependencyGraph(MockParser())
    graph.build("G:A:1.0", max_depth=3)

    assert graph.graph["G:A:1.0"] == ["X:Y:1.0", "Z:W:2.0"]
    assert graph.graph["X:Y:1.0"] == ["Z:W:2.0"]
    assert graph.graph["Z:W:2.0"] == []


def test_reverse_dependencies_exact_match():
    graph = DependencyGraph(MockParser())
    graph.build("G:A:1.0", max_depth=3)

    assert graph.reverse_dependencies("Z:W:2.0") == [
        "G:A:1.0", "X:Y:1.0"
    ]


def test_invalid_root_coordinate():
    graph = DependencyGraph(MockParser())
    with pytest.raises(ValueError):
        graph.build("invalid", max_depth=1)
