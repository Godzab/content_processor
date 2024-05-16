.PHONY: install install-linux install-macos install-windows

install: install-linux install-macos install-windows

install-linux:
    python3 -m pip install --user .

install-macos:
    python3 -m pip install --user .

install-windows:
    python -m pip install --user .