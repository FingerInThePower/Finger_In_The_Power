CFLAGS += -g -Wall -O0 -lm -lpthread -Wno-maybe-uninitialized
WASM = wat2wasm

WAT_DIR := ./wasm
SRC_DIR := ./native
OBJ_DIR := ./build
WAT_FILES := $(wildcard $(WAT_DIR)/*.wat)
OBJ_FILES := $(patsubst $(WAT_DIR)/%.wat,$(OBJ_DIR)/%.wasm,$(WAT_FILES))


all: pow_fp

$(OBJ_DIR)/%.wasm: $(WAT_DIR)/%.wat
	$(WASM) -o $@ $< --enable-threads

pow_fp: $(OBJ_FILES)



clean:
	rm build/*
