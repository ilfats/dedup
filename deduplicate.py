import os
import shutil
import filecmp
import argparse


def normalize_string(str):
    return ''.join(x for x in str if x not in ' \t-_()"01234567890').lower()


def file_details(dirname, filename):
    fullname = os.path.join(dirname, filename)
    stat = os.stat(fullname)
    name, ext = os.path.splitext(filename)
    name = normalize_string(name) + ext
    return name, stat.st_size, stat.st_mtime


def group_files(dirname, filenames):
    """
    Groups similar files (similar normalized name and size) and returns a dict, mapping
    a tuple (normalized file name, size) to a list of tuples (file name, modification time)
    """
    groups = {}
    for fname in filenames:
        nname, fsize, ftime = file_details(dirname, fname)
        key = (nname, fsize)
        detail = (fname, ftime)
        if key in groups:
            groups[key].append(detail)
        else:
            groups[key] = [detail]

    return groups


def compare_dirs(dir_contents, dir1, dir2):
    c1 = dir_contents[dir1]
    c2 = dir_contents[dir2]

    if c1 != c2:
        # dir lists or file lists are different
        return False

    equal = True
    for subdir in c1[0]:
        equal = compare_dirs(dir_contents, os.path.join(dir1, subdir), os.path.join(dir2, subdir))
        if not equal:
            break

    return equal


def find_duplicates(path):
    """
    Returns a list of duplicates in a path
    """
    # find groups of files consisting of more than 1 item (suspected duplicates)
    bgroups = []
    dir_contents = {}
    for dirname, dirnames, filenames in os.walk(path):
        groups = group_files(dirname, filenames)
        for group in groups.items():
            if len(group[1]) > 1:
                bgroups.append((dirname, group))
        dir_contents[dirname] = (dirnames, sorted(groups.keys()))

    # check suspected duplicate files
    duplicates = []
    for dirname, group in bgroups:
        files = sorted(group[1], key=lambda p: p[1], reverse=True)
        while len(files) > 1:
            champ = files[0]
            suspects = files[1:]
            f1 = os.path.join(dirname, champ[0])
            unconfirmed = []
            for suspect in suspects:
                f2 = os.path.join(dirname, suspect[0])
                if filecmp.cmp(f1, f2, shallow=False):
                    duplicates.append(f2)
                    print '"{}" is a duplicate of "{}" in "{}"'.format(suspect[0], champ[0], dirname)
                else:
                    unconfirmed.append(suspect)

            files = unconfirmed

    for item in dir_contents.items():
        parent = item[0]
        dirs = item[1][0]
        files = item[1][1]
        for d1 in range(len(dirs)-1):
            for d2 in range(d1+1, len(dirs)):
                dir1 = os.path.join(parent, dirs[d1])
                dir2 = os.path.join(parent, dirs[d2])
                if compare_dirs(dir_contents, dir1, dir2):
                    if os.stat(dir1).st_mtime > os.stat(dir2).st_mtime:
                        master = dirs[d1]
                        dup = dirs[d2]
                        dup_fullpath = dir2
                    else:
                        master = dirs[d2]
                        dup = dirs[d1]
                        dup_fullpath = dir1

                    if dup_fullpath not in duplicates:
                        duplicates.append(dup_fullpath)
                    print 'Directory "{}" is a duplicate of "{}" in "{}"'.format(dup, master, parent)

    return duplicates


def deduplicate(path, remove):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print 'Path does not exist "{}"'.format(path)
        return

    print '---- Processing ', path

    dups = find_duplicates(path)

    if dups:
        print
        if remove:
            for dup in dups:
                print 'Deleting "{}"'.format(dup)
                if os.path.isdir(dup):
                    shutil.rmtree(dup)
                else:
                    os.remove(dup)
        else:
            print 'Not deleting detected duplicates. Use --remove flag to enable auto delete.'


def main():
    parser = argparse.ArgumentParser(description='Find/remove duplicates in downloaded Coursera content')
    parser.add_argument('--remove', dest='remove', action="store_true", default=False,
                        help="remove detected duplicates keeping only the latest version. Use at your own risk!")
    parser.add_argument('path_name', type=str, help='Path to process (e.g., C:\\Coursera)')
    args = parser.parse_args()

    deduplicate(args.path_name, args.remove)


if __name__ == '__main__':
    main()
