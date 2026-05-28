# anvil-xchacha20-poly1305

Coordinates:

```text
org.exploit.anvil:xchacha20-poly1305:0.1.0
```

Java package:

```text
org.exploit.crypto.aead
```

`xchacha20-poly1305` provides an AEAD interface and a libsodium-backed
XChaCha20-Poly1305 implementation.

## Primary API

| Type | Purpose |
| --- | --- |
| `AEADCipher` | Interface with `encrypt` and `decrypt`. |
| `XChaCha20Poly1305` | Singleton AEAD implementation over libsodium's IETF XChaCha20-Poly1305 functions. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.0")
    implementation "org.exploit.anvil:xchacha20-poly1305"
}
```

```java
import org.exploit.crypto.aead.XChaCha20Poly1305;

var cipher = XChaCha20Poly1305.getInstance();

byte[] encrypted = cipher.encrypt(plaintext, aad, key32);
byte[] decrypted = cipher.decrypt(encrypted, aad, key32);
```

## Encoding

`encrypt` returns:

```text
nonce || ciphertext || tag
```

The nonce is generated internally with `SecureRandom`. `decrypt` expects the
same combined format. The key length is checked against
`crypto_aead_xchacha20poly1305_ietf_keybytes()`.

## Runtime

The module uses libsodium through Java FFM bindings. The loader tries a bundled
`natives/{os}-{arch}/` resource first, then falls back to
`System.loadLibrary("sodium")` and `System.loadLibrary("libsodium")`.

Applications that use this module through the class path should launch with:

```bash
--enable-native-access=ALL-UNNAMED
```
