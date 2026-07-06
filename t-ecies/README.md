# anvil-t-ecies

Coordinates:

```text
org.exploit.anvil:t-ecies:0.1.2
```

Java package:

```text
org.exploit.ecies
```

`t-ecies` contains threshold ECIES components: ElGamal KEM encryption,
participant partial decryption, DLEQ-checked partial decrypt combination, and
symmetric cipher adapters.

## Primary API

| Area | Types |
| --- | --- |
| Client | `ThresholdECIESClient` |
| Context | `ECIESContext`, `ECIESCryptoContext`, `PartialDecryptContext` |
| In-memory contexts | `InMemoryCryptoContext`, `InMemoryPartialDecryptContext` |
| KEM | `ElGamalKEM` |
| Partial decrypt | `PartialDecryptor`, `PartialDecryptCombiner`, `PartialDecrypt` |
| Ciphertext | `CipherText`, `EncryptionResult` |
| Symmetric ciphers | `SymmetricCipher`, `AesGcmCipher`, `ChaCha20Poly1305Cipher` |
| KDF | `HKDF` |
| Abort | `IdentifiableAbortException` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:t-ecies"
    implementation "org.exploit.anvil:ecc-p256"
}
```

```java
import org.exploit.ecies.ThresholdECIESClient;
import org.exploit.ecies.cipher.AesGcmCipher;

var client = new ThresholdECIESClient<>(
    eciesContext,
    new AesGcmCipher()
);

var ciphertext = client.encryptor().encrypt(message);
var partial = client.decryptor().partialDecrypt(ciphertext);
client.context().decrypt().storePartialDecrypt(partial);
var plaintext = client.combiner().decrypt(ciphertext);
```

## Ciphertext Encoding

`CipherText` stores:

```text
version
R
c
tag
```

It supports binary encoding with `encode()` / `decode(byte[])` and text encoding
with `encode64()` / `decode64(String)`. The decoder accepts the current
versioned format and the legacy three-part text format.

## Dependencies

This module depends on `ecc-spi`, `bigint`, `zk-dlog`, `util`, and Bouncy Castle
`bcprov-jdk18on`.
