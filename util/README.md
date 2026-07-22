# anvil-util

Coordinates:

```text
org.exploit.anvil:util:0.2.0
```

Java package:

```text
org.exploit.anvil.util
```

`util` contains shared helper code used by Anvil modules that need stable byte
composition and digest creation without duplicating local utility classes.

## Primary API

| Type | Methods |
| --- | --- |
| `Bytes` | `concat(List<byte[]>)`, `concat(byte[]...)`, `encode(byte[]...)` |
| `Digests` | `sha256(byte[])`, `sha512(byte[])`, `digest(String, byte[])`, `newDigest(String)` |

`Bytes.encode(...)` writes each byte array as a 4-byte big-endian length followed
by the raw bytes. This is used for transcript-style domain-separated inputs
where concatenation alone is ambiguous.

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0")
    implementation "org.exploit.anvil:util"
}
```

```java
import org.exploit.anvil.util.Bytes;
import org.exploit.anvil.util.Digests;

byte[] transcript = Bytes.encode(sessionId, participantId, publicKey);
byte[] challenge = Digests.sha256(transcript);
```

## Dependency Model

This module has no Anvil dependencies. Other Anvil modules depend on it as a
normal Gradle/Maven dependency; it is not embedded or shaded into those
artifacts.
