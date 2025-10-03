from mechanic.guards import is_path_allowed, count_changed_lines, validate_patch


def test_is_path_allowed_basic():
    assert is_path_allowed("src/foo.py")
    assert is_path_allowed("tests/test_x.py")
    assert is_path_allowed("fixtures/demo/file.txt")
    assert not is_path_allowed("other/file.py")


def test_validate_patch_small_diff_ok():
    diff = """
diff --git a/src/a.py b/src/a.py
index 83db48f..bf12d24 100644
--- a/src/a.py
+++ b/src/a.py
@@ -1,3 +1,3 @@
-x = 1
+x = 2
 y = 3
 z = 4
""".strip()
    ok, reasons = validate_patch(diff)
    assert ok, reasons
    assert count_changed_lines(diff) == 2  # one + and one -


def test_validate_patch_disallowed_path_and_too_large():
    # Build a too-large diff affecting a disallowed path
    changes = "\n".join(["+line" for _ in range(205)])
    diff = f"""
diff --git a/hack.txt b/hack.txt
index 1111111..2222222 100644
--- a/hack.txt
+++ b/hack.txt
@@ -1,2 +1,205 @@
{changes}
""".strip()
    ok, reasons = validate_patch(diff)
    assert not ok
    assert any("paths not allowed" in r for r in reasons)
    assert any("exceeds max" in r for r in reasons)

