.PHONY: all
all: out/sprite.png out/audio.bin

out/sprite.png: sprite.png $(RULE_DEP) asset.py
	@python3 asset.py render "$(RULE_DEP)"

out/audio.bin: audio.bin
	@mkdir -p out
	@cp audio.bin out/audio.bin
	@echo 'BUILD audio'
