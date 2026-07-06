# anvil-t-ecdsa

Coordinates:

```text
org.exploit.anvil:t-ecdsa:0.2.0-SNAPSHOT
```

Java package:

```text
org.exploit.tss.gg20
```

`t-ecdsa` contains the GG20 threshold ECDSA client and supporting protocol
components: MtA runners, commitments, Chaum-Pedersen proof handling, integrity
checks, partial signature calculation, and signature aggregation.

## Primary API

| Area | Types |
| --- | --- |
| Client | `GG20Client` |
| Context | `GG20Context`, `CryptoContext`, `InitContext`, `MtAContext`, `SignatureContext`, `IntegrityContext`, `SignatureAggregatorContext` |
| In-memory contexts | `InMemoryCryptoContext`, `InMemoryInitContext`, `InMemoryMtAInitiatorContext`, `InMemoryMtARespondentContext`, `InMemorySignatureContext`, `InMemoryIntegrityContext`, `InMemoryAggregatorContext` |
| Commitments | `GG20CommitmentGenerator`, `CommitmentResult`, `GammaCommitment`, `ChaumPedersenCommitment`, `ChaumPedersenCommitmentWithValue` |
| MtA | `MtAProtocolRunner`, `MtAInitiatorProtocolRunner`, `MtARespondentProtocolRunner` |
| Signing | `PartialSignatureCalculator`, `SignaturePartAggregator`, `SignatureBuilder` |
| Integrity | `IntegrityChecker`, `IdentifiableAbortException` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")
    implementation "org.exploit.anvil:t-ecdsa"
    implementation "org.exploit.anvil:ecc-secp256k1"
}
```

```java
import org.exploit.tss.gg20.GG20Client;

try (var client = new GG20Client<>(
    executor,
    context,
    commitmentGenerator,
    signatureBuilder
)) {
    client.init();
    var mta = client.mta();
    var partial = client.signature().computePartialS();
    var signature = client.aggregator().calculateSignature();
}
```

## Integration Model

The module exposes protocol state through context interfaces and Java model
types. It does not define a network transport. Integrations are expected to
persist and exchange the message objects required by each GG20 phase.

`IdentifiableAbortException` carries a participant id for aborts where the
code can identify the peer.

## Dependencies

This module depends on `ecc-spi`, `paillier`, `bigint`, and `zk-dlog`.
Concrete curve support is supplied by curve modules such as `ecc-secp256k1` or
`ecc-p256`.
