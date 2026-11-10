import pytest

from src.maven_parser import MavenParser, MavenParserError

POM = b"""<?xml version='1.0' encoding='UTF-8'?>
<project xmlns='http://maven.apache.org/POM/4.0.0'>
  <properties><commons.version>1.0</commons.version></properties>
  <dependencies>
    <dependency>
      <groupId>X</groupId><artifactId>Y</artifactId>
      <version>${commons.version}</version>
    </dependency>
    <dependency>
      <groupId>Z</groupId><artifactId>W</artifactId>
      <version>2.0</version><scope>test</scope>
    </dependency>
  </dependencies>
</project>
"""


def test_parse_namespace_and_properties():
    parser = MavenParser("./test_repo", test_mode=True)
    assert parser.parse_dependencies(POM) == ["X:Y:1.0"]


def test_test_mode_rejects_http():
    with pytest.raises(MavenParserError):
        MavenParser("https://repo1.maven.org/maven2/", test_mode=True)
