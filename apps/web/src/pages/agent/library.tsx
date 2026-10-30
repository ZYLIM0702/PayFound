import { buildLibrary } from './library.spec';
import { OfferGridView, OfferView, StoreMapView, RouteCardView, WeatherCardView, CompareOffersView, StoreSummaryView, ReviewsView, OrderStatusView, OrderListView } from '../../components/assistant/cards';
import { ReserveAndPayView } from '../../components/assistant/ReserveAndPay';
import { ReportCardChatView } from '../merchant/reports/ReportCardView';
import { KpiRowView, StockAlertsView, MerchantOrderQueueView } from '../../components/assistant/merchantCards';

export const payfoundLibrary = buildLibrary({
  OfferGrid: ({ props }: any) => <OfferGridView props={props} />,
  Offer: ({ props }: any) => <OfferView props={props} />,
  StoreMap: ({ props }: any) => <StoreMapView props={props} />,
  RouteCard: ({ props }: any) => <RouteCardView props={props} />,
  WeatherCard: ({ props }: any) => <WeatherCardView props={props} />,
  CompareOffers: ({ props }: any) => <CompareOffersView props={props} />,
  StoreSummary: ({ props }: any) => <StoreSummaryView props={props} />,
  Reviews: ({ props }: any) => <ReviewsView props={props} />,
  ReserveAndPay: ({ props }: any) => <ReserveAndPayView props={props} />,
  OrderStatus: ({ props }: any) => <OrderStatusView props={props} />,
  OrderList: () => <OrderListView />,
  KpiRow: ({ props }: any) => <KpiRowView props={props} />,
  StockAlerts: ({ props }: any) => <StockAlertsView props={props} />,
  MerchantOrderQueue: ({ props }: any) => <MerchantOrderQueueView props={props} />,
  ReportCard: ({ props }: any) => <ReportCardChatView props={props} />,
});
