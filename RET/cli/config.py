#import the dataclass, fields, and path

from dataclasses import dataclass, field
from logging import root
from pathlib import Path
#creates a dataclass that has frozen attributes to the modification of information required for running
#slots are used to optimize the memory usage of the dataclass
@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    #defines the folder that RET should analyze
    project_root: Path
    #the directories that the analyzers FileScanner should ignore
    excluded_dirs: tuple[str, ...] = ()
    #sets the suffix to be looked for as ".py" files only, and it cannot be changed
    target_suffixes: tuple[str, ...] = field(default=(".py",), init=False)

    def __post_init__(self) -> None:
        #defense validation check. CLI should also check for this in the main entry but better safe than sorry
        root = self.project_root.expanduser().resolve()

        if not root.exists():
            raise ValueError(f"Project root {root} does not exist.")

        if not root.is_dir():
            raise ValueError(f"Project root {root} is not a directory.")

        #clean duplicate/emtpy exclusions while preserving their order
        clean_exclusions: list[str] = []
        seen: set[str] = set()
        #loop through the excluded directories and clean them up
        for excluded in self.excluded_dirs:
            cleaned = excluded.strip()
            # if they arent cleaned then keep looping
            if not cleaned:
                continue
            #if the cleaned isn't seen, then add it to the clean_exclusions and seen set
            if cleaned not in seen:
                clean_exclusions.append(cleaned)
                seen.add(cleaned)
        #we have to use object.__setattr__ because the dataclass is frozen, so we cannot modify the attributes directly
        object.__setattr__(self, "project_root", root)
        object.__setattr__(self, "excluded_dirs", tuple(clean_exclusions))
