import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const AlertHistoryList = ({ history }) => {
  if (history.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-border rounded-sm">
        <p className="text-muted-foreground">No hay alertas enviadas aún.</p>
      </div>
    );
  }

  const getAlertTypeLabel = (type) => {
    const labels = {
      target_buy: 'Objetivo Compra',
      target_sell: 'Objetivo Venta',
      stop_loss: 'Stop Loss',
      take_profit: 'Take Profit'
    };
    return labels[type] || type;
  };

  const getAlertColor = (type) => {
    const colors = {
      target_buy: 'text-blue-600',
      target_sell: 'text-emerald-600',
      stop_loss: 'text-rose-600',
      take_profit: 'text-violet-600'
    };
    return colors[type] || 'text-foreground';
  };

  return (
    <div className="space-y-4" data-testid="alert-history-list">
      {history.map((item) => (
        <div
          key={item.history_id}
          className="bg-card border border-border rounded-sm p-6 hover:border-primary/20 transition-colors"
        >
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-xl">{item.ticker}</span>
                <span className={`text-sm font-medium px-3 py-1 rounded-full bg-muted ${
                  getAlertColor(item.alert_type)
                }`}>
                  {getAlertTypeLabel(item.alert_type)}
                </span>
              </div>
              <p className="text-muted-foreground text-sm mt-2">{item.message}</p>
            </div>
            <div className="text-right">
              <div className="font-mono font-bold text-lg text-primary">
                ${item.current_price.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {format(new Date(item.sent_at), "d 'de' MMMM yyyy 'a las' HH:mm", { locale: es })}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertHistoryList;