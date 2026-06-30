import timeit
import hashlib
import hmac
import time

def hkdf_legacy(ikm, salt, info, length):
    if salt is None:
        salt = b"\x00" * 32
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out = b""
    t = b""
    i = 0
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([i & 0xFF]), hashlib.sha256).digest()
        out += t
        i += 1
    return out[:length]

def hkdf_legacy_opt(ikm, salt, info, length):
    if salt is None:
        salt = b"\x00" * 32
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out_parts = []
    out_len = 0
    t = b""
    i = 0
    while out_len < length:
        t = hmac.new(prk, t + info + bytes([i & 0xFF]), hashlib.sha256).digest()
        out_parts.append(t)
        out_len += len(t)
        i += 1
    return b"".join(out_parts)[:length]

ikm = b"some_initial_keying_material_that_is_long"
salt = b"some_salt_that_is_long"
info = b"some_info_that_is_long"
length = 1024 * 512 # 512KB

assert hkdf_legacy(ikm, salt, info, length) == hkdf_legacy_opt(ikm, salt, info, length)

def run_bench(func):
    return func(ikm, salt, info, length)

start = time.time()
run_bench(hkdf_legacy)
print(f"Legacy: {time.time() - start:.4f}s")

start = time.time()
run_bench(hkdf_legacy_opt)
print(f"Opt: {time.time() - start:.4f}s")
