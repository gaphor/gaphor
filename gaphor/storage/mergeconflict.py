import io
import tempfile


def split(fd: io.IOBase, file_type=tempfile.TemporaryFile):
    CURRENT = 1
    INCOMING = 2
    BOTH = CURRENT | INCOMING
    current = file_type()
    incoming = file_type()
    state = BOTH
    found_merge_conflict = False
    for line in fd.readlines():
        if state == BOTH and line.startswith(b"<<<<<<<"):
            state = CURRENT
            found_merge_conflict = True
        elif state == CURRENT and line.startswith(b"======="):
            state = INCOMING
        elif state == INCOMING and line.startswith(b">>>>>>>"):
            state = BOTH
        else:
            if state & CURRENT:
                current.write(line)
            if state & INCOMING:
                incoming.write(line)

    current.seek(0)
    incoming.seek(0)
    if found_merge_conflict:
        return current, incoming
    else:
        incoming.close()
        return current, None
