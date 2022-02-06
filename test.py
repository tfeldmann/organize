import fs

with fs.open_fs("mem://") as mem:
    mem.touch("Old-name.txt")
    mem.move("Old-name.txt", "New-name.txt")
    mem.tree()
