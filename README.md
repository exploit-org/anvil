![Anvil](assets/anvil-logo.png)

# anvil

Anvil is a Java 25 multi-module cryptography library published under the
`org.exploit.anvil` Maven group. The modules are split by primitive, curve, and
threshold protocol layer so applications can depend only on the pieces they use.

Anvil is a continuation of
[tss4j](https://github.com/tkeeper-org/tss4j) under Java 25 and is part of the
[TKeeper](https://github.com/tkeeper-org/tkeeper) Java 25 API transition. It is intended to be used in TKeeper and other
[exploit.org](https://exploit.org) products.

Java packages currently use the existing `org.exploit.*` namespaces. Maven
coordinates use `org.exploit.anvil:{artifact}:{version}`.

## Coordinates

Current project version:

```text
0.1.2
```

Gradle usage with the BOM:

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")

    implementation "org.exploit.anvil:ecc-secp256k1"
    implementation "org.exploit.anvil:paillier"
}
```

Gradle usage without the BOM:

```groovy
dependencies {
    implementation "org.exploit.anvil:ecc-secp256k1:0.1.2"
    implementation "org.exploit.anvil:paillier:0.1.2"
}
```

The BOM aligns all Anvil artifacts to the same version. The modules are
published as normal Java artifacts with Maven metadata; they are not shaded.
Consumers receive transitive Java dependencies through their build tool, while
native library resolution remains explicit at runtime.

## Runtime

The build is configured for Java 25 and compiles with preview features enabled.
Code that reaches native bindings uses the Java Foreign Function and Memory API.
Runtime launches that use native-backed modules should enable native access for
the application class path:

```bash
java --enable-native-access=ALL-UNNAMED ...
```

Native-backed modules load bundled resources under `natives/{os}-{arch}/` first
if present in the runtime class path, then fall back to system libraries.

Native library names used by the loaders:

| Module | Native library |
| --- | --- |
| `bigint` | `gmp` |
| `ecc-secp256k1` | `secp256k1` |
| `ecc-ed25519` | `sodium`, `libsodium` |
| `xchacha20-poly1305` | `sodium`, `libsodium` |

Loader resource tags are formed from `linux`, `macos`, or `windows` plus
`amd64` or `aarch64`, for example `linux-amd64` or `macos-aarch64`.

## Modules

| Artifact | Module path | Main packages | Scope |
| --- | --- | --- | --- |
| `bom` | `:bom` | none | Java platform BOM for Anvil artifact alignment. |
| `bigint` | `:bigint` | `org.exploit.bigint` | GMP-backed arbitrary precision integers, CSPRNG access, prime and Blum-prime generation. |
| `util` | `:util` | `org.exploit.anvil.util` | Shared byte encoding and message digest helpers. |
| `ecc-spi` | `:ecc-spi` | `org.exploit.ecc.spi`, `org.exploit.ecc.util` | Curve, key, point, signer, verifier, signature, and hash-to-curve interfaces. |
| `ecc-secp256k1` | `:ecc-secp256k1` | `org.exploit.ecc.secp256k1` | secp256k1 keys, point operations, ECDSA, recoverable ECDSA, BIP340, Taproot helpers, hash-to-curve. |
| `ecc-ed25519` | `:ecc-ed25519` | `org.exploit.ecc.ed25519` | Ed25519 keys, point operations, EdDSA signing and verification. |
| `ecc-p256` | `:ecc-p256` | `org.exploit.ecc.p256` | P-256 keys, point operations, ECDSA, recoverable ECDSA, hash-to-curve. |
| `paillier` | `:paillier` | `org.exploit.crypto.paillier` | Paillier key generation, encryption/decryption, MtA helpers, and Paillier-related ZK proofs. |
| `shamir` | `:shamir` | `org.exploit.crypto.shamir` | Shamir splitting and recovery for elliptic-curve private scalars. |
| `t-schnorr` | `:t-schnorr` | `org.exploit.tss.frost` | FROST core contexts, preprocessing, partial signing, and aggregation. |
| `frost-ed25519` | `:t-schnorr:frost-ed25519` | `org.exploit.tss.frost.ed25519` | FROST Ed25519 scheme and SHA-512 cipher suite. |
| `frost-secp256k1` | `:t-schnorr:frost-secp256k1` | `org.exploit.tss.frost.secp256k1` | FROST secp256k1 schemes, including Schnorr, BIP340, and Taproot variants. |
| `frost-p256` | `:t-schnorr:frost-p256` | `org.exploit.tss.frost.p256` | FROST P-256 scheme and SHA-256 cipher suite. |
| `t-ecdsa` | `:t-ecdsa` | `org.exploit.tss.gg20` | GG20 threshold ECDSA client, contexts, MtA runners, commitments, integrity checks, and partial signature aggregation. |
| `t-ecies` | `:t-ecies` | `org.exploit.ecies` | Threshold ECIES client, ElGamal KEM, partial decrypt flow, AES-GCM and ChaCha20-Poly1305 ciphers. |
| `xchacha20-poly1305` | `:xchacha20-poly1305` | `org.exploit.crypto.aead` | XChaCha20-Poly1305 AEAD wrapper over libsodium. |
| `zk-spi` | `:zk-spi` | `org.exploit.crypto.zk` | Proof, prover, verifier, statement, and witness interfaces. |
| `zk-dlog` | `:zk-dlog` | `org.exploit.crypto.zk.dlog` | Discrete-log proof utilities: Pedersen commitments, Chaum-Pedersen, and DLEQ. |

## License

[Apache License 2.0](LICENSE.md)
