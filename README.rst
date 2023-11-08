Development
===========

Dependencies:

- Python 3 (tested mainly on 3.10, 3.11, and 3.12)
- asn1_ (from PyPI; run-time dependency only)
- cryptography_ (from PyPI; run-time dependency only)
- cffi_ (from PyPI; build-time dependency only)
- setuptools_ (from PyPI; build-time dependency only)
- a C compiler (build-time dependency only)

  - If you're on Windows, https://visualstudio.microsoft.com/visual-cpp-build-tools/ AND THEN make sure you launch "Developer Command Prompt for VS 2022" or whatever
  - If you're on Linux, install build-essential_ or `"Development Tools"`_ or something like that

    - Linux users may also not have got the `Python Headers`_ free with their xbox and will have to go beg on the streets to get them before cffi will work

  - haven't tested it, but if you're allergic to installing things outside the venv you might be able to use `this C compiler <https://pypi.org/project/ziglang/>`

Getting started:

0. Maybe `use a venv <https://www.bitecode.dev/p/relieving-your-python-packaging-pain>`_ or whatever if you want to

   - tldr: ``python3 -m venv .venv; . .venv/bin/activate`` on Linux (`install it <https://packages.ubuntu.com/jammy/python/python3-venv>` if needed); ``py -m venv .venv && .venv\bin\activate.bat`` on Windows

1. Run ``python -m pip install -r requirements-dev.txt`` to get CFFI and setuptools

   - if on Windows, make sure you're running (somehow) from an environment that gives you access to your C compiler and ISN'T in cross-compile mode (unless that's what you meant to do)

2. Run ``python -m pip install -e .`` to get the rest of the build-time dependencies

   - I can't friggin figure out setuptools X cffi, pls halp (the code "works" as-written, but is BAD BAD BAD BAD BAD)

   - If you make any changes that implicate the C library or CFFI, you will need to re-run the command; OTHERWISE, your changes should apply basically live

3. Run ``python -m pqc.demo`` to test it (run this from a DIFFERENT directory, such as your home folder, so you can be sure it's being imported properly)

.. _cffi: https://cffi.readthedocs.io/en/release-1.16/
.. _setuptools: https://setuptools.pypa.io/en/stable/
.. _asn1: https://github.com/andrivet/python-asn1
.. _cryptography: https://github.com/pyca/cryptography
.. _`Python Headers`: https://packages.ubuntu.com/jammy/python3-dev
.. _build-essential: https://packages.ubuntu.com/jammy/build-essential
.. _`"Development Tools"`: https://git.rockylinux.org/rocky/comps/-/blob/e6c8f29a7686326a731ea72b6caa06dabc7801b5/comps-rocky-9-lh.xml#L1768

Usage
=====

At this time, ONLY the McEliece 6960,119 KEM is exposed. If this displeases you, I beg and solicit (either publicly or privately; e-mail is great!) free advice on CFFI and setuptools.

::

    from pqc.kem import mceliece6960119
    pk, sk = mceliece6960119.kem_keypair()  # WARNING these are some chonky keys (1MiB public, 13.6KiB private); consider using base64.encode() to print them
    k, ek = mceliece6960119.kem_enc(pk)
    # ct = MY_SYMMETRIC_CRYPTOSYSTEM.enc(m, key=k)
    k_result = mceliece6960119.kem_dec(ek, sk); assert k == k_result
    # m_result = MY_SYMMETRIC_CRYPTOSYSTEM.dec(ct, key=k_result)