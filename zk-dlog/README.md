# anvil-zk-dlog

Coordinates:

```text
org.exploit.anvil:zk-dlog:0.2.0-SNAPSHOT
```

Java package:

```text
org.exploit.crypto.zk.dlog
```

`zk-dlog` provides discrete-log proof utilities over the generic `PointOps`
interface: Pedersen commitments, Chaum-Pedersen proofs, and DLEQ proofs.

## Primary API

| Area | Types |
| --- | --- |
| Commitment | `PedersenCommitment` |
| Chaum-Pedersen | `ChaumPedersenInput`, `ChaumPedersenWitness`, `ChaumPedersenStatement`, `ChaumPedersenProof`, `ChaumPedersenProver`, `ChaumPedersenVerifier`, `ChaumPedersenSupport` |
| DLEQ | `DleqInput`, `DleqWitness`, `DleqStatement`, `DleqProof`, `DleqProver`, `DleqVerifier`, `DleqSupport` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0-SNAPSHOT")
    implementation "org.exploit.anvil:zk-dlog"
    implementation "org.exploit.anvil:ecc-secp256k1"
}
```

```java
import org.exploit.crypto.zk.dlog.prover.DleqProver;
import org.exploit.crypto.zk.dlog.verifier.DleqVerifier;

var prover = new DleqProver<>(q, g);
var verifier = new DleqVerifier<>(q, g);

var proof = prover.prove(input);
boolean ok = verifier.verify(proof, statement);
```

## Transcript Inputs

Statements implement `FiatShamirStatement` and carry `additionalData()`.
Support classes define domain separators and challenge construction for each
proof family:

```text
ChaumPedersenProof/v2
DLEQProof/v2
```

## Dependencies

This module depends on `zk-spi`, `ecc-spi`, and `util`. It uses `BigInt` scalar
types through the elliptic-curve interfaces.
