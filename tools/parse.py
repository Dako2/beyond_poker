import glob
import os
fns = glob.glob("./face/*.png")
print(fns)
for fn in fns:
    if "3x" in fn or "2x" in fn:
        os.remove(fn)

for fn in fns:
    if "1x" in fn:
        os.rename(fn, fn.replace('@1x',''))

