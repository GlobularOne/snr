FAQ
===

Here we answer some of the most common question asked about snr.

Can I run snr on windows?
-------------------------

Natively? No. Theoretically, you should be able to run it on WSL, but we provide no support whatsoever for WSL. We recommend using a Linux VM

How much of my internet connection does snr use?
------------------------------------------------

Snr downloads things once (with the exception of payload dependencies which are very lightweight, and not common) during it's initialization process.

Can I run snr as root?
----------------------

Yes you can, but then you must be extra careful if you use external payloads not written by us, as they execute code on your machine as well. If snr needs root, it will use `sudo` so root permissions can be used whenever it is absolutely necessary.

I configured something wrong, can I revert it?
----------------------------------------------

In general, you can just reload the shell using `reload` command, it also resets the payload loaded (so you have to `use` it again)
If you got a wrong value in the config file, you can just remove the config file. But for a variable, you can reload the payload to automatically reset the variables as well `use <payload>`

Can I hack my ex/classmate/this guy I don't like with it?
---------------------------------------------------------

No, we unequivocally condemn any illegal activities using this tool. It was strictly created because of passion, to raise awareness and aid during physical pentest sessions, or for education. It's your responsibility to use this tool responsibly.
