from src.visualizer import MermaidVisualizer


def test_mermaid_unique_node_ids():
    graph = {"A:B:1.0": ["C:D:2.0"], "A:B_1.0": []}
    result = MermaidVisualizer(graph).generate()
    assert "pkg_0_A_B_1_0 --> pkg_1_C_D_2_0" in result
    assert result.count("pkg_0_") == 1
