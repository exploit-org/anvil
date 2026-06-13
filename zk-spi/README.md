# anvil-zk-spi

Coordinates:

```text
org.exploit.anvil:zk-spi:0.1.2
```

Java package:

```text
org.exploit.crypto.zk
```

`zk-spi` defines the proof interfaces shared by Anvil zero-knowledge modules.
It contains no proof implementation.

## Primary API

| Type | Purpose |
| --- | --- |
| `ZKProof` | Marker interface for proof values. |
| `ZKStatement` | Marker interface for public statement values. |
| `FiatShamirStatement` | Statement interface carrying `additionalData()`. |
| `ZKWitness` | Marker interface for private witness values. |
| `ZKProver<P, I>` | Prover interface with `prove(I input)`. |
| `ZKVerifier<P, S>` | Verifier interface with `verify(P proof, S statement)`. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:zk-spi"
}
```

```java
import org.exploit.crypto.zk.proof.ZKProof;
import org.exploit.crypto.zk.prover.ZKProver;
import org.exploit.crypto.zk.statement.ZKStatement;
import org.exploit.crypto.zk.verifier.ZKVerifier;

record Proof(byte[] value) implements ZKProof {}
record Statement(byte[] value) implements ZKStatement {}

ZKProver<Proof, Statement> prover = input -> new Proof(input.value());
ZKVerifier<Proof, Statement> verifier = (proof, statement) -> true;
```

## Dependency Model

This module has no implementation dependencies. Proof modules such as `zk-dlog`
and Paillier proof packages implement these interfaces.
