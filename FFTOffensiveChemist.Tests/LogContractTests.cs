using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;

namespace FFTOffensiveChemist.Tests
{
    /// <summary>
    /// The build-voice contract gate (docs/LOGGING.md + tools/lib/say.py), the data-only
    /// adaptation of the sibling mods' logging contract: this repo has no runtime, so the
    /// contract governs the BUILD pipeline's output instead.
    ///
    /// A. No bare print( in tools/ Python outside say.py itself: every line the tools emit
    ///    must go through say/warn/fail so it carries the [Offensive Chemist] [verb] tag.
    /// B. The closed verb set in tools/lib/say.py matches the glossary table in
    ///    docs/LOGGING.md one-for-one and in order, so doc and code cannot drift.
    /// C. Dash rules: no em dash anywhere in tools/ or docs/LOGGING.md; no " -- " separator
    ///    in docs/LOGGING.md or on any tools/ line that calls say(/warn(/fail( (log text
    ///    uses colons, commas, and parentheses; " -- " remains fine in ordinary comments).
    /// </summary>
    public class LogContractTests
    {
        private static string RepoRoot()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir is not null)
            {
                if (File.Exists(Path.Combine(dir.FullName, "docs", "TODO.md")) &&
                    File.Exists(Path.Combine(dir.FullName, "data", "grenades.json")))
                    return dir.FullName;
                dir = dir.Parent;
            }
            throw new FileNotFoundException("repo root (docs/TODO.md + data/grenades.json) not found above the test bin dir");
        }

        private static string SayPyPath() => Path.Combine(RepoRoot(), "tools", "lib", "say.py");
        private static string LoggingMdPath() => Path.Combine(RepoRoot(), "docs", "LOGGING.md");

        /// <summary>Every hand-written Python file under tools/ (skips __pycache__).</summary>
        private static List<string> ToolPyFiles() =>
            Directory.EnumerateFiles(Path.Combine(RepoRoot(), "tools"), "*.py", SearchOption.AllDirectories)
                .Where(p => !p.Contains("__pycache__"))
                .ToList();

        // A print CALL, not the word in prose: no identifier char or '.' immediately before it
        // (so "pprint(" and "self.print(" do not match) and an opening paren after.
        private static readonly Regex BarePrintRegex = new(@"(?<![\w.])print\s*\(", RegexOptions.Compiled);

        // A say-facade CALL SITE (the lines whose text becomes emitted log output).
        private static readonly Regex SayCallRegex = new(@"(?<![\w.])(say|warn|fail)\s*\(", RegexOptions.Compiled);

        // The closed verb tuple in say.py: VERBS = ("gate", "generate", ...)
        private static readonly Regex VerbsTupleRegex = new(@"VERBS\s*=\s*\(([^)]*)\)", RegexOptions.Compiled);

        // A glossary table row in docs/LOGGING.md: | `[gate]` | ... |
        private static readonly Regex GlossaryRowRegex = new(@"^\|\s*`\[(\w+)\]`", RegexOptions.Compiled);

        // The em dash character lives here as an escape, never a literal: this repo bans the
        // literal glyph repo-wide, and this test is part of what enforces the ban.
        private static readonly char EmDash = '—';

        // --- A. No bare print() in tools/ outside say.py ---

        [Fact]
        public void No_bare_print_in_tools_python_outside_say_py()
        {
            var violations = new List<string>();
            foreach (var file in ToolPyFiles())
            {
                if (Path.GetFileName(file) == "say.py") continue;
                int lineNo = 0;
                foreach (var line in File.ReadAllLines(file))
                {
                    lineNo++;
                    if (line.TrimStart().StartsWith("#")) continue;
                    if (BarePrintRegex.IsMatch(line))
                        violations.Add($"{Path.GetFileName(file)}:{lineNo}: {line.Trim()}");
                }
            }
            Assert.True(violations.Count == 0,
                "Bare print( calls in tools/ (route them through tools/lib/say.py):\n" + string.Join("\n", violations));
        }

        // --- B. Verb glossary pinned: say.py tuple == docs/LOGGING.md table, in order ---

        [Fact]
        public void Verb_set_in_say_py_matches_the_LOGGING_md_glossary_one_for_one()
        {
            Assert.True(File.Exists(SayPyPath()), "tools/lib/say.py does not exist");
            Assert.True(File.Exists(LoggingMdPath()), "docs/LOGGING.md does not exist");

            var tupleMatch = VerbsTupleRegex.Match(File.ReadAllText(SayPyPath()));
            Assert.True(tupleMatch.Success, "tools/lib/say.py has no VERBS = (...) tuple to pin");
            var sayVerbs = Regex.Matches(tupleMatch.Groups[1].Value, @"""(\w+)""")
                .Select(m => m.Groups[1].Value).ToList();

            var docVerbs = File.ReadAllLines(LoggingMdPath())
                .Select(l => GlossaryRowRegex.Match(l))
                .Where(m => m.Success)
                .Select(m => m.Groups[1].Value).ToList();

            Assert.True(sayVerbs.Count > 0, "no verbs parsed out of say.py's VERBS tuple");
            Assert.True(docVerbs.Count > 0, "no glossary rows (| `[verb]` | ...) parsed out of docs/LOGGING.md");
            Assert.Equal(sayVerbs, docVerbs);
        }

        [Fact]
        public void The_verb_set_is_the_agreed_closed_eight()
        {
            Assert.True(File.Exists(SayPyPath()), "tools/lib/say.py does not exist");
            var tupleMatch = VerbsTupleRegex.Match(File.ReadAllText(SayPyPath()));
            Assert.True(tupleMatch.Success, "tools/lib/say.py has no VERBS = (...) tuple to pin");
            var sayVerbs = Regex.Matches(tupleMatch.Groups[1].Value, @"""(\w+)""")
                .Select(m => m.Groups[1].Value).ToList();
            Assert.Equal(
                new[] { "gate", "generate", "names", "abilities", "icons", "test", "deploy", "package" },
                sayVerbs);
        }

        // --- C. Dash rules over the build voice ---

        [Fact]
        public void No_em_dash_in_tools_python_or_LOGGING_md()
        {
            var violations = new List<string>();
            var files = ToolPyFiles();
            files.Add(Path.Combine(RepoRoot(), "tools", "pipeline.ps1"));
            if (File.Exists(LoggingMdPath())) files.Add(LoggingMdPath());
            else violations.Add("docs/LOGGING.md: file does not exist");

            foreach (var file in files)
            {
                int lineNo = 0;
                foreach (var line in File.ReadAllLines(file))
                {
                    lineNo++;
                    if (line.Contains(EmDash))
                        violations.Add($"{Path.GetFileName(file)}:{lineNo}: {line.Trim()}");
                }
            }
            Assert.True(violations.Count == 0, "Em dash found:\n" + string.Join("\n", violations));
        }

        [Fact]
        public void No_double_dash_separator_in_LOGGING_md_or_on_say_call_lines()
        {
            var violations = new List<string>();

            if (File.Exists(LoggingMdPath()))
            {
                int lineNo = 0;
                foreach (var line in File.ReadAllLines(LoggingMdPath()))
                {
                    lineNo++;
                    if (line.Contains(" -- "))
                        violations.Add($"LOGGING.md:{lineNo}: {line.Trim()}");
                }
            }
            else
            {
                violations.Add("docs/LOGGING.md: file does not exist");
            }

            foreach (var file in ToolPyFiles())
            {
                if (Path.GetFileName(file) == "say.py") continue;
                int lineNo = 0;
                foreach (var line in File.ReadAllLines(file))
                {
                    lineNo++;
                    if (SayCallRegex.IsMatch(line) && line.Contains(" -- "))
                        violations.Add($"{Path.GetFileName(file)}:{lineNo}: {line.Trim()}");
                }
            }
            Assert.True(violations.Count == 0,
                "Double-dash separator in emitted log text or LOGGING.md (use colons, commas, parentheses):\n"
                + string.Join("\n", violations));
        }
    }
}
