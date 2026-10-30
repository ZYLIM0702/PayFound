import { useEffect, useMemo, useRef, type Ref } from 'react';
import { AgGridReact, type AgGridReactProps } from 'ag-grid-react';
import type { ColDef, GridApi } from 'ag-grid-community';
import { pfGridTheme } from './grid-setup';

export { pfGridTheme };

/** Phones show the first few data columns (pinned, selection and action columns stay); the grid scrolls sideways inside its box. */
const PHONE_COLUMNS = 3;
const hiddenByUs = new WeakMap<GridApi, string[]>();
function narrowColumns(api: GridApi) {
  const phone = window.matchMedia('(max-width: 767px)').matches;
  const before = hiddenByUs.get(api) || [];
  if (before.length) api.setColumnsVisible(before, true);
  hiddenByUs.set(api, []);
  // A 300px pinned action column would leave no room to scroll on a phone: let it scroll with the row instead.
  const pins = (api.getColumns() || []).filter(c => c.getColDef().pinned === 'right').map(c => ({ colId: c.getColId(), pinned: phone ? null : 'right' as const }));
  if (pins.length) api.applyColumnState({ state: pins });
  if (!phone) return;
  const optional = (api.getColumns() || []).filter(c => { const d = c.getColDef(); return !d.pinned && !d.checkboxSelection && d.field !== undefined && c.isVisible(); });
  const hide = optional.slice(PHONE_COLUMNS).map(c => c.getColId());
  if (hide.length) { api.setColumnsVisible(hide, false); hiddenByUs.set(api, hide); }
}
function useNarrowColumns(apiRef: { current: GridApi | null }) {
  useEffect(() => {
    const query = window.matchMedia('(max-width: 767px)');
    const apply = () => { const api = apiRef.current; if (api && !api.isDestroyed()) narrowColumns(api); };
    query.addEventListener('change', apply);
    return () => query.removeEventListener('change', apply);
  }, [apiRef]);
}

const baseDefaultColDef: ColDef = { sortable: true, filter: true, resizable: true, minWidth: 110, flex: 1 };

/** Full-featured PayFound AG Grid: themed, with sensible defaults. Pass any AgGridReact prop. */
export function PFGrid<T extends object>({ height = 480, gridRef, defaultColDef, className = '', ...props }: AgGridReactProps<T> & { height?: number | string; gridRef?: Ref<AgGridReact<T>> }) {
  const merged = useMemo(() => ({ ...baseDefaultColDef, ...defaultColDef }) as ColDef<T>, [defaultColDef]);
  const api = useRef<GridApi | null>(null);
  useNarrowColumns(api);
  return <div className={`pf-grid ${className}`} style={{ height }}><AgGridReact<T> ref={gridRef} onGridReady={e => { api.current = e.api; e.api.addEventListener('gridColumnsChanged', () => narrowColumns(e.api)); narrowColumns(e.api); props.onGridReady?.(e); }} theme={pfGridTheme} defaultColDef={merged} animateRows suppressCellFocus={false} {...props} /></div>;
}

/** Backward compatible simple paginated grid (used by the POS simulator). */
export function DataGrid<T extends object>({ rows, columns, height = 410, ...extra }: { rows: T[]; columns: ColDef<T>[]; height?: number } & Partial<AgGridReactProps<T>>) {
  const defaultColDef = useMemo<ColDef<T>>(() => ({ flex: 1, minWidth: 105 }), []);
  return <PFGrid<T> height={height} rowData={rows} columnDefs={columns} defaultColDef={defaultColDef} rowHeight={48} pagination paginationPageSize={10} paginationPageSizeSelector={[10, 20, 50]} animateRows={false} {...extra} />;
}
