# SwarmStack command language

The toolkit separates project management from controls for a running agent team.

## Language

**Swarm controls**:
The user-facing interface for team direction, availability, progress, blockers, pause and resume, named /swarm.

**Swarm availability**:
The user's declared day or night mode, indicating whether the swarm should expect replies. It is separate from work priority, permissions and whether the goal is paused.

**Project commands**:
The interface for project setup, installed toolkit state, installation health, reviewed updates and guidance, named /swarmstack. Each command has a separate procedure.

**Standalone skill**:
An independently invoked workflow such as /grill-with-docs or /code-review, outside the two command interfaces.

**Installation**:
Project-local skill and reusable toolkit files made available to a host, with a pinned source revision and an unconfigured draft.

**Setup**:
The project-specific requirements, instructions, configuration and permissions agreed after installation. Installation alone is not setup.
