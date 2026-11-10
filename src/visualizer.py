"""Генерация Mermaid-диаграммы по графу зависимостей."""


class MermaidVisualizer:
    """Создаёт Mermaid-диаграмму с уникальными идентификаторами узлов."""

    def __init__(self, graph: dict[str, list[str]]):
        self.graph = graph
        self._ids: dict[str, str] = {}

    def generate(self) -> str:
        """Возвращает текст Mermaid-диаграммы."""
        lines = ["graph TD"]
        for package, dependencies in self.graph.items():
            source = self._node_id(package)
            for dependency in dependencies:
                target = self._node_id(dependency)
                lines.append(f"    {source} --> {target}")
        return "\n".join(lines)

    def _node_id(self, package: str) -> str:
        """Создаёт уникальный безопасный идентификатор узла."""
        if package not in self._ids:
            safe = "".join(
                char if char.isalnum() else "_" for char in package
            )
            self._ids[package] = f"pkg_{len(self._ids)}_{safe}"
        return self._ids[package]
