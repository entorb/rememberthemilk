#!/bin/sh
set -e
cd "$(dirname "$0")/.."

# Download SonarCloud open issues as JSON.

api=https://sonarcloud.io/api/issues/search
component=$(sed -n 's/^sonar\.projectKey=//p' sonar-project.properties .sonarcloud.properties 2>/dev/null | head -n1)
[ -n "$component" ] || {
  echo "sonar.projectKey missing in sonar-project.properties / .sonarcloud.properties" >&2
  exit 1
}

mkdir -p tmp
out=tmp/sonar.json

# API caps a page at 500 issues; fetch pages until all are collected.
# shortcut: SonarCloud refuses p*ps > 10000, split by rule/severity if ever needed.
page=1
echo '{"total":0,"issues":[]}' >"$out"
while :; do
  curl -sS "$api?componentKeys=$component&resolved=false&ps=500&p=$page" >"$out.page"
  jq -s '{total: .[1].total, issues: (.[0].issues + .[1].issues)}' "$out" "$out.page" >"$out.tmp" && mv "$out.tmp" "$out"
  [ "$(jq '.issues | length' "$out")" -ge "$(jq -r '.total' "$out")" ] && break
  [ "$(jq '.issues | length' "$out.page")" -eq 0 ] && break
  page=$((page + 1))
done
rm -f "$out.page"

# Reduce to the fields an AI needs to fix each finding (file/line/message/flows).
jq '{
  total,
  issues: [ .issues[] | {
    file: (.component | sub("^[^:]*:"; "")),
    line: .textRange.startLine,
    startOffset: .textRange.startOffset,
    endOffset: .textRange.endOffset,
    rule, severity, type, message
  } ]
}' "$out" >"$out.tmp" && mv "$out.tmp" "$out"

echo "Wrote $out ($(jq '.issues | length' "$out") issues, SonarQube total $(jq -r '.total' "$out"))."

echo "Prompt:"
echo "fix tmp/sonar.json findings, update AGENTS.md to prevent in future, where it makes sense"
