# sksd
<ins>**S**</ins>pyder <ins>**K**</ins>ernel <ins>**S**</ins>pinner <ins>**D**</ins>aemon


# Preample

Up to now there is some 'buttox pains' when it comes to:
  1. **Detecting what 'machines' are available in your network**, this is prior to 'connecting' to them, and currently not available.
  2. **Connecting to remote spyder-kernels**, this is available, but it is very manual. (actually almost un-usable).
  3. **Environment(s)** ... If ther is any, they are not 'controlled' from `Spyder`. (Or better yet : the application you are coding for!)

This initial proposal tries to solve thes issues transparantly both remote **and local!** (see notes at end)

# Description (Proposal)

The `sksd` uses [zeroconf](https://github.com/jstasiak/python-zeroconf) to announce it's presence to the zeroconf network.

[Spyder](https://github.com/spyder-ide/spyder) can now easily 'discover' what machines are available (including the local machine)! 

`Spyder` then 'contact' the desired `sksd` and ask him to spin up a `spyder-kernel` as a `user` in a specific `conda environment`, and pass the needed 'credentials' back to `spyder` so `spyder` can connect auto-magically connect to the spinned spyder-kernel.

## installation
https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/admin-multi-user-install.html

## modus operandi

### sksd

### Spyder

This `sksd`, on startup will collect:

  *
  * [A free port](https://github.com/nerohmot/spyder-kernels/blob/nerohmot/proposal/publish.py#L25) (so no need for 'well known ports' shit)
  * the <ins>**host name**</ins> of the system (mind you, **not** the fully quantified one, no need for that either)
  ```python
  import socket
  hostname = socket.gethostname()
  ```
  * the list of <ins>**conda environments**</ins>

Then he will publish this on the zero-conf network, under `_skd._tcp.local.` When the daemon dies (shut down system), he will un-publish,
and yes, he needs to update the pulication from thime to time to satisfy the TTL's.

From `Spyder` side, he will have his '[listener](discover.py)' running, so he knows how to reach all the `spyder-kerneld`'s

Good, so now we have a system where `Spyder` can 'discover' all `remote` machines, but on these machines we still have no instance(s) of
the `spyder-kernels` running. We can however open a TCP/IP connection (we have the IP address and the port) to the deamon and start
interacting with the daemon like so: (over simplified for now)

  - Q: Please spin-up a `spyder-kernels` in environment `xyz` as user `john`. (`xyz` would basically be one of the environments existing on the host)
  - A1: Done, here is the connection data. (And the 'connection data' would basically be the `jupyter/runtime/dir/path/kernal-id.json`)
  - A2: Done, however user `john` is unknown to me, I casted him into the `guest` user and here is the connection data.
  - A3: Done, however the environment `xyz` didn't exist, I created it, here is the connection data.
  - A4: I already have environment `xyz` but it is not compatible to what you gave me.
  - ...

There thus is a thin layer between the `spyder-kernelsd` and `conda` to manage the remote (but why not also the local-?) environments. The `spyder-kernels` themselves would probably be launched like this:
```shell
#!/usr/bin/env conda run -n desired-environment python -m spyder_kernels.console &
```
by the `spyder-kernelsd`.

# Notes
  1. Once spyder has his own `application environment`, we have the same 'control' over the local environments 😍 (Including the spyder application environmnet itself! think: plugin installation) without any additional work!
  2. By starting `Spyder`, we make our machine also accessable for others ... not sure if this is (always) desirable ... maybe we need to foresee something to block that (probably in the settings of `Spyder`)
  3. Above I didn't talk about the `password` for user `john`, but it is obvious we need then to obtain an encription key to exchange the password (that itself probably comes straight from the [keyring](https://github.com/jaraco/keyring)) ... probably something like [TLS 1.3](https://tools.ietf.org/pdf/rfc8446.pdf#page=96) 😈 python standard [ssl](https://docs.python.org/3/library/ssl.html) library already has this implemented. And, oh, yes, the certificate (or rather the pointer to the CA) will probably live in the `spyder-kernelsd.conf` file. 😎
  4. The `hostname` above is usefull, but now always meaningfull (think server farms) it is probably a good idea that in the `spyder-kernelsd.conf` file there is also a 'pretty host name' like : `John's Raspberry Pi` or `Tom's MiniSCT` 🤓
  5. Also the `guest` account thingy probably lives in `spyder-kernelsd.conf`
  6. os independent 'daemon library' ... woops ... need more elaboration here!
