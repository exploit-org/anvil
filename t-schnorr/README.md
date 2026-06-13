# anvil-t-schnorr

Coordinates:

```text
org.exploit.anvil:t-schnorr:0.1.2
```

Java package:

```text
org.exploit.tss.frost
```

`t-schnorr` contains the curve-independent FROST core: contexts, commitment
preprocessing, partial signature computation, and signature aggregation. Curve
specific schemes live in the nested modules.

## Primary API

| Area | Types |
| --- | --- |
| Client | `FrostClient` |
| Context | `FrostContext`, `CryptoContext`, `CommitmentContext`, `SignatureAggregatorContext` |
| In-memory contexts | `InMemoryCryptoContext`, `InMemoryCommitmentContext`, `InMemorySignatureAggregatorContext` |
| Preprocessing | `FrostPreProcessor`, `CommitmentPair`, `ParticipantCommitment` |
| Signing | `FrostPartialSignatureClient`, `SignaturePartAggregator` |
| Schemes | `FrostScheme`, `AbstractFrostScheme`, `FrostCipherSuite` |
| Utilities | `Polynomials`, `Sum`, `Endian`, `FrostPreProcessorSupport` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:t-schnorr"
    implementation "org.exploit.anvil:frost-secp256k1"
}
```

```java
import org.exploit.tss.frost.FrostClient;
import org.exploit.tss.frost.secp256k1.FrostSecp256k1Scheme;

var client = new FrostClient<>(
    sessionId,
    frostContext,
    new FrostSecp256k1Scheme()
);

var commitment = client.preProcessor().generateCommitment(opId);
client.signature().storeCommitment(peerId, opId, peerCommitment);
var z = client.signature().computeZ(opId);
client.aggregator().storeZ(peerId, opId, z);
var signature = client.aggregator().computeSignature(opId);
```

## Context Model

The core module does not own networking or durable storage. Protocol messages
are represented as Java values and stored through context interfaces. The
provided in-memory contexts are useful for local sessions and tests. Other
integrations can implement the same interfaces against their own transport and
state layer.

## Curve Modules

Use one of the curve-specific modules for concrete signature construction:

```text
org.exploit.anvil:frost-ed25519
org.exploit.anvil:frost-secp256k1
org.exploit.anvil:frost-p256
```
