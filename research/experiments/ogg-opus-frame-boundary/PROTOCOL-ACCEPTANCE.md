# Protocol acceptance before implementation

2026-10-31T23:21:02Z. Main integrator read the full protocol and accepted its finite scope following independent review.

- Immutable protocol SHA256: 4024d6fda4d3533eeca3e124d79c398cae1ec540d143da7ef18b6fb0ba27db5e
- Independent protocol review: da0686a2edbe7eed244fda00f98577965aa6ea9a0940a7d4cb85e5b46226facd
- Independent source review: c6090d099970d90a2412dff08671d6d3ae632e8cfe1be7d8a6dcac52f08bdc46
- Main source read: 1b119f6a8a5e2c2b2d3bed77f6f12cb3dd9cb855597f7c7ef735cafc77b3b92b

Implementation and pure stdlib tests are now allowed in the draft directory. No encoder, decoder or media-native invocation is accepted by this record: that requires separate reviewed-code acceptance. Preserve negative test evidence and keep source files/imports inert. Source manifests include consumer and tests as well as runner/reader/generator/isolation helper. Explicit type checks and ordinary conditional failures must remain effective under optimized Python. The existing article and old fixture remain unchanged until publication review.
