# Integrator primary-source gate

Accessed 2026-10-31. GitHub commits/main resolved to `59ecbdba704206bb656965ab4e202881806066f1`, committer date 2026-10-30T15:21:59Z. Read immutable Specification.adoc sections Buffer Views, Accessors/Accessing Data from Buffer Views, Vertex Attributes, Topology and Connectivity; also accessor.schema.json, bufferView.schema.json and mesh.primitive.schema.json from specification/2.0/schema. No Khronos validator or graphics API executed.

Required distinctions: buffer span vs accessor typed elements; offset relative to view plus view offset relative to buffer; step is stride, not necessarily element width. Per-view last-element bound includes one final element, not an extra whole stride. Vertex attributes share index identity; positions and normals cannot have unrelated index streams in one primitive. Valid byte interpretation still does not prove the artist-intended topology. POSITION bounds, finite floats, normalized normals and same attribute counts matter to this bounded fixture. Schema syntax constraints alone do not validate actual binary values or intended geometry.

Primary URLs use https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc and its schema siblings. The spec is authoritative format evidence, not independent engine-import observation. Original artifact and literal oracle supply a distinct empirical layer, still CPU-only.

Attempted Blender5.0 manual public page returned tool402; not read, not cited, no access workaround attempted. Earlier search snippets are discovery leads only.
