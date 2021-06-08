import os
from agents import download, ZLAGENT, gen_md5
from settings import DOWNLOAD_URL, BASE_DIR

zlagent_owl = os.path.join(BASE_DIR, 'resources', 'zlagent.owl')
zlagent_py = os.path.join(BASE_DIR, 'resources', 'zlagent.py')
a = gen_md5(zlagent_owl)
print(a)
b = gen_md5(zlagent_py)
print(b)
