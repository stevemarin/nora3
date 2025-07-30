import argparse
import json
import os
import pathlib
import platform
import subprocess
import tempfile

from nora3 import lex, parse

parser = argparse.ArgumentParser(
    prog="Nora3 Compiler",
    description="C-compliler based on Nora Sandler's book",
)

parser.add_argument("filename")
parser.add_argument(
    "--stop-after",
    action="store",
    default="test",
    choices=["lex", "parse", "resolve", "tacky", "asm", "codegen", "assemble", "run", "test"],
)

args = parser.parse_args()

assert isinstance(args.filename, str)
client: str | None
assembly_provided = False
if args.filename.endswith("_client.c"):
    exit(0)
elif args.filename.endswith("tests/chapter_9/valid/stack_arguments/stack_alignment.c"):
    assert platform.system() == "Linux", "only runs on Linux"
    client = os.path.join(os.path.dirname(args.filename), "stack_alignment_check_linux.s")
    assembly_provided = True
elif args.filename.endswith("tests/chapter_10/valid/push_arg_on_page_boundary.c"):
    assert platform.system() == "Linux", "only runs on Linux"
    client = os.path.join(os.path.dirname(args.filename), "data_on_page_boundary_linux.s")
    assembly_provided = True
else:
    client = args.filename.replace(".c", "_client.c")
    if client is None or not pathlib.Path(client).exists():
        client = None

print("RUNNING:", args.filename)

with open(args.filename, "r") as fh:
    src = fh.read()

tokens = lex.Lexer(src).lex()
if args.stop_after == "lex":
    exit(0)

ast = parse.Parser(tokens).parse()
if args.stop_after == "parse":
    exit(0)

ast = ast.resolve()
if args.stop_after == "resolve":
    exit(0)

ir = ast.to_tacky()
if args.stop_after == "tacky":
    exit(0)

assembly = ir.to_asm()
assembly.replace_pseudo(0, {})
assembly = assembly.fix_instructions()

if args.stop_after == "asm":
    exit(0)

code = assembly.codegen()
if args.stop_after == "codegen":
    exit(0)

with tempfile.NamedTemporaryFile(
    mode="+w",
    encoding="ascii",
    delete=False,
    delete_on_close=False,
    suffix=".S",
) as tmp_S:
    s_filename = tmp_S.name
    out_filename = s_filename.replace(".S", ".out")
    tmp_S.write(code)

if client is None:
    subprocess.run(["gcc", "-o", out_filename, s_filename])
elif assembly_provided:
    object_filename = client.replace(".s", ".o")
    subprocess.run(["gcc", "-fPIE", "-c", "-o", object_filename, client])
    subprocess.run(["gcc", "-fPIE", "-o", out_filename, s_filename, object_filename])
    os.unlink(object_filename)
else:
    object_filename = s_filename.replace(".S", ".o")
    subprocess.run(["gcc", "-fPIE", "-c", "-o", object_filename, s_filename])
    subprocess.run(["gcc", "-fPIE", "-o", out_filename, client, object_filename])


if args.stop_after == "assemble":
    exit(0)

output = subprocess.run(out_filename, capture_output=True)
if args.stop_after == "run":
    exit(0)

with open("./expected_results.json", "r") as fh:
    expected = json.load(fh)

path = str(pathlib.Path(args.filename).relative_to("tests"))
result = expected[path]["return_code"]
if result == output.returncode:
    print(f"✔️ {args.filename}")
    exit(0)
else:
    print(f"❌ {args.filename} --- expected {result} got {output.returncode}")
    exit(1)
