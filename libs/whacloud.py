#!/usr/bin/env python3
"""
whacloud.py - Whatsapp iCloud Extractor (Mac Edition)
This script extracts and decrypts WhatsApp End-to-End Encrypted (E2EE) backups 
locally from iCloud Drive on a Mac.

Where are the files located on a Mac?
macOS automatically syncs iCloud Drive. The WhatsApp backup files are typically located at:
~/Library/Mobile Documents/57T9237FN3~net~whatsapp~WhatsApp/Accounts/<Phone_Number_or_ID>/backup/

Within this directory, you will find:
- .enc files (e.g., ChatStorage.sqlite.enc) which contain the SQLite databases and plists.
- .tar files (e.g., Media.tar, Video.tar) which contain the media.

Note: You need the 64-character hex recovery key to decrypt the backup.

Usage:
  python3 whacloud.py --key <64_hex_chars> [--output <output_dir>] [--backup-path <path>]
"""

import sys
import os
import struct
import hmac
import hashlib
import ctypes
import base64
import tarfile
import shutil
import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def banner():
    print(r"""
     __      __.__           _________ .__                   .___
    /  \    /  \  |__ _____  \_   ___ \|  |   ____  __ __  __| _/
    \   \/\/   /  |  \\__  \ /    \  \/|  |  /  _ \|  |  \/ __ | 
     \        /|   Y  \/ __ \\     \___|  |_(  <_> )  |  / /_/ | 
      \__/\  / |___|  (____  /\______  /____/\____/|____/\____ | 
           \/       \/     \/        \/                       \/ 

    ------------------ Whatsapp iCloud Extractor ----------------
    """)

# --- Crypto and LZFSE setup ---

def hkdf_legacy(ikm, salt, info, length):
    if salt is None: 
        salt = b"\x00"*32
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out = b""
    t = b""
    i = 0
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([i & 0xff]), hashlib.sha256).digest()
        out += t
        i += 1
    return out[:length]

def hkdf_v1(ikm, info, length):
    return hkdf_legacy(ikm, None, info, length)

# LZFSE decoding via macOS native libcompression
COMPRESSION_LZFSE = 0x801
try:
    _lib = ctypes.CDLL("/usr/lib/libcompression.dylib")
    _lib.compression_decode_buffer.restype = ctypes.c_size_t
    _lib.compression_decode_buffer.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_int
    ]
except Exception as e:
    _lib = None

def lzfse_decode(src, hint):
    if _lib is None:
        raise RuntimeError("libcompression.dylib not found. This script requires macOS.")
    cap = max(hint, len(src)) * 2 + 4096
    while True:
        dst = ctypes.create_string_buffer(cap)
        got = _lib.compression_decode_buffer(dst, cap, src, len(src), None, COMPRESSION_LZFSE)
        if got == 0: 
            raise RuntimeError("LZFSE decode failed")
        if got < cap: 
            return dst.raw[:got]
        cap *= 2

def decrypt_enc(path, out_path, key):
    with open(path, "rb") as f:
        data = f.read()
    n = len(data)
    if n < 50 or data[0] != 0x83:
        print(f"[-] Skipping {path} (not a valid 0x83 .enc envelope)")
        return False
    enc_key = hkdf_v1(key, b"file", 32)
    mac_key = hkdf_v1(key, b"file-verify", 32)
    iv = data[2:18]
    ct = data[18:n-32]
    tag = data[n-32:n]
    
    calc = hmac.new(mac_key, data[0:n-32], hashlib.sha256).digest()
    if calc != tag:
        print(f"[-] HMAC verification failed for {path}")
        return False
        
    d = Cipher(algorithms.AES(enc_key), modes.CBC(iv)).decryptor()
    pt = d.update(ct) + d.finalize()
    pad = pt[-1]
    if 1 <= pad <= 16 and pt[-pad:] == bytes([pad])*pad: 
        pt = pt[:-pad]
        
    if pt[:4] not in (b"pbze", b"pbzx"):
        print(f"[-] Unexpected container magic for {path}")
        return False
        
    off = 12
    out = b""
    while off + 16 <= len(pt):
        dlen = struct.unpack(">Q", pt[off:off+8])[0]
        clen = struct.unpack(">Q", pt[off+8:off+16])[0]
        off += 16
        payload = pt[off:off+clen]
        off += clen
        out += lzfse_decode(payload, dlen)
        
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(out)
    print(f"[+] Decrypted {os.path.basename(path)} -> {out_path}")
    return True

def derive_tar_key(backup_key):
    return hkdf_legacy(backup_key, None, b"tar", 32)

def derive_file_block(tar_key, entry_id_32):
    return hkdf_legacy(tar_key, entry_id_32, b"\x00", 80)

def _pkcs7_strip(b):
    pad = b[-1]
    if 1 <= pad <= 16 and b[-pad:] == bytes([pad])*pad:
        return b[:-pad]
    return b

def _safe_join(out_dir, rel):
    rel = rel.lstrip("/")
    root = os.path.realpath(out_dir)
    dst = os.path.realpath(os.path.join(root, rel))
    if dst != root and not dst.startswith(root + os.sep):
        raise ValueError(f"Refusing path that escapes output dir: {rel!r}")
    return dst

