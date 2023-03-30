import os
import errno
import io
import struct
import shutil
import fileinput
import json


def round_up(i, m):
    return (i + m - 1) & ~(m - 1)


class Asar:
    def __init__(self, path, fp, header, base_offset):
        self.path = path
        self.fp = fp
        self.header = header
        self.base_offset = base_offset

    @classmethod
    def open(cls, path):
        fp = open(path, 'rb')
        data_size, header_size, header_object_size, header_string_size = struct.unpack('<4I', fp.read(16))
        header_json = fp.read(header_string_size).decode('utf-8')
        return cls(
            path=path,
            fp=fp,
            header=json.loads(header_json),
            base_offset=round_up(16 + header_string_size, 4)
        )

    @classmethod
    def compress(cls, path):
        offset = 0
        paths = []

        def _path_to_dict(path):
            nonlocal offset, paths
            result = {'files': {}}
            for f in os.scandir(path):
                if os.path.isdir(f.path):
                    result['files'][f.name] = _path_to_dict(f.path)
                elif f.is_symlink():
                    result['files'][f.name] = {
                        'link': os.path.realpath(f.name)
                    }
                else:
                    paths.append(f.path)
                    size = f.stat().st_size
                    result['files'][f.name] = {
                        'size': size,
                        'offset': str(offset)
                    }
                    offset += size
            return result

        def _paths_to_bytes(paths):
            _bytes = io.BytesIO()
            with fileinput.FileInput(files=paths, mode="rb") as f:
                for i in f:
                    _bytes.write(i)
            return _bytes.getvalue()

        header = _path_to_dict(path)
        header_json = json.dumps(header, sort_keys=True, separators=(',', ':')).encode('utf-8')
        header_string_size = len(header_json)
        data_size = 4
        aligned_size = round_up(header_string_size, data_size)
        header_size = aligned_size + 8
        header_object_size = aligned_size + data_size
        diff = aligned_size - header_string_size
        header_json = header_json + b'\0' * diff if diff else header_json
        fp = io.BytesIO()
        fp.write(struct.pack('<4I', data_size, header_size, header_object_size, header_string_size))
        fp.write(header_json)
        fp.write(_paths_to_bytes(paths))

        return cls(
            path=path,
            fp=fp,
            header=header,
            base_offset=round_up(16 + header_string_size, 4))

    def _copy_unpacked_file(self, source, destination):
        unpacked_dir = self.path + '.unpacked'
        if not os.path.isdir(unpacked_dir):
            print("Couldn't copy file {}, no extracted directory".format(source))
            return

        src = os.path.join(unpacked_dir, source)
        if not os.path.exists(src):
            print("Couldn't copy file {}, doesn't exist".format(src))
            return

        dest = os.path.join(destination, source)
        shutil.copyfile(src, dest)

    def _extract_file(self, source, info, destination):
        if 'offset' not in info:
            self._copy_unpacked_file(source, destination)
            return

        self.fp.seek(self.base_offset + int(info['offset']))
        r = self.fp.read(int(info['size']))

        dest = os.path.join(destination, source)
        with open(dest, 'wb') as f:
            f.write(r)

    def _extract_link(self, source, link, destination):
        dest_filename = os.path.normpath(os.path.join(destination, source))
        link_src_path = os.path.dirname(os.path.join(destination, link))
        link_to = os.path.join(link_src_path, os.path.basename(link))

        try:
            os.symlink(link_to, dest_filename)
        except OSError as e:
            if e.errno == errno.EXIST:
                os.unlink(dest_filename)
                os.symlink(link_to, dest_filename)
            else:
                raise e

    def _extract_directory(self, source, files, destination):
        dest = os.path.normpath(os.path.join(destination, source))

        if not os.path.exists(dest):
            os.makedirs(dest)
        
        for i,(name, info) in enumerate( files.items()):
            
            item_path = os.path.join(source, name)

            if 'files' in info:
                self._extract_directory(item_path, info['files'], destination)
            elif 'link' in info:
                self._extract_link(item_path, info['link'], destination)
            else:
                self._extract_file(item_path, info, destination)
            
    def extract(self, path):
        self._extract_directory('.', self.header['files'], path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()


def extract_asar(source, dest):
    with Asar.open(source) as a:
        a.extract(dest)

if __name__=='__main__':
    extract_asar("app.asar", "app")  