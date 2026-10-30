import { ModuleRegistry, themeQuartz } from 'ag-grid-community';
import { AllEnterpriseModule, LicenseManager } from 'ag-grid-enterprise';
import { AgChartsEnterpriseModule } from 'ag-charts-enterprise';

/**
 * AG Grid Enterprise (all modules + AG Charts Enterprise for integrated charts and sparklines),
 * registered once for every grid in the app. The AG Studio trial key is applied as the grid
 * licence key; if it is not accepted for Grid, Enterprise still runs with a watermark.
 */
const key = import.meta.env.VITE_AG_STUDIO_LICENSE_KEY as string | undefined;
if (key) LicenseManager.setLicenseKey(key);
ModuleRegistry.registerModules([AllEnterpriseModule.with(AgChartsEnterpriseModule)]);

/** PayFound grid theme: Inter, ink text, hairlines, airy rows, blue accent. */
export const pfGridTheme = themeQuartz.withParams({
  accentColor: '#0057ff',
  backgroundColor: '#ffffff',
  foregroundColor: '#0a0a0b',
  textColor: '#0a0a0b',
  borderColor: '#e7e8eb',
  fontFamily: "'Inter', ui-sans-serif, system-ui, sans-serif",
  fontSize: 14,
  headerFontSize: 12.5,
  headerFontWeight: 600,
  headerTextColor: '#62656d',
  headerBackgroundColor: '#f6f6f7',
  headerHeight: 44,
  rowHeight: 56,
  wrapperBorder: false,
  wrapperBorderRadius: 0,
  headerColumnBorder: false,
  columnBorder: false,
  rowBorder: { style: 'solid', width: 1, color: '#eff0f2' },
  rowHoverColor: '#f8f8f9',
  selectedRowBackgroundColor: 'rgba(0, 87, 255, 0.06)',
  oddRowBackgroundColor: '#ffffff',
  pinnedRowBackgroundColor: '#f6f6f7',
  pinnedRowFontWeight: 600,
  iconSize: 15,
  spacing: 8,
  cellHorizontalPaddingScale: 1,
  inputBorder: { color: '#cfd1d6' },
  menuShadow: '0 12px 40px rgb(10 10 11 / 0.12), 0 2px 8px rgb(10 10 11 / 0.06)',
  popupShadow: '0 12px 40px rgb(10 10 11 / 0.12), 0 2px 8px rgb(10 10 11 / 0.06)',
  statusBarLabelColor: '#62656d',
  statusBarValueColor: '#0a0a0b',
  sideBarBackgroundColor: '#ffffff',
  cellEditingBorder: { color: '#0057ff', width: 2, style: 'solid' },
  cellEditingShadow: '0 4px 16px rgb(0 87 255 / 0.18)',
  rangeSelectionBorderColor: '#0057ff',
  rangeSelectionBackgroundColor: 'rgba(0, 87, 255, 0.07)',
  rangeSelectionChartBackgroundColor: 'rgba(0, 87, 255, 0.12)',
  rangeSelectionChartCategoryBackgroundColor: 'rgba(10, 10, 11, 0.06)',
});
