import argparse
import sys

from pathlib import Path
from typing import Any, Protocol, Sequence, TextIO
from RET.cli.config import AnalysisConfig
from RET.cli.errors import (NoPythonFilesError, ReporterError, AnalysisError)

#Protocol class to define the analyze function, what it should take (AnalysisConfig) and what it should return(ProjectModel)
class AnalyzerProtocol(Protocol):
    def analyze(self, config: AnalysisConfig) -> ProjectModel:
        ...

#Protocol class to define the report function, what it should take (ProjectModel) and what it should return(Path to the report file)
class ReporterProtocol(Protocol):
    def report(self, project_model: Any,) -> Path:
        ...

#Exit codes for CLI success and errors

EXIT_SUCCESS = 0
#failed analysis or report generation
EXIT_FAILURE = 1
#ivalid command line input
EXIT_USAGE_ERROR = 2
#user interrupt using ctrl+c
EXIT_INTERRUPT = 130

#buidling the parser for the CLI parser

def build_parser() -> argparse.ArgumentParser:
    #this should create the CLI grammar for the ret. this include the prog, commands, and posiitonal arrgument
    #these arguments will be used to create the AnalysisConfig object that will be passed to the analyzers and reporters

    parser = argparse.ArgumentParser(
        prog="ret", #starts the CLI with ret to begin running commands
        description="RET - Reeingineering Toolkit for static analysis of Python codebases.",
    )  
    # creates a command that will be used to analyze a Python project
    subparsers = parser.add_subparsers(dest="command", required=True),
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a Python project."),
    #positiona argument that will be used to specify the path to the Python project that RET should analyze
    analyze_parser.add_argument("project_path", help="Path to the Pythin project RET should analyze."),

    analyze_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="DIRECTORY",
        help="Directories to exclude from analysis. Can be specified multiple times."),

    return parser


class RetCLI:
    #CLI controller class for handling CLI actions

    def __init__( #main intializations
            self,
            analyzer: AnalyzerProtocol,
            reporter: ReporterProtocol,
            stdout: TextIO | None = None,
            stderr: TextIO | None = None,
    ) -> None:
        #sets the analyzer and reporter to be used by the CLI
        self.analyzer = analyzer 
        self.reporter = reporter

        #allow for stdout and stderr to be repalced for testing purposes, but default to sys.stdout and sys.stderr
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

        #build the parser for the CLI
        self.parser = build_parser()


# Main Entry Point for CLI

def run(self, argv: Sequence[str] | None = None) -> int: #takes args as input and returns the exit codes
    try:
        args = self.parser.parse_args(argv) #parse the args using the parser built in the build_parser function

        if args.command == "analyze":
            return self._run_analysis(args)
        self.print_error(f"Unknown command: {args.command}")
        return EXIT_USAGE_ERROR
    except KeyboardInterrupt:
    #user pressed ctrl+c
        self._print_error("\nRET anakkysis interrupted by user.")
        return EXIT_INTERRUPT

#create the command to run the analysis
def _run_analysis(self, args: argparse.Namespace) -> int:
    #handles the analysis command, creates the AnalysisConfig object and passes it to the analyzer and reporter
    try:
        #first we do a validation, the first of two (the other being in config)
        project_root = self._validate_project_path(args.project_path)
    except ValueError as error:
        self._print_error(f"Error: {error}")
        return EXIT_USAGE_ERROR

    self._print("Starting Analysis Configuration...")

    try:
        config = AnalysisConfig(project_root=project_root, excluded_dirs=tuple(args.exclude))
    except ValueError as error:
        self._print_error(f"Error creating analysis configuration: {error}")
        return EXIT_USAGE_ERROR

    self._print(f"Analyzing Project: {config.project_root}")
    try:
        project_model = self.analyzer.analyze(config)
    except NoPythonFilesError as error:
        self._print_error(f"Analysis failed: {error}")
        return EXIT_FAILURE
    except AnalysisError as error:
        self._print_error(f"Analysis failed: {error}")
        return EXIT_FAILURE
    self._print("Analysis is complete.")

    
    self.print("Generating Report...")
    try:
        report_path =  self.reporter.generate_report(project_model)
    except ReporterError as error:
        self._print_error(f"Report generation failed: {error}")
        return EXIT_FAILURE

    self._print("")
    self.print("RET completed successfully")
    self.prrint(f"Report generated at: {report_path}")
    return EXIT_SUCCESS

#create the previously called _validate_project_path function to validate the project path provided by the user
@staticmethod
def _validate_project_path(project_path: str) -> Path:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"Project path does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"Project path is not a directory: {path}")
    return path

#function helpers for printing and errors

#this is made for testing purposes, so that we can capture the output of the CLI and assert on it in tests
def _print(self, message: str) -> None:
    print(message, file= self.stdout)

def _print_error(self, message: str) -> None:
    print(message, file= self.stderr)


#Actual entry point for the CLI

def main(argv: Sequence[str] | None = None,) -> int:
    #Grabs the RET Analyzer and Reporter from the actual files and sets them to be the protocols we defined earlier, and runs the CLI
    from ret.analyzer.ret_analyzer import RETAnalyzer
    from ret.reporter.ret_reporter import RETReporter

    analyzer = RETAnalyzer
    reporter = RETReporter

    cli = RetCLI(analyzer=analyzer, reporter=reporter,)
    return cli.run(argv)


