import { Button } from '@/components/ui/button';
import { Pencil, Trash2, Bell, TrendingUp, TrendingDown } from 'lucide-react';

const AssetsList = ({ assets, onEdit, onDelete, onAddAlert }) => {
  if (assets.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-border rounded-sm">
        <p className="text-muted-foreground">No tienes activos aún. ¡Agrega tu primer activo!</p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-sm overflow-hidden" data-testid="assets-list">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted/50 border-b border-border">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Ticker
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Tipo
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Cantidad
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Precio Compra
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Precio Actual
              </th>
              <th className="text-right px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Ganancia/Pérdida
              </th>
              <th className="text-left px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Recomendación
              </th>
              <th className="text-center px-6 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {assets.map((assetWithPrice) => {
              const asset = assetWithPrice.asset;
              const isPositive = (assetWithPrice.gain_loss || 0) >= 0;

              return (
                <tr
                  key={asset.asset_id}
                  className="asset-row"
                  data-testid={`asset-row-${asset.ticker}`}
                >
                  <td className="px-6 py-4">
                    <div className="font-mono font-semibold text-base">{asset.ticker}</div>
                    <div className="text-xs text-muted-foreground">{asset.market}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm">{asset.asset_type}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono">{asset.quantity}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono">
                      ${asset.avg_purchase_price.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {assetWithPrice.current_price ? (
                      <span className="font-mono">
                        ${assetWithPrice.current_price.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
                      </span>
                    ) : (
                      <span className="text-muted-foreground text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {assetWithPrice.gain_loss !== null ? (
                      <div className="flex flex-col items-end">
                        <div className={`font-mono font-semibold flex items-center gap-1 ${
                          isPositive ? 'text-emerald-600' : 'text-rose-600'
                        }`}>
                          {isPositive ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          )}
                          ${assetWithPrice.gain_loss.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
                        </div>
                        <div className={`font-mono text-xs ${
                          isPositive ? 'text-emerald-600' : 'text-rose-600'
                        }`}>
                          {assetWithPrice.gain_loss_pct >= 0 ? '+' : ''}
                          {assetWithPrice.gain_loss_pct?.toFixed(2)}%
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-muted-foreground">
                      {assetWithPrice.recommendation || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onAddAlert(assetWithPrice)}
                        data-testid={`add-alert-${asset.ticker}`}
                      >
                        <Bell className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onEdit(asset)}
                        data-testid={`edit-asset-${asset.ticker}`}
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onDelete(asset.asset_id)}
                        data-testid={`delete-asset-${asset.ticker}`}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssetsList;