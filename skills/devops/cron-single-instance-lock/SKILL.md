---
name: cron-single-instance-lock
description: Prevent duplicate script execution in cron jobs using file lock mechanism
tags: [cron, python, automation, lock, duplicate-prevention]
---

# Cron Single Instance Lock

Prevent duplicate script execution when using cron jobs. Useful when:
- Script might be triggered multiple times
- Manual run overlaps with cron run
- Previous instance hasn't finished yet

## Python Implementation

```python
import fcntl

def main():
    # Lock mechanism - prevent duplicate runs
    lock_file = open('/tmp/script_name.lock', 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("❌ Another instance is already running. Exiting.")
        return 1
    
    # ... your script logic here ...
    
    # Release lock before exit
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

## How It Works

1. `fcntl.LOCK_EX` - Exclusive lock (only one process can hold it)
2. `fcntl.LOCK_NB` - Non-blocking (returns error immediately if locked)
3. Lock is automatically released when process ends
4. Lock file persists in `/tmp/` (cleared on reboot)

## Common Use Cases

- Twitter/social media auto-poster
- Data synchronization scripts
- Email sending batches
- Any cron job that shouldn't overlap

## Pitfalls

- Don't forget to release lock manually for clean exit
- Lock file location should be writable (`/tmp/` is standard)
- If script crashes hard, lock auto-releases (safe)

## Alternative for Node.js

```javascript
const fs = require('fs');

// Try to acquire lock
const lockPath = '/tmp/script.lock';
try {
    const fd = fs.openSync(lockPath, 'w');
    fs.flockSync(fd, 'exnb'); // exclusive, non-blocking
    // ... script logic ...
    fs.flockSync(fd, 'un'); // unlock
    fs.closeSync(fd);
} catch (e) {
    console.log('Another instance running');
    process.exit(1);
}
```