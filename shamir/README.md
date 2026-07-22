# anvil-shamir

Coordinates:

```text
org.exploit.anvil:shamir:0.2.0
```

Java package:

```text
org.exploit.crypto.shamir
```

`shamir` provides Shamir splitting and recovery for elliptic-curve private
scalars over a caller-supplied curve order and generator.

## Primary API

| Type | Purpose |
| --- | --- |
| `ECShamirKeySplitter<P>` | Splits a scalar into threshold shares and recovers a scalar from shares. |
| `ECKeyShare<P>` | Share index, scalar share, and point commitment. |
| `ECKeySplitResult<P>` | Generated share set and global commitment point. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.2.0")
    implementation "org.exploit.anvil:shamir"
    implementation "org.exploit.anvil:ecc-secp256k1"
}
```

```java
import org.exploit.crypto.shamir.ECShamirKeySplitter;
import org.exploit.ecc.secp256k1.params.Secp256k1CurveParams;

var curve = Secp256k1CurveParams.getInstance();
var splitter = new ECShamirKeySplitter<>(
    curve.getCurveOrder(),
    curve.getG(),
    2,
    3
);

var split = splitter.splitKey(secretScalar);
var recovered = splitter.recoverKey(split.shares().subList(0, 2));
```

## Operational Notes

The caller supplies the curve order, generator, threshold, and total peer count.
`ECKeyShare` implements `Destroyable`; destroying a share destroys its scalar
share value.
