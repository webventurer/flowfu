export const GITIGNORE_BEGIN = "# >>> stride (auto-managed, do not edit) >>>";
export const GITIGNORE_END = "# <<< stride <<<";

export function buildSection(entries) {
  return [GITIGNORE_BEGIN, ...entries, GITIGNORE_END].join("\n");
}

export function removeSection(content) {
  const bounds = findSectionBounds(content);
  if (!bounds) return content;
  const { before, after } = splitAroundSection(content, bounds);
  return joinOutsideSection(before, after);
}

function findSectionBounds(content) {
  const beginIdx = content.indexOf(GITIGNORE_BEGIN);
  if (beginIdx === -1) return null;
  const endIdx = content.indexOf(GITIGNORE_END, beginIdx);
  if (endIdx === -1) return null;
  return { beginIdx, sectionEnd: lineAfter(content, endIdx) };
}

function lineAfter(content, idx) {
  const newline = content.indexOf("\n", idx);
  return newline === -1 ? content.length : newline + 1;
}

function splitAroundSection(content, { beginIdx, sectionEnd }) {
  return {
    before: content.slice(0, beginIdx).replace(/\n+$/, ""),
    after: content.slice(sectionEnd).replace(/^\n+/, ""),
  };
}

function joinOutsideSection(before, after) {
  if (!before && !after) return "";
  if (!before) return after;
  if (!after) return `${before}\n`;
  return `${before}\n\n${after}`;
}
