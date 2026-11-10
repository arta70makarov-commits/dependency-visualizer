.PHONY: build run test clean

build:
	python -m pip install -r requirements.txt

run:
	python -m src.main

test:
	python -m pytest tests -v

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
