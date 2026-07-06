# anvil-crypto-spi

Coordinates:

```text
org.exploit.anvil:crypto-spi:0.1.2
```

Java packages:

```text
org.exploit.crypto.spi
```

`crypto-spi` defines protocol-agnostic asymmetric cryptography interfaces shared
by concrete signature and key modules.

## Primary API

| Area | Types |
| --- | --- |
| Keys | `Key`, `PrivateKey`, `PublicKey`, `KeyPair` |
| Factories | `AsymmetricKeyFactory` |
| Signatures | `Signature` |
| Signing | `AsymmetricSigner`, `AsymmetricVerifier` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:crypto-spi"
}
```

## Contracts

Keys and signatures expose their canonical encoded form through `encode()`.
Private keys and key pairs implement `Destroyable`; key pair destruction
delegates to the private key by default.
