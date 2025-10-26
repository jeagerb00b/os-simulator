def scan_disk_scheduling(requests, head, disk_size, direction):
    requests.sort()
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    seek_sequence = []
    seek_time = 0
    current = head

    if direction == "left":
        for r in reversed(left):
            seek_sequence.append(r)
            seek_time += abs(current - r)
            current = r
        seek_sequence.append(0)
        seek_time += current
        current = 0
        for r in right:
            seek_sequence.append(r)
            seek_time += abs(current - r)
            current = r
    else:
        for r in right:
            seek_sequence.append(r)
            seek_time += abs(current - r)
            current = r
        
        for r in reversed(left):
            seek_sequence.append(r)
            seek_time += abs(current - r)
            current = r

    return seek_sequence, seek_time