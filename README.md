# sksd
<ins>**S**</ins>pyder <ins>**K**</ins>ernel <ins>**S**</ins>pinner <ins>**D**</ins>aemon

## Preample

Up to now there is some 'buttox pains' in `spyder` when it comes to:
1. **Detecting what 'machines' are available in your network**, this is prior to 'connecting' to them, and currently not available.
2. **Connecting to remote spyder-kernels**, this is available, but it is very manual. (actually almost un-usable).
3. **Environment(s)** ... `spyder` runs in the same environmnet as the environment we are coding for. This has the following consequences:
  - The app **needs** to conform to the `spyder` requirements. (not the packages themselves, but their restrictions can pose a problem)
  - As if this is not enough, the app **needs** to conform to the rest of the environment **too**. (eg `anaconda`, again not the packages but their restrictions make life hard) ... Shouldn't it be the other way around? Shouldn't the environment conform to the application?!?
  - As `spyder` doesn't know up-front what his run-time environement will be, a lot of extra testing needs to be done, which doesn't help the 'time to market' **and** results in further package restrictions.
  
The goal of this initial proposal is to solve these issues transparantly!

## Proposal

If we give `spyder` his own 'application environment', for example `_spyder_`, that holds whatever `spyder` (and it's plugins) need, even with very strong restrictions if so desired. Then `spyder` testing will become much more lightweight **and** focused on `spyder` itself!

As a consequence, `spyder` whould need to start the (local) `spyder-kernel` a bit differently:
```sh
conda run -n anaconda python -m spyder_kernels.console
```
This way the spyder-kernel runs in the anaconda environment, and connects to the `spyder-console` which is running in the `_spyder_` environment. 😎

**NOTE:**
> This way we don't loose any users by dropping Python2 support for `spyder` itself! The user is probably already programming in Python3, but he (or his company/organization) might have tools/libraries written for Python2, they work fine and just need small touch-up's from time to time. It is **very unlikely** that they accept a Python3 overhaul of those tools just because of the IDE! It **is very likely** that they will just switch IDE! 😱 Using this concept however, they just need to run their tools in an apporpriate environment, which they already do in any case! 😇

Nice, but how do we connect `spyder` to a <ins>**remote**</ins> `spyder-kernel` running on a **head-full** or even worse, a **head-less** box? 

Well, here we will not get around the creation of an 'omni-present' 'beacon' ... let's call a cat a cat ... we need a **DAEMON**, and that is what **sksd** (<ins>**S**</ins>pyder <ins>**K**</ins>ernel <ins>**S**</ins>pinner **D**aemon) is all about.

The tasks of **sksd** are:

- Make himself, his state and his 'capabilities' be known to the 'world'. 👍
- Spin up `spyder-kernel`(s) on behalf of a `user` in a specified `environment` from `spyder` and pass the 'connection data' back to `spyder` so that the `spyder-console` can connect! 🎉
- Serve as a `gateway` to administer environments remotely from `spyder` or possibly other tools in a graphical way! 😍

**NOTE:**
> A 'user daemon' (Contradictio in terminis) although much easier to implement, as it is a simpel process with a user's login process (or one of it's ancestors) as parent, will not do the trick as it will **not be 'omni-present'**! One first needs to login to the box ... and how whould that work with a truely head-less device ?!?

## Specification

`sksd` will most likely get his own `_sksd_` 'application environment'. Where ? Well a daemon is running as root, so forceably at the root level, which means : ["administering a multi-user conda installation"](https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/admin-multi-user-install.html) 🎉🎉🎉 beautifull! (Food for thought: The `_spyder_` application environment should probably also live at 'system level'. 🤔)

