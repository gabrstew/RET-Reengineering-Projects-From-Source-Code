#some errors that can be agreed upon by us team memers of ZeroCool

class RETError(Exception):

    """Base class for expected RET errors.

    This should let the CLI distinguish between expected erros and random Python bugs
    """

class AnalysisError(RETError):

    """Raised when an error occurs during analysis."""

class NoPythonFilesError(AnalysisError):

    """Raised when no Python files are found in the project root."""

class ReporterError(RETError):

    """Raised when an error occurs during the final report."""