from pathlib import Path

def is_dicom_file(path: Path):
    if not path.is_file() or not path.exists():
        return False

    with open(path, "rb") as file:
        file.seek(128)
        magic = file.read(4)
        return magic == b'DICM'

def to_path_array(files):
    try:
        if isinstance(files, str):
            return [Path(files)]

        if isinstance(files, Path):
            return [files]

        iter(files)

        if len(files) > 0:
            if isinstance(files[0], Path):
                return files

            if isinstance(files[0], str):
                return [Path(f) for f in files]

        return []
    except TypeError:
        raise TypeError("Excepting str, pathlib.Path, [str] or [pathlib.Path]")

def get_filelist_from_path_array(files):
    out_files = []
    for item in files:
        if item.is_dir():
            p = item.glob('**/*')
            cur_files = [x for x in p if x.is_file()]
            out_files.extend(cur_files)
        else:
            out_files.append(item)
    return out_files