So when a box boots, the `sksd` will be brought up automatically. It will find an unused [free port](https://github.com/nerohmot/sksd/blob/master/sksd/daemon/publish.py#L25) to be contacted on, and then use [zeroconf](https://github.com/jstasiak/python-zeroconf) (which is `noarch` package 👍👍👍) to announce it's presence to the zeroconf network, and thus to the world.

A `Spyder` instance can now easily 'discover' what machines are available (including his own local machine 😂) by also using this zeroconf library. (transparency : ✅)

`Spyder` then can 'contact' the desired `sksd` (over TCP/IP [socket](https://docs.python.org/3/library/socket.html)s) and can:

- Ask to spin up a `spyder-kernel` as a `user` in a specific `conda` `environment`, and pass the needed 'credentials' (read: the spyder-kernel's .json file) back to `spyder` so that the `spyder-console` can connect auto-magically to the spinned `spyder-kernel`.

- Administer a `user` environment. For this we can basically take Gonzalo's old work, split it into the GUI part that will transform as a `spyder5` plugin, and the part that runs the commands in a sub-process and returns the `json` answers, that part can be merged in sksd.

## Notes

### Licensing

We relay on the `noarch` [zeroconf](https://github.com/jstasiak/python-zeroconf) package which is licensed under [LGPLv2.1](https://github.com/jstasiak/python-zeroconf/blob/master/COPYING). Given the fact that I had in mind to conform to `spyder-ide` licencing philosophy, thus choose `MIT` I am not sure if this would be a problem or not ...

After all, we just use the library, it is thus not 'derived work' or so ... IMHO there is no problem, but someone with more knowledge should maybe have a look at the situation before release.

### Cross-platform 'daemon' implementation

There is some fundamental differences in how `daemons` are constructed in Linux/Windows/MacOS ...

Maybe [daemoniker](https://daemoniker.readthedocs.io/en/latest/) (or similar) can help there, but for the moment (proof of concept) we'll limit ourselves to Linux, and use 'well-behaved' daemons according to Stevens.

### Security

I didn't talk about the `user` `password`, but it is obvious we need to obtain an encription key to exchange the password (that itself probably comes straight from the [keyring](https://github.com/jaraco/keyring)) ... probably something like [TLS 1.3](https://tools.ietf.org/pdf/rfc8446.pdf#page=96) will be used (both the python standard [ssl](https://docs.python.org/3/library/ssl.html) library and [wolfssl](https://github.com/wolfSSL/wolfssl) already implement TLS1.3). And, oh, yes, the certificate (or rather the pointer to the CA) will probably live in the `sksd.conf` file. 😎

### Dependencies and their implications

  * Old situation:
    `spyder` ➜ `spyder-kernels`
  
  * New situation: no more **package** dependencies !
    `Spyder`
    `sksd` 
    `spyder-kernels` (need to be located in the environment!)

### Spyder installer

Question is if the installer needs to be 'graphical' ... 

In any case, the installer for spyder should be based on [minifoge](https://github.com/conda-forge/miniforge), however we might need to talk to Ilan to see what it takes to also add 'Windows' to the installer list. Then it is a matter of `conda install -c spyder-ide spyder` 

... need some input from Carlos to understand how he sees this ...

### sksd concurency

We don't need to make the sksd 'concurrent' (read: able to talk to multiple `spyder` instances at the same time).
`sksd` publishes (actually 'updates') his state to the world, so when a `spyder` instance connects to the `sksd`, `sksd` will let the word know that he is bussy. We can do so, because the connections are short lived anyway.

### sksd.conf

The `sksd` config file is to be UTF-8 encoded, this way we can publish very nice machine names (mind you **not** the hostname, that one is shared in any case) like for example:

- "Gonzalo Peña-Castellanos' RPi"
- "Tom Hören's MiniSCT"
- ...

We need to start the `sksd` config file with `# -*- coding: utf-8 -*-`, this way also the editors should understand that.

### Conda Channels

Note, that eventhough `spyder` can still be part of a standard `anaconda` installation, it no longer is bound to the `anaconda` channel only! Also `conda-forge` and `pip` come into scope now! 😍 (hint for the whole Qt stuff)

PS: the 'administring' part also should include adding/removing/re-arranging channels !

### Open issues
- what about kite ? (where does it run? local or remote?)
- `spyder-kernels` does (as I understand) accept a python module to be run (remotely), however what about a package? 
