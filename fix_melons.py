import os

path = "inputs/matches/"
match_file_list = os.scandir(path)
text_to_search = "Salt&amp;VinegarCripps"
replacement_text = "Salt&VinegarCripps"

# for match in match_file_list:
#     with fileinput.FileInput(match.name, backup='.bak') as file:
#         for line in file:
#             print(line.replace(text_to_search, replacement_text), end='')


for dname, dirs, files in os.walk(path):
    # print(files)
    # print("{} {} {}".format(dname, dirs, files))
    for fname in files:
        print(fname)
        fpath = os.path.join(dname, fname)
        with open(fpath) as f:
            s = f.read()
        s = s.replace("Salt&amp;VinegarCripps", replacement_text)
        with open(fpath, "w") as f:
            f.write(s)
