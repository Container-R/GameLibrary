# Main source read: FMOD observation layers

2026-11-01 UTC. The main integrator directly read the FMOD Engine and Studio manuals' relevant body sections and footers, all self-identifying as 2.04.00 (2026-09-29). This is documentation identity, not an installed SDK or release-date authentication.

- Core API Managing Resources §§9.1.5–9.1.7 distinguishes total Core channel capacity, real mixing capacity, permanently stolen handles, virtual-to-real content position and the Studio/Core interaction. Its explicit example allows `EventInstance::isVirtual == false` with some or all underlying Channels virtual. Main also read the priority and nested-event caveats, without adopting numeric voice-budget recommendations.
- Studio Advanced Topics §§16.4.1–16.4.2 separates stop/reject/virtualize policies and states that virtualization preserves advancing playback and internal behavior. The broad Core guide heading about stealing must not erase the Studio mode distinctions.
- EventInstance API `isVirtual` states its event-polyphony observation scope. It is not a check that every underlying Channel, route, device or listener has received the required information.

These pages are ordinary accessible original FMOD documentation, not a workaround for inaccessible Audiokinetic material. No Wwise policy equivalence follows. No middleware installation, sound playback, listening, device query or execution was performed. Existing audio lifecycle model results remain unchanged.

Proposed engineering contribution: a field-level observation/claim decision table and an explicitly unexecuted opening/tail cue scenario. Do not infer that a later nonvirtual observation proves an earlier information-bearing interval was delivered, or that replaying a stale cue is always correct. Any prototype would need independently specified audio and semantic acceptance rather than a Boolean proxy.
