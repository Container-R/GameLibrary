# Independent finite LittleCMS ABI feasibility review

2026-11-01 00:44 UTC. Accepted ABI-GATE.md SHA256 `5be2508747c93e6c67fbcd3199fea7f5b9e9c96a0155048715b1d412ecfc2a71` for protocol drafting only. No native library load/import, C call, runtime version query, profile construction, transform or numerical experiment.

## Direct pinned-source checks

Independently fetched original Little-CMS commit `b76633e60c8387a77268fb3359277ca25b5fd75c` files via GitHub connector: include/lcms2.h, src/cmsvirt.c, src/cmspack.c, src/cmsgamma.c, src/cmswtpnt.c and src/cmsopt.c. Read the gate's selected type/signature, constructor/curve, buffer-packing and optimization ranges, not the entire engine.

- Header declares double float64, uint32 format/count fields, opaque profile/transform handles, C int cmsBool, xyY of three doubles and a three-xyY primary structure. The proposed struct field order and sizes are consistent with the intended ABI. TYPE_RGB_DBL is float flag + PT_RGB + three channels + bytesfield0: `0x440018`; the zero bytes field encodes double storage, not zero-length channels. Relative intent1 and NOCACHE/NOOPTIMIZE0x0140 are coherent.
- Selected non-vararg function bindings distinguish pointer-return constructors, void transforms/deletion/free/error-handler installation and int close/version returns. cmsDoTransform's final argument is a pixel count. One shared gamma pointer supplied three times must be freed once, with transforms destroyed before profiles. Error callback lifetime must span all creation, transforms and cleanup.
- cmsvirt.c's built-in sRGB uses the stated D65 and Rec709 primary coordinates and type4 transfer parameters. The candidate linear profile uses the same coordinate tuple with gamma1; both constructor paths set v4.4 display-RGB/XYZ profiles. Constructor source writes D50 media white/adaptation data; cmswtpnt.c applies D50 adaptation to colorants. Same device coordinates do not mean no internal PCS/adaptation.
- cmspack.c explicitly narrows external double input to float working values and expands float output to double storage. No end-to-end double precision guarantee follows. cmsopt.c performs trivial preprocessing before the NOOPTIMIZE check; the gate correctly avoids claiming no simplification at all.
- cmsgamma.c supports the sRGB type4/inverse and gamma-builder path. An independent W3C-based transfer oracle remains preferable to reproducing this implementation as its own expected answer.

Immutable source base: https://github.com/mm2/Little-CMS/tree/b76633e60c8387a77268fb3359277ca25b5fd75c . This comparison is not proof that the selected installed file was built from that commit.

## Acceptance policy and remaining protocol details

The unequal RGB128/64/192 candidate, alpha128/255 over opaque black and alpha1 control is narrow and more discriminating than neutral gray. It still does not validate a general ICC implementation, gamut/primaries accuracy or display appearance. Host code performs alpha arithmetic; only RGB conversion is delegated to LittleCMS. The alpha scalar must not enter the transfer transform.

Normalized absolute1e-4 is a defensible **preselected finite acceptance threshold**, not a sourced library-wide error bound. Float intermediates justify allowing nonzero discrepancy but do not mathematically establish this particular bound. Protocol must freeze independent reference literals, each comparison point (forward, host-composite, reverse, opaque control), quantization/rounding and sufficient distance from the wrong-domain result and rounding thresholds before observing native data. A tolerance failure must stop, not trigger profile/flag/tolerance searches.

Before code, specify pointer size/alignment and C int width as well as uint32/double and struct offsets; reject unsupported ABI. Callback must record errors without raising through C, remain strongly referenced until all cleanup ends, and make any recorded CMM diagnostic fail the finite invocation. Null returns must prevent subsequent uses while still cleaning up previously acquired handles. A sentinel output plus finiteness checks distinguishes unwritten data from valid conversion. These are implementation requirements, not extra native cases.

Load the single resolved vendored absolute path/hash, never generic system fallback. Runtime mapping records must be limited to that selected library; mapped path/hash/self-report does not authenticate upstream provenance or prove all dependency resolution. Direct ctypes on this file is not Pillow ImageCms execution. No arbitrary profile parsing/serialization, image assets, plugins, installation or general ICC framework is warranted.

No material ABI-source blocker remains for a small frozen protocol. Exact code and native execution remain separate approval gates.
