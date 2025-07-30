
ALL := valid invalid

.PHONY: all
all: $(ALL) ;

.PHONY: valid
valid:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after test {}

.PHONY: invalid
invalid:
	pytest tests

.PHONY: valid-lex
valid-lex:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after lex {}

.PHONY: valid-parse
valid-parse:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after parse {}

.PHONY: valid-resolve
valid-resolve:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after resolve {}

.PHONY: valid-tacky
valid-tacky:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after tacky {}

.PHONY: valid-asm
valid-asm:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after asm {}

.PHONY: valid-codegen
valid-codegen:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after codegen {}

.PHONY: valid-run
valid-run:
	@find tests -wholename "*/valid/*.c" -print0 | sort -zn | xargs --null -I {} python -m nora3 --stop-after run {}


 