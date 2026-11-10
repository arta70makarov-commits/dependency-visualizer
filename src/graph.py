"""Построение графа зависимостей методом BFS."""
from collections import deque

from src.maven_parser import MavenParser, MavenParserError


class DependencyGraph:
    """Хранит граф зависимостей и строит его обходом BFS."""

    def __init__(self, parser: MavenParser):
        self.parser = parser
        self.graph: dict[str, list[str]] = {}
        self.warnings: list[str] = []

    def build(self, root: str, max_depth: int) -> None:
        """Строит граф зависимостей без рекурсии."""
        queue = deque([(root, 0)])
        enqueued = {root}

        while queue:
            package, depth = queue.popleft()
            self.graph[package] = []
            if depth >= max_depth:
                continue

            for dependency in self._dependencies_of(package):
                self.graph[package].append(dependency)
                if dependency not in enqueued:
                    enqueued.add(dependency)
                    queue.append((dependency, depth + 1))

    def _dependencies_of(self, package: str) -> list[str]:
        """Получает зависимости одного пакета."""
        group, artifact, version = self._split_coordinate(package)
        try:
            return self.parser.fetch_dependencies(group, artifact, version)
        except MavenParserError as exc:
            self.warnings.append(f"{package}: {exc}")
            return []

    def _split_coordinate(self, package: str) -> tuple[str, str, str]:
        """Разделяет координату на groupId, artifactId и version."""
        parts = package.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Координата должна быть groupId:artifactId:version: {package}"
            )
        return parts[0], parts[1], parts[2]

    def reverse_dependencies(self, target: str) -> list[str]:
        """Возвращает пакеты, которые напрямую зависят от target."""
        return [
            package for package, dependencies in self.graph.items()
            if target in dependencies
        ]
