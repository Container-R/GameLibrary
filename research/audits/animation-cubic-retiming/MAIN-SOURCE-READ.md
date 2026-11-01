# Main source and algebra review: translation-curve retiming

2026-11-01 UTC. Direct GitHub connector reads at KhronosGroup/glTF fixed commit `59ecbdba704206bb656965ab4e202881806066f1`:

- [Specification.adoc Appendix C](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L3979-L4077), lines3979–4077: normalized segment time, duration and cubic formula with duration multiplying outgoing/incoming tangents; quaternion-specific text is read but excluded from the proposed claim.
- [Animation samplers](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L3257-L3293), lines3257–3293: seconds, translation VEC3 float32, input min/max, finite values and nonlinear-time-input limitation.
- [Sampler schema](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/animation.sampler.schema.json), complete file: strictly increasing nonnegative initial times; cubic in/value/out entries. These are one normative source system, not independent implementations.

Read complete current ROLE-ANIM-001 (SHA-256 `d4f2cdadd14ae54a8db0f2930621b03b921adc76876d8f7f7df31b4814b6b0f5`). Existing content concerns expression and character-combination handoff, not interpolation retiming.

Independent main hand check: at u=1/2, h00=h01=1/2, h10=1/8, h11=-1/8. With x0=0, x1=1, b0=2, a1=0, original duration1 gives3/4; duration2 with unchanged tangent gives1; duration2 and b0=1 gives3/4. Equal u compares original t=0.5 with retimed t=1, not equal wall-clock seconds. Algebraically sΔt·(b/s)=Δt·b and likewise for a, so every normalized position is preserved in this ideal translation segment for positive s. This is an original derivation from the formula, not a normative exporter instruction or executed test.

Stored-key retiming and rescaling a playback clock are different operations. The proof does not establish float32 representation, asset metadata validity, full skeletal pose, rotations, nonlinear time warps or character quality. No animation asset, engine playback, image or runtime archive was used.
