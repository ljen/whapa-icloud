WHATSAPP IOS E2E FORMAT
====

## 1. Introduction
This document specifies the format and decryption process for iOS WhatsApp End-to-End encrypted backups. The backup consists of independently encrypted database files (`*.enc`) and individually encrypted media within standard USTAR tar archives (`*.tar`).

## 2. Inputs
The primary input required for decryption is the 32-byte recovery key, derived from the 64-character hexadecimal string provided to the user.

### 2.1 Backup Structure
The backup directory typically resides in the iOS/iCloud Drive location:
`~/Library/Mobile Documents/57T9237FN3~net~whatsapp~WhatsApp/Accounts/<phone>/backup/`

It contains:
* `*.enc` files: Independently encrypted files (e.g., `ChatStorage.sqlite.enc`, `UserDefaults.plist.enc`).
* `*.tar` files: Unencrypted USTAR archives containing encrypted media entries (e.g., `Media.tar`, `Thumbnail.tar`).
* `Backup.plist`: A binary-plist manifest containing metadata and file sizes.

## 3. Database and File Encryption (`*.enc`)

### 3.1 Key Derivation
Encryption and verification keys are derived using a legacy variant of HKDF-SHA256 (see Section 6.1).

* Encryption Key: `enc_key = HKDF(ikm = recoveryKey, salt = nil, info = b"file", length = 32)`
* Verification Key: `mac_key = HKDF(ikm = recoveryKey, salt = nil, info = b"file-verify", length = 32)`

### 3.2 File Layout
Each `.enc` file has the following binary structure:

* Offset `0`: `1 byte` - Header flags (`0x83` indicates format version 3 and Apple Archive compression).
* Offset `1`: `1 byte` - Key Type (`0x01`).
* Offset `2`: `16 bytes` - Initialization Vector (IV).
* Offset `18`: `n-50 bytes` - Ciphertext (AES-256-CBC, PKCS#7 padded).
* Offset `n-32`: `32 bytes` - Trailer HMAC-SHA256 tag.
(where `n` is the total file length).

### 3.3 Integrity Verification
An Encrypt-then-MAC scheme is used. The HMAC-SHA256 tag covers the header, IV, and the ciphertext.

`Verify: HMAC-SHA256(key = mac_key, msg = data[0 : n-32]) == data[n-32 : n]`

### 3.4 Decryption and Decompression
After verifying the HMAC, the ciphertext is decrypted using AES-256-CBC with the derived `enc_key` and the file's stored IV. Following decryption and PKCS#7 padding removal, the plaintext is revealed to be a chunked LZFSE compressed stream (Apple "pbze" container).

The container structure:
* `[0:4]`: Magic bytes `0x70 62 7a 65` ("pbze").
* `[4:12]`: Flags (8 bytes, ignored).
* Repeats to end of stream:
  * `[+0:8]`: Decompressed chunk length (8 bytes, Big-Endian).
  * `[+8:16]`: Compressed LZFSE frame length (8 bytes, Big-Endian).
  * `[+16:16+compressed_len]`: LZFSE frame (decodable via standard LZFSE implementations).

Concatenating the decompressed chunks yields the original file (e.g., SQLite database).

## 4. Media Archive Encryption (`*.tar`)
Media files are stored within plain USTAR tar archives. Each file entry inside the tar is independently encrypted using AES-256-CBC.

### 4.1 Key Derivation
A base media key is derived from the recovery key, and specific keys are derived for each file entry using the entry's ID (the Base64-URL decoded filename).

* Base Media Key: `tar_key = HKDF(ikm = recoveryKey, salt = nil, info = b"tar", length = 32)`
* Entry Identifier: `id = Base64URL_Decode(entry_name)` (32-byte hash)
* Entry Key Block: `block = HKDF(ikm = tar_key, salt = id, info = b"\x00", length = 80)`

The 80-byte `block` provides the cryptographic parameters:
* `enc_key` = `block[0:32]`
* `mac_key` = `block[32:64]`
* `iv` = `block[64:80]`

### 4.2 Entry Framing and Integrity
The structure of each media tar entry is:
* `entry[:-32]`: Ciphertext (length is a multiple of 16).
* `entry[-32:]`: HMAC-SHA256 tag.

Integrity must be verified prior to decryption:
`Verify: HMAC-SHA256(key = mac_key, msg = iv || ciphertext) == entry[-32:]`

### 4.3 Entry Wrapper Format
After decryption and PKCS#7 padding removal, the plaintext reveals a wrapper containing the file path and actual content or a reference to another file (deduplication).

Wrapper layout:
* `[0]`: Version (`0x01`).
* `[1]`: Type (`0x00` for inline media, `0x01` for deduplication link).
* `[2:10]`: Modification time in milliseconds (8 bytes, Big-Endian).
* `[10]`: Destination filename length (`fnlen`).
* `[11:11+fnlen]`: Destination filename string.

Type `0x00` Payload:
* `[+0:8]`: Content length (8 bytes, Big-Endian).
* `[+8:...]`: Actual media file bytes.

Type `0x01` Payload:
* Contains a source path string referencing another media entry inside the archive to be copied.

## 5. Notes and Caveats (Unique Implementations)

### 5.1 Legacy Signal HKDF
WhatsApp employs a legacy "v1" variant of the Signal-protocol HKDF. Standard RFC-5869 HKDF implementations initialize the HMAC expansion counter at `0x01`. The legacy WhatsApp implementation initializes the counter at `0x00`. Off-the-shelf HKDF libraries will generate incorrect keys if used out of the box.

### 5.2 AES-CBC over AES-GCM
Despite internal binary strings referencing "GCM", the encryption mode utilized for both database (`*.enc`) files and media (`*.tar`) entries is AES-256-CBC combined with an Encrypt-then-MAC (HMAC-SHA256) approach.

### 5.3 Stored Initialization Vectors
For `.enc` files, the IV is persistently stored at offsets 2 through 18 of the file envelope and is not derived from the HKDF key material. The 80-byte HKDF derivation produces an unused 16-byte block from bytes 64 to 80.

### 5.4 Custom Apple Archive Magic
The LZFSE compressed envelope uses a custom magic identifier `pbze` (`0x70 62 7a 65`), replacing the standard Apple `pbzx` signature. Decompression logic must be adapted to accept this signature.

### 5.5 Shared Keying
All `.enc` files share identical `enc_key` and `mac_key` values. There is no file-specific salt used during key derivation; uniqueness per file is strictly provided by the embedded IV.
