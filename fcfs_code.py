def fcfs_disk_schedule(requests, head):
    seek_sequence = []
    seek_time = 0
    current = head

    for req in requests:
        seek_sequence.append(req)
        seek_time += abs(current - req)
        current = req

    return seek_sequence, seek_time
