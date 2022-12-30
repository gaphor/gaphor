import io


def split(fd: io.TextIOBase, current: io.TextIOBase, incoming: io.TextIOBase):
    CURRENT = 1
    INCOMING = 2
    BOTH = CURRENT | INCOMING
    state = BOTH
    found_merge_conflict = False
    for line in fd.readlines():
        if state == BOTH and line.startswith("<<<<<<<"):
            state = CURRENT
            found_merge_conflict = True
        elif state == CURRENT and line.startswith("======="):
            state = INCOMING
        elif state == INCOMING and line.startswith(">>>>>>>"):
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
    incoming.close()
    return current, None
