import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, makeUnitImportDetector } from './refNotOwn.js';

// REFNOTOWN (structural) — ui-memo-view (U6) is FROZEN. Its fetchSeam / StructuralGuard / by-construction /
// testid-lint conventions are MIRRORED by ui-history, NEVER imported: the sibling UI units stay
// decoupled, and the structural consistency between them comes from the shared WIRE-1 contract and
// the shared ui-shell primitives, not from cross-unit coupling.
const findImport = makeUnitImportDetector('memoView');

describe('REFNOTOWN (structural) — ui-memo-view (U6) is mirrored, never imported', () => {
  it('no production history module imports from src/memoView', () => {
    expect(productionFiles().filter((f) => findImport(readSource(f)))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findImport("import { x } from '../../memoView/something.js';")).toBe(true);
    expect(findImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
  });
});
