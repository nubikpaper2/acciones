import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const periods = [
  { value: '1d', label: '1D' },
  { value: '5d', label: '5D' },
  { value: '1mo', label: '1M' },
  { value: '3mo', label: '3M' },
  { value: '6mo', label: '6M' },
  { value: '1y', label: '1A' },
];

const AssetChartModal = ({ isOpen, onClose, asset, currentPrice, gainLoss, gainLossPct }) => {
  const [priceHistory, setPriceHistory] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('1mo');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && asset) {
      fetchPriceHistory();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, asset, selectedPeriod]);

  const fetchPriceHistory = async () => {
    if (!asset) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${API_URL}/api/prices/${asset.ticker}/history?market=${encodeURIComponent(asset.market)}&asset_type=${encodeURIComponent(asset.asset_type)}&period=${selectedPeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setPriceHistory(data.history || []);
      } else {
        setError('No se pudo cargar el historial de precios');
      }
    } catch (err) {
      setError('Error al conectar con el servidor');
    } finally {
      setLoading(false);
    }
  };

  if (!asset) return null;

  const isPositive = (gainLoss || 0) >= 0;
  const purchasePrice = asset.avg_purchase_price;

  // Formatear precio para tooltip
  const formatPrice = (value) => {
    return `$${value?.toLocaleString('es-AR', { minimumFractionDigits: 2 })}`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-sm font-semibold">{formatPrice(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-2xl font-bold">{asset.ticker}</span>
            <span className="text-sm text-muted-foreground font-normal">
              {asset.market} • {asset.asset_type}
            </span>
          </DialogTitle>
        </DialogHeader>

        {/* Precio actual y ganancia */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Precio Actual</p>
            <p className="text-xl font-bold font-mono">
              {currentPrice ? formatPrice(currentPrice) : '-'}
            </p>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Precio Compra</p>
            <p className="text-xl font-bold font-mono">
              {formatPrice(purchasePrice)}
            </p>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Ganancia/Pérdida</p>
            <div className={`flex items-center gap-1 text-xl font-bold font-mono ${
              isPositive ? 'text-emerald-600' : 'text-rose-600'
            }`}>
              {isPositive ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
              {gainLoss !== null ? formatPrice(Math.abs(gainLoss)) : '-'}
            </div>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Variación %</p>
            <p className={`text-xl font-bold font-mono ${
              isPositive ? 'text-emerald-600' : 'text-rose-600'
            }`}>
              {gainLossPct !== null ? `${gainLossPct >= 0 ? '+' : ''}${gainLossPct?.toFixed(2)}%` : '-'}
            </p>
          </div>
        </div>

        {/* Selector de período */}
        <div className="flex gap-2 mb-4">
          {periods.map((period) => (
            <Button
              key={period.value}
              variant={selectedPeriod === period.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period.value)}
            >
              {period.label}
            </Button>
          ))}
        </div>

        {/* Gráfico */}
        <div className="h-[300px] w-full">
          {loading ? (
            <div className="h-full flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground">{error}</p>
            </div>
          ) : priceHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceHistory} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 10 }}
                  tickFormatter={(value) => {
                    if (selectedPeriod === '1d' || selectedPeriod === '5d') {
                      return value.split(' ')[1] || value;
                    }
                    return value.split(' ')[0];
                  }}
                  stroke="hsl(var(--muted-foreground))"
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 10 }}
                  tickFormatter={(value) => `$${value.toLocaleString()}`}
                  stroke="hsl(var(--muted-foreground))"
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine 
                  y={purchasePrice} 
                  stroke="hsl(var(--primary))" 
                  strokeDasharray="5 5"
                  label={{ 
                    value: 'Compra', 
                    position: 'right',
                    fill: 'hsl(var(--primary))',
                    fontSize: 10
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke={isPositive ? '#10b981' : '#f43f5e'}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground">No hay datos disponibles</p>
            </div>
          )}
        </div>

        {/* Info adicional */}
        <div className="text-xs text-muted-foreground text-center mt-2">
          Cantidad: {asset.quantity} • Inversión Total: {formatPrice(asset.quantity * purchasePrice)}
          {currentPrice && ` • Valor Actual: ${formatPrice(asset.quantity * currentPrice)}`}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AssetChartModal;
