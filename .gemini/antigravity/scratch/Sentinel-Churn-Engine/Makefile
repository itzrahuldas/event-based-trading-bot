.PHONY: setup

setup:
	@echo "Installing dependencies..."
	pip install -e .

train:
	@echo "Running Training Pipeline..."
	python src/models/train_model.py

app:
	@echo "Launching Dashboard..."
	streamlit run src/dashboard/app.py

test:
	@echo "Running Tests..."
	pytest tests/