def decrypt_media_entry(entry_bytes, tar_key, entry_id_32):
    blk = derive_file_block(tar_key, entry_id_32)
    enc_key, mac_key, iv = blk[0:32], blk[32:64], blk[64:80]
    if len(entry_bytes) < 48 or (len(entry_bytes) - 32) % 16 != 0:
        return None
    ct, tag = entry_bytes[:-32], entry_bytes[-32:]
    
    calc = hmac.new(mac_key, iv + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(calc, tag):
        return None
        
    d = Cipher(algorithms.AES(enc_key), modes.CBC(iv)).decryptor()
    pt = d.update(ct) + d.finalize()
    if len(pt) < 11 or pt[0] != 0x01:
        return None
        
    etype = pt[1]
    fnlen = pt[10]
    if 11 + fnlen > len(pt):
        return None
    fn = pt[11:11+fnlen].decode("utf-8", errors="replace").lstrip("/")
    off = 11 + fnlen
    
    if etype == 0x00:
        clen = struct.unpack(">Q", pt[off:off+8])[0]
        contents = pt[off+8:off+8+clen]
        return {"type": 0, "filename": fn, "contents": contents}
    elif etype == 0x01:
        core = _pkcs7_strip(pt)
        src = core[off:].decode("utf-8", errors="replace").lstrip("/")
        return {"type": 1, "dest": fn, "src": src}
    return None

def decrypt_media_tar(path, out_dir, backup_key):
    tar_key = derive_tar_key(backup_key)
    links = []
    extracted = 0
    with tarfile.open(path, "r") as t:
        for m in t.getmembers():
            try:
                entry_id = base64.urlsafe_b64decode(m.name)
            except Exception:
                continue
            if len(entry_id) != 32 or m.size == 0:
                continue
            e = decrypt_media_entry(t.extractfile(m).read(), tar_key, entry_id)
            if not e:
                continue
                
            if e["type"] == 0:
                dst = _safe_join(out_dir, e["filename"])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(e["contents"])
                extracted += 1
            else:
                links.append((e["dest"], e["src"]))
                
    linked = 0
    for dest, src in links:
        try:
            sp = _safe_join(out_dir, src)
            dp = _safe_join(out_dir, dest)
            if os.path.exists(sp):
                os.makedirs(os.path.dirname(dp), exist_ok=True)
                shutil.copyfile(sp, dp)
                linked += 1
        except ValueError:
            pass
            
    print(f"[+] Decrypted {os.path.basename(path)} -> extracted {extracted} files, {linked} copies")

def is_media_tar(path):
    try:
        with open(path, "rb") as f:
            head = f.read(265)
        if head[:1] == b"\x83":
            return False
        return head[257:262] == b"ustar"
    except Exception:
        return False

def find_mac_backups():
    base = os.path.expanduser("~/Library/Mobile Documents/57T9237FN3~net~whatsapp~WhatsApp/Accounts")
    backups = []
    if os.path.isdir(base):
        for account in os.listdir(base):
            backup_path = os.path.join(base, account, "backup")
            if os.path.isdir(backup_path):
                backups.append(backup_path)
    return backups

def main():
    banner()
    parser = argparse.ArgumentParser(
        description="Extract and decrypt WhatsApp E2E backups from Mac iCloud Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Where are the files located on a Mac?
macOS automatically syncs iCloud Drive. The WhatsApp backup files are typically located at:
~/Library/Mobile Documents/57T9237FN3~net~whatsapp~WhatsApp/Accounts/<Phone_Number_or_ID>/backup/

This tool will try to auto-discover them. You can also specify a custom --backup-path.
"""
    )
    parser.add_argument("-k", "--key", required=True, help="64-character hex recovery key")
    parser.add_argument("-o", "--output", default="whacloud_output", help="Output directory (default: whacloud_output)")
    parser.add_argument("-b", "--backup-path", help="Path to the backup directory (if not auto-detected)")
    
    args = parser.parse_args()
    
    try:
        key_bytes = bytes.fromhex(args.key)
        if len(key_bytes) != 32:
            raise ValueError
    except ValueError:
        print("[-] Invalid key format. The key must be exactly 64 hex characters.")
        sys.exit(1)
        
    backups = []
    if args.backup_path:
        if os.path.isdir(args.backup_path):
            backups.append(args.backup_path)
        else:
            print(f"[-] Provided backup path is not a directory: {args.backup_path}")
            sys.exit(1)
    else:
        backups = find_mac_backups()
        if not backups:
            print("[-] No WhatsApp backups automatically found on this Mac.")
            print("    Please ensure iCloud Drive is synced and try providing --backup-path.")
            sys.exit(1)
            
    os.makedirs(args.output, exist_ok=True)
    
    for backup in backups:
        print(f"\n[*] Processing backup directory: {backup}")
        for root, dirs, files in os.walk(backup):
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, backup)
                
                if file.endswith(".enc"):
                    out_path = os.path.join(args.output, rel_path[:-4]) # strip .enc
                    decrypt_enc(filepath, out_path, key_bytes)
                elif file.endswith(".tar") and is_media_tar(filepath):
                    # extract directly to output dir
                    decrypt_media_tar(filepath, args.output, key_bytes)
                elif file == "Backup.plist":
                    # copy the manifest
                    shutil.copy(filepath, os.path.join(args.output, file))
                    
    print("\n[i] Done. Decrypted files are saved in:", os.path.abspath(args.output))

if __name__ == "__main__":
    main()
