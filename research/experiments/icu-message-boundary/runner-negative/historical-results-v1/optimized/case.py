from pathlib import Path
Path(__file__).with_name("child-executed.txt").write_text("yes")
raise RuntimeError("CHILD_EXECUTED")
