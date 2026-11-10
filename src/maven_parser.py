"""Загрузка и разбор Maven POM-файлов."""
import os
import re
import xml.etree.ElementTree as ET

import requests

MAVEN_NAMESPACE = "http://maven.apache.org/POM/4.0.0"
SKIPPED_SCOPES = {"test", "system"}


class MavenParserError(Exception):
    """Ошибка загрузки или разбора POM."""


class MavenParser:
    """Получает прямые зависимости пакета из POM-файла."""

    def __init__(self, repo_url: str, test_mode: bool = False):
        self.repo_url = repo_url.rstrip("/")
        self.test_mode = test_mode
        if test_mode and repo_url.startswith(("http://", "https://")):
            raise MavenParserError(
                "В test_mode repo_url должен быть локальным каталогом")

    def fetch_dependencies(
        self, group_id: str, artifact_id: str, version: str
    ) -> list[str]:
        """Возвращает список координат прямых зависимостей."""
        xml_bytes = self._load_pom(group_id, artifact_id, version)
        return self.parse_dependencies(xml_bytes)

    def _load_pom(
        self, group_id: str, artifact_id: str, version: str
    ) -> bytes:
        """Загружает POM из сети или локального каталога."""
        if self.test_mode:
            return self._read_local_pom(group_id, artifact_id, version)
        return self._download_pom(group_id, artifact_id, version)

    def _download_pom(
        self, group_id: str, artifact_id: str, version: str
    ) -> bytes:
        """Скачивает POM из Maven-репозитория."""
        group_path = group_id.replace(".", "/")
        url = (
            f"{self.repo_url}/{group_path}/{artifact_id}/{version}/"
            f"{artifact_id}-{version}.pom"
        )
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise MavenParserError(f"Не удалось загрузить {url}: {exc}")
        return response.content

    def _read_local_pom(
        self, group_id: str, artifact_id: str, version: str
    ) -> bytes:
        """Читает POM из локального репозитория."""
        group_path = group_id.replace(".", "/")
        path = os.path.join(
            self.repo_url, group_path, artifact_id, version,
            f"{artifact_id}-{version}.pom"
        )
        if not os.path.isfile(path):
            raise MavenParserError(f"POM не найден: {path}")
        with open(path, "rb") as stream:
            return stream.read()

    def parse_dependencies(self, xml_bytes: bytes) -> list[str]:
        """Извлекает compile- и runtime-зависимости из POM."""
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as exc:
            raise MavenParserError(f"Некорректный XML POM: {exc}") from exc

        properties = self._collect_properties(root)
        dependencies = root.findall(
            f"{{{MAVEN_NAMESPACE}}}dependencies/"
            f"{{{MAVEN_NAMESPACE}}}dependency"
        )
        return [
            coordinate for coordinate in (
                self._dependency_coordinate(item, properties)
                for item in dependencies
            )
            if coordinate is not None
        ]

    def _collect_properties(self, root: ET.Element) -> dict[str, str]:
        """Собирает свойства POM для подстановки версий."""
        properties = {}
        node = root.find(f"{{{MAVEN_NAMESPACE}}}properties")
        if node is not None:
            for child in node:
                tag = self._local_name(child.tag)
                properties[tag] = (child.text or "").strip()
        return properties

    def _dependency_coordinate(
        self, dependency: ET.Element, properties: dict[str, str]
    ) -> str | None:
        """Формирует координату зависимости или возвращает None."""
        group = self._text(dependency, "groupId")
        artifact = self._text(dependency, "artifactId")
        if not group or not artifact:
            return None

        scope = self._text(dependency, "scope") or "compile"
        if scope in SKIPPED_SCOPES:
            return None

        version = self._text(dependency, "version")
        if version:
            version = self._resolve_property(version, properties)
        if not version:
            return None

        return f"{group}:{artifact}:{version}"

    def _resolve_property(
        self, value: str, properties: dict[str, str]
    ) -> str:
        """Подставляет значения Maven-свойств."""
        match = re.fullmatch(r"\$\{([^}]+)\}", value.strip())
        if not match:
            return value
        return properties.get(match.group(1), "")

    def _text(self, parent: ET.Element, tag: str) -> str:
        """Возвращает текст дочернего элемента без namespace."""
        node = parent.find(f"{{{MAVEN_NAMESPACE}}}{tag}")
        return (node.text or "").strip() if node is not None else ""

    def _local_name(self, tag: str) -> str:
        """Убирает namespace из имени XML-тега."""
        return tag.split("}")[-1]
