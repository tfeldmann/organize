from organize.rule import Folder, FolderWalker

tests = Folder(
    "./tests", "**", exclude_dirs=["*__*"], exclude_files=["__init__.py"],
)
src = Folder(
    "/organize", "**", base_fs="zip://testzip.zip", exclude_dirs=["__pycache__"]
)

x = Folder("~/Documents")
walker = FolderWalker([tests, src, x])

count = 0
for f in walker.files():
    print(f)
    count += 1
print(count)
