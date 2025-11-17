.PHONY: isort black clean_imports reformat

isort:
	isort .

black:
	black .

clean_imports:
	autoflake .

reformat: clean_imports isort black