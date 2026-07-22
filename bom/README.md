# anvil-bom

Coordinates:

```text
org.exploit.anvil:bom:0.2.0-SNAPSHOT
```

The BOM is a Gradle `java-platform` artifact that constrains every published
Anvil module to the same project version. It contains dependency constraints,
not Java classes.

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")

    implementation "org.exploit.anvil:bigint"
    implementation "org.exploit.anvil:ecc-secp256k1"
    implementation "org.exploit.anvil:paillier"
}
```

Use the BOM when an application depends on more than one Anvil artifact. It
keeps curve modules, threshold modules, proof modules, and shared utilities on
the same release line without repeating the version on each dependency.

## Included Artifacts

The platform constrains:

```text
bigint
util
crypto-spi
ecc-spi
ecc-secp256k1
ecc-ed25519
ecc-p256
paillier
shamir
t-schnorr
frost-ed25519
frost-secp256k1
frost-p256
t-ecdsa
t-ecies
t-mldsa
xchacha20-poly1305
zk-dlog
zk-spi
```

## Publishing

The root build publishes the BOM from `components.javaPlatform` under the same
group and version as the Java modules.
