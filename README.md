# sksd
Spyder Kernel Spinner Daemon

# Description
The `sksd` uses [zeroconf]() to announce it's presence to the zeroconf network.
It can 'talk' directly with [Spyder]()
It can spin up a `spyder-kernel` as a user in a specific conda environment, and pass the needed 'credentials' to `spyder` so `spyder` can connect auto-magically to both local and remote kernels.
