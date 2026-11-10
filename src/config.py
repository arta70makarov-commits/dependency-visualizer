"""Загрузка и валидация YAML-конфигурации."""
from dataclasses import dataclass
import os
import sys

import yaml


@dataclass
class Config:
    """Параметры запуска визуализатора."""

    package_name: str
    repo_url: str
    test_mode: bool
    version: str
    max_depth: int


def load_config(filepath: str) -> Config:
    """Загружает конфигурацию и проверяет обязательные поля."""
    if not os.path.isfile(filepath):
        raise ConfigError(f"Файл конфигурации не найден: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Некорректный YAML: {exc}") from exc

    _check_required(data)
    _check_types(data)

    return Config(
        package_name=str(data["package_name"]).strip(),
        repo_url=str(data["repo_url"]).strip(),
        test_mode=bool(data["test_mode"]),
        version=str(data["version"]).strip(),
        max_depth=int(data["max_depth"]),
    )


def _check_required(data: dict) -> None:
    """Проверяет наличие обязательных параметров."""
    required = (
        "package_name", "repo_url", "test_mode", "version", "max_depth"
    )
    missing = [key for key in required if key not in data]
    if missing:
        raise ConfigError(f"Отсутствуют параметры: {', '.join(missing)}")


def _check_types(data: dict) -> None:
    """Проверяет типы и допустимые значения параметров."""
    if not isinstance(data["test_mode"], bool):
        raise ConfigError("test_mode должен быть true или false")
    depth = data["max_depth"]
    if not isinstance(depth, int) or depth < 1:
        raise ConfigError("max_depth должен быть целым числом больше 0")
    if ":" not in str(data["package_name"]):
        raise ConfigError(
            "package_name должен иметь формат groupId:artifactId")


def print_config(config: Config) -> None:
    """Выводит параметры конфигурации."""
    print("--- Параметры конфигурации ---")
    print(f"package_name: {config.package_name}")
    print(f"repo_url: {config.repo_url}")
    print(f"test_mode: {config.test_mode}")
    print(f"version: {config.version}")
    print(f"max_depth: {config.max_depth}")
    print("------------------------------")


class ConfigError(Exception):
    """Ошибка конфигурации."""
