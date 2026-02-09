import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Trash2 } from 'lucide-react';

const AlertsList = ({ alerts, assets, onToggle, onDelete }) => {
  const getAssetTicker = (assetId) => {
    const asset = assets.find((a) => a.asset.asset_id === assetId);
    return asset?.asset?.ticker || 'N/A';
  };

  const getAlertTypeLabel = (type) => {
    const labels = {
      target_buy: 'Precio Objetivo Compra',
      target_sell: 'Precio Objetivo Venta',
      stop_loss: 'Stop Loss',
      take_profit: 'Take Profit'
    };
    return labels[type] || type;
  };

  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-border rounded-sm">
        <p className="text-muted-foreground">No tienes alertas configuradas. Crea una desde la sección de activos.</p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-sm overflow-hidden" data-testid="alerts-list">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted/50 border-b border-border">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Ticker
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Tipo de Alerta
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Valor Objetivo
              </th>
              <th className="text-center px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Estado
              </th>
              <th className="text-center px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {alerts.map((alert) => (
              <tr key={alert.alert_id} className="hover:bg-muted/50 transition-colors">
                <td className="px-6 py-4">
                  <span className="font-mono font-semibold">{getAssetTicker(alert.asset_id)}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm">{getAlertTypeLabel(alert.alert_type)}</span>
                </td>
                <td className="px-6 py-4 text-right">
                  <span className="font-mono">
                    {alert.is_percentage ? `${alert.target_value}%` : `$${alert.target_value}`}
                  </span>
                </td>
                <td className="px-6 py-4 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <Switch
                      checked={alert.is_active}
                      onCheckedChange={() => onToggle(alert)}
                      data-testid={`toggle-alert-${alert.alert_id}`}
                    />
                    <span className={`text-xs ${
                      alert.is_active ? 'text-emerald-600' : 'text-muted-foreground'
                    }`}>
                      {alert.is_active ? 'Activa' : 'Pausada'}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(alert.alert_id)}
                    data-testid={`delete-alert-${alert.alert_id}`}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AlertsList;