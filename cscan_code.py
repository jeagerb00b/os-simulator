def cscan_disk_scheduling(requests, head, disk_size):
    requests.sort()
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]

    seek_sequence = []
    seek_time = 0
    current = head

    for r in right:
        seek_sequence.append(r)
        seek_time += abs(current - r)
        current = r

    if left:
        seek_time += abs(current - (disk_size - 1))  # go to end
        seek_time += disk_size - 1  # jump to start
        current = 0

        for r in left:
            seek_sequence.append(r)
            seek_time += abs(current - r)
            current = r

    return seek_sequence, seek_time