# Queue metadata recovery guard integration

This corrective engineering unit responds to an actual queue typo: TASK-0048 used RENDER rather than the established GFX taxonomy ID. Article validation did not inspect queue references. The typo was corrected in the shader publication; this unit adds a reusable read-only guard to detect recurrence. Historical author output retains the old failure; it does not describe the current corrected state.

Production tool and tests: [scripts/queue at the preserved historical revision](https://github.com/Container-R/GameLibrary/blob/cc99dab476ab93db828afed227eb88b93574fcde/scripts/queue/README.md). The original author/reviewer copies and observed outputs remain here. Runtime code is byte-identical to reviewed version935abf2b7a469b7188f0c036c15e41218f717e479d6b6c6bf3be6031218009dc.

Integration ran 15 unittest methods normally and with -O (9 author+6 reviewer), plus current queue checks in both modes. Initial migration declares12 paths across tasks0045–0049, preserving all old expected_artifact prose and other tasks. Seven are the prior reviewed suggestions, two now reference the published shader article/fixture, and three reference the new guard/tests. Existing directories are valid declared locations, not proof of their contents. No artifact coverage is inferred for older unannotated tasks. Current exact counts are in integration/queue.json; later receipts may add tasks.

The prior48-task rejection/in-memory correction, reviewer49-task/zero-path state and integrator49-task/12-path migration are distinct observations, not contradictory reports. The coverage gate is historical at25articles; the shader publication subsequently raised26. No article/runtime research claimed for this guard, and no new engine or compiler process executed. Fail-closed checks are not full schema, file-content, malicious-filesystem or concurrency validation.

Navigation maintenance note: the tool link now pins the historical pre-migration tree. This link-only edit does not rerun or update the observations above; current tools are under the maintenance directory.
