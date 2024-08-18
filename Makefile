SNIPPET_INPUTS := $(shell find codegen/snippet-tests/input/*.pkl)
FIXTURES_INPUTS := $(shell find tests/Fixtures/*.pkl)

PACKAGE_DIR = ./codegen/src
OUTPUT_DIR = output

PROJECT_FILE := $(strip $(PACKAGE_DIR))/PklProject
SUFFIXES := "" .sha256 .zip .zip.sha256

PKL_BIN:=pkl_bin
PKL_LATEST_RELEASE_URL=https://api.github.com/repos/apple/pkl/releases/latest
PKL_DOWNLOAD_URL=$(shell curl -s $(PKL_LATEST_RELEASE_URL) | grep "browser_download_url.*pkl-linux-amd64" | cut -d : -f 2,3 | tr -d \")

NAME = $(shell ./$(PKL_BIN) eval $(PROJECT_FILE) -x package.name)
VERSION = $(shell ./$(PKL_BIN) eval $(PROJECT_FILE) -x package.version)
#TARGETS = $(addprefix $(strip $(OUTPUT_DIR))/$(NAME)@$(VERSION),$(SUFFIXES))

#$(info  PACKAGE_DIR is $(PACKAGE_DIR))
#$(info  PROJECT_FILE is $(PROJECT_FILE))
#$(info  NAME is $(NAME))
#$(info  VERSION is $(VERSION))
#$(info  SIGNATURE is $(SIGNATURE))
#$(info  SUFFIXES is $(SUFFIXES))
#$(info  TARGETS is $(TARGETS))

.PHONY: help
help:
	@echo "Snippet tests:"
	@echo $(SNIPPET_INPUTS) | tr ' ' '\n' | sort

	@echo "Fixtures:"
	@echo $(FIXTURES_INPUTS) | tr ' ' '\n' | sort

pkl_bin:
	@echo "Fetching latest release of pkl..."
	curl -L -o $(PKL_BIN) $(PKL_DOWNLOAD_URL)
	chmod +x $(PKL_BIN)
	./$(PKL_BIN) --version

.PHONY: build
build:
	python -m build

.PHONY: package
package: pkl_bin
	./$(PKL_BIN) project package $(PACKAGE_DIR) --output-path $(OUTPUT_DIR)

$(TARGETS): pkl_package

.PHONY: version
version: pkl_bin
	@./$(PKL_BIN) eval $(PROJECT_FILE) -x package.version

.PHONY: clean
clean:
	rm -f $(PKL_BIN)
	rm -rf $(OUTPUT_DIR)
