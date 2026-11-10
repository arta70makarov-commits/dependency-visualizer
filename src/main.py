"""Точка входа визуализатора зависимостей Maven."""
from src.config import ConfigError, load_config, print_config
from src.graph import DependencyGraph
from src.maven_parser import MavenParser, MavenParserError
from src.visualizer import MermaidVisualizer

CONFIG_PATH = "config.yaml"
OUTPUT_PATH = "graph.mmd"


def main() -> int:
    """Выполняет полный цикл анализа и генерации диаграммы."""
    try:
        config = load_config(CONFIG_PATH)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}")
        return 1

    print_config(config)
    root = f"{config.package_name}:{config.version}"

    try:
        parser = MavenParser(config.repo_url, config.test_mode)
    except MavenParserError as exc:
        print(f"Ошибка: {exc}")
        return 1

    graph = DependencyGraph(parser)
    graph.build(root, config.max_depth)
    _print_results(graph, root)

    mermaid = MermaidVisualizer(graph.graph).generate()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as stream:
        stream.write(mermaid)

    print(f"\nДиаграмма сохранена в {OUTPUT_PATH}")
    return 0


def _print_results(graph: DependencyGraph, root: str) -> None:
    """Выводит прямые, обратные зависимости и предупреждения."""
    print("\n--- Прямые зависимости корня ---")
    for dependency in graph.graph.get(root, []):
        print(f" - {dependency}")

    print("\n--- Обратные зависимости ---")
    reverse = graph.reverse_dependencies(root)
    if reverse:
        for package in reverse:
            print(f" - {package}")
    else:
        print(" Обратных зависимостей не найдено.")

    if graph.warnings:
        print("\n--- Предупреждения ---")
        for warning in graph.warnings:
            print(f" - {warning}")


if __name__ == "__main__":
    raise SystemExit(main())
