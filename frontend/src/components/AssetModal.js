import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Lista completa de tickers (CEDEARs + Acciones Argentinas + ONs)
const ALL_TICKERS = [
  // CEDEARs populares
  { ticker: 'AAPL', name: 'Apple Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'MSFT', name: 'Microsoft Corp.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'GOOG', name: 'Alphabet Inc. Class C', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'META', name: 'Meta Platforms', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'TSLA', name: 'Tesla Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'NVDA', name: 'NVIDIA Corp.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'JPM', name: 'JPMorgan Chase', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'V', name: 'Visa Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'MA', name: 'Mastercard Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'DIS', name: 'Walt Disney Co.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'NFLX', name: 'Netflix Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'KO', name: 'Coca-Cola Co.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'PEP', name: 'PepsiCo Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'WMT', name: 'Walmart Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'JNJ', name: 'Johnson & Johnson', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'PG', name: 'Procter & Gamble', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'BABA', name: 'Alibaba Group', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'AMD', name: 'AMD Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'INTC', name: 'Intel Corp.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'BA', name: 'Boeing Co.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'GS', name: 'Goldman Sachs', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'MELI', name: 'MercadoLibre', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'GLOB', name: 'Globant S.A.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'DESP', name: 'Despegar.com', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'PYPL', name: 'PayPal Holdings', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'UBER', name: 'Uber Technologies', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'ABNB', name: 'Airbnb Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'CRM', name: 'Salesforce Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'ORCL', name: 'Oracle Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'IBM', name: 'IBM Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'CSCO', name: 'Cisco Systems', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'ADBE', name: 'Adobe Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'QCOM', name: 'Qualcomm Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'TXN', name: 'Texas Instruments', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'AVGO', name: 'Broadcom Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'COST', name: 'Costco Wholesale', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'HD', name: 'Home Depot', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'NKE', name: 'Nike Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'MCD', name: 'McDonalds Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'SBUX', name: 'Starbucks Corp.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'T', name: 'AT&T Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'VZ', name: 'Verizon Communications', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'XOM', name: 'Exxon Mobil Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'CVX', name: 'Chevron Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'PFE', name: 'Pfizer Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'MRNA', name: 'Moderna Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'ABBV', name: 'AbbVie Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'UNH', name: 'UnitedHealth Group', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'BAC', name: 'Bank of America', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'WFC', name: 'Wells Fargo', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'C', name: 'Citigroup Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'BRK.B', name: 'Berkshire Hathaway B', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'SHOP', name: 'Shopify Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'SQ', name: 'Block Inc. (Square)', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'SNAP', name: 'Snap Inc.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'SPOT', name: 'Spotify Technology', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'ZM', name: 'Zoom Video', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'DOCU', name: 'DocuSign Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'ROKU', name: 'Roku Inc.', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'COIN', name: 'Coinbase Global', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'HOOD', name: 'Robinhood Markets', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'RBLX', name: 'Roblox Corp.', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'U', name: 'Unity Software', market: 'NYSE', type: 'CEDEAR' },
  { ticker: 'EA', name: 'Electronic Arts', market: 'NASDAQ', type: 'CEDEAR' },
  { ticker: 'ATVI', name: 'Activision Blizzard', market: 'NASDAQ', type: 'CEDEAR' },
  // Acciones argentinas (BCBA)
  { ticker: 'GGAL', name: 'Grupo Galicia', market: 'BCBA', type: 'Acción' },
  { ticker: 'YPFD', name: 'YPF S.A.', market: 'BCBA', type: 'Acción' },
  { ticker: 'PAMP', name: 'Pampa Energía', market: 'BCBA', type: 'Acción' },
  { ticker: 'TXAR', name: 'Ternium Argentina', market: 'BCBA', type: 'Acción' },
  { ticker: 'ALUA', name: 'Aluar', market: 'BCBA', type: 'Acción' },
  { ticker: 'BBAR', name: 'Banco BBVA Argentina', market: 'BCBA', type: 'Acción' },
  { ticker: 'BMA', name: 'Banco Macro', market: 'BCBA', type: 'Acción' },
  { ticker: 'SUPV', name: 'Grupo Supervielle', market: 'BCBA', type: 'Acción' },
  { ticker: 'CEPU', name: 'Central Puerto', market: 'BCBA', type: 'Acción' },
  { ticker: 'TECO2', name: 'Telecom Argentina', market: 'BCBA', type: 'Acción' },
  { ticker: 'EDN', name: 'Edenor', market: 'BCBA', type: 'Acción' },
  { ticker: 'TRAN', name: 'Transener', market: 'BCBA', type: 'Acción' },
  { ticker: 'MIRG', name: 'Mirgor', market: 'BCBA', type: 'Acción' },
  { ticker: 'CRES', name: 'Cresud', market: 'BCBA', type: 'Acción' },
  { ticker: 'LOMA', name: 'Loma Negra', market: 'BCBA', type: 'Acción' },
  { ticker: 'VALO', name: 'Grupo Valores', market: 'BCBA', type: 'Acción' },
  { ticker: 'COME', name: 'Sociedad Comercial del Plata', market: 'BCBA', type: 'Acción' },
  { ticker: 'BYMA', name: 'Bolsas y Mercados Argentinos', market: 'BCBA', type: 'Acción' },
  { ticker: 'IRSA', name: 'IRSA Propiedades', market: 'BCBA', type: 'Acción' },
  { ticker: 'AGRO', name: 'Agrometal', market: 'BCBA', type: 'Acción' },
  { ticker: 'AUSO', name: 'Autopistas del Sol', market: 'BCBA', type: 'Acción' },
  { ticker: 'BHIP', name: 'Banco Hipotecario', market: 'BCBA', type: 'Acción' },
  { ticker: 'BOLT', name: 'Boldt', market: 'BCBA', type: 'Acción' },
  { ticker: 'BPAT', name: 'Banco Patagonia', market: 'BCBA', type: 'Acción' },
  { ticker: 'CADO', name: 'Carlos Casado', market: 'BCBA', type: 'Acción' },
  { ticker: 'CAPX', name: 'Capex', market: 'BCBA', type: 'Acción' },
  { ticker: 'CARC', name: 'Carboclor', market: 'BCBA', type: 'Acción' },
  { ticker: 'CECO2', name: 'Central Costanera', market: 'BCBA', type: 'Acción' },
  { ticker: 'CELU', name: 'Celulosa Argentina', market: 'BCBA', type: 'Acción' },
  { ticker: 'CGPA2', name: 'Camuzzi Gas Pampeana', market: 'BCBA', type: 'Acción' },
  { ticker: 'CTIO', name: 'Consultatio', market: 'BCBA', type: 'Acción' },
  { ticker: 'CVH', name: 'Cablevisión Holding', market: 'BCBA', type: 'Acción' },
  { ticker: 'DGCU2', name: 'Distribuidora de Gas Cuyana', market: 'BCBA', type: 'Acción' },
  { ticker: 'DYCA', name: 'Dycasa', market: 'BCBA', type: 'Acción' },
  { ticker: 'FERR', name: 'Ferrum', market: 'BCBA', type: 'Acción' },
  { ticker: 'FIPL', name: 'Fiplasto', market: 'BCBA', type: 'Acción' },
  { ticker: 'GAMI', name: 'Gami', market: 'BCBA', type: 'Acción' },
  { ticker: 'GARO', name: 'Garovaglio', market: 'BCBA', type: 'Acción' },
  { ticker: 'GBAN', name: 'Gas Natural BAN', market: 'BCBA', type: 'Acción' },
  { ticker: 'GCLA', name: 'Grupo Clarín', market: 'BCBA', type: 'Acción' },
  { ticker: 'GRIM', name: 'Grimoldi', market: 'BCBA', type: 'Acción' },
  { ticker: 'HARG', name: 'Holcim Argentina', market: 'BCBA', type: 'Acción' },
  { ticker: 'HAVA', name: 'Havanna Holding', market: 'BCBA', type: 'Acción' },
  { ticker: 'INTR', name: 'Introductora', market: 'BCBA', type: 'Acción' },
  { ticker: 'INVJ', name: 'Inversora Juramento', market: 'BCBA', type: 'Acción' },
  { ticker: 'LONG', name: 'Longvie', market: 'BCBA', type: 'Acción' },
  { ticker: 'METR', name: 'Metrogas', market: 'BCBA', type: 'Acción' },
  { ticker: 'MOLA', name: 'Molinos Agro', market: 'BCBA', type: 'Acción' },
  { ticker: 'MOLI', name: 'Molinos Río de la Plata', market: 'BCBA', type: 'Acción' },
  { ticker: 'MORI', name: 'Morixe', market: 'BCBA', type: 'Acción' },
  { ticker: 'MTR', name: 'Matba Rofex', market: 'BCBA', type: 'Acción' },
  { ticker: 'PATA', name: 'Imp. y Exp. Patagonia', market: 'BCBA', type: 'Acción' },
  { ticker: 'RICH', name: 'Laboratorios Richmond', market: 'BCBA', type: 'Acción' },
  { ticker: 'RIGO', name: 'Rigolleau', market: 'BCBA', type: 'Acción' },
  { ticker: 'ROSE', name: 'Instituto Rosenbusch', market: 'BCBA', type: 'Acción' },
  { ticker: 'SAMI', name: 'San Miguel', market: 'BCBA', type: 'Acción' },
  { ticker: 'SEMI', name: 'Molinos Juan Semino', market: 'BCBA', type: 'Acción' },
  { ticker: 'TGNO4', name: 'Transportadora Gas del Norte', market: 'BCBA', type: 'Acción' },
  { ticker: 'TGSU2', name: 'Transportadora Gas del Sur', market: 'BCBA', type: 'Acción' },
  // ONs
  { ticker: 'YCA6O', name: 'YPF ON Clase XLVI', market: 'BCBA', type: 'Obligación Negociable' },
  { ticker: 'IRCFO', name: 'IRCP ON', market: 'BCBA', type: 'Obligación Negociable' },
  { ticker: 'PAA2O', name: 'Pan American Energy ON', market: 'BCBA', type: 'Obligación Negociable' },
  { ticker: 'TLC1O', name: 'Telecom ON', market: 'BCBA', type: 'Obligación Negociable' },
  { ticker: 'GMCAO', name: 'Grupo Macro ON', market: 'BCBA', type: 'Obligación Negociable' },
];

const MARKETS = [
  { value: 'BCBA', label: 'BCBA - Bolsa de Buenos Aires' },
  { value: 'NYSE', label: 'NYSE - New York Stock Exchange' },
  { value: 'NASDAQ', label: 'NASDAQ' },
  { value: 'BYMA', label: 'BYMA - Bolsas y Mercados Argentinos' },
];

const AssetModal = ({ isOpen, onClose, onSave, asset, token }) => {
  const [formData, setFormData] = useState({
    asset_type: 'CEDEAR',
    ticker: '',
    quantity: '',
    avg_purchase_price: '',
    purchase_date: '',
    market: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [tickerSearch, setTickerSearch] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Filtrar sugerencias - busca en TODOS los tickers cuando hay texto
  const filteredTickers = useMemo(() => {
    if (!tickerSearch || tickerSearch.length < 1) return [];
    
    const search = tickerSearch.toUpperCase();
    
    // Buscar en todos los tickers
    const results = ALL_TICKERS.filter(t => 
      t.ticker.toUpperCase().includes(search) || 
      t.name.toUpperCase().includes(search)
    );
    
    // Ordenar: primero los que empiezan con la búsqueda, luego los que la contienen
    results.sort((a, b) => {
      const aStartsWith = a.ticker.toUpperCase().startsWith(search);
      const bStartsWith = b.ticker.toUpperCase().startsWith(search);
      if (aStartsWith && !bStartsWith) return -1;
      if (!aStartsWith && bStartsWith) return 1;
      return a.ticker.localeCompare(b.ticker);
    });
    
    return results.slice(0, 10);
  }, [tickerSearch]);

  useEffect(() => {
    if (asset) {
      setFormData({
        asset_type: asset.asset_type,
        ticker: asset.ticker,
        quantity: asset.quantity.toString(),
        avg_purchase_price: asset.avg_purchase_price.toString(),
        purchase_date: asset.purchase_date,
        market: asset.market
      });
      setTickerSearch(asset.ticker);
    } else {
      // Reset form para nuevo activo
      setFormData({
        asset_type: 'CEDEAR',
        ticker: '',
        quantity: '',
        avg_purchase_price: '',
        purchase_date: '',
        market: ''
      });
      setTickerSearch('');
    }
  }, [asset, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const data = {
      ...formData,
      quantity: parseFloat(formData.quantity),
      avg_purchase_price: parseFloat(formData.avg_purchase_price)
    };

    try {
      if (asset) {
        await axios.put(`${API}/assets/${asset.asset_id}`, data, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Activo actualizado');
      } else {
        await axios.post(`${API}/assets`, data, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Activo creado');
      }
      onSave();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al guardar activo');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Seleccionar un ticker de las sugerencias - autocompleta tipo, mercado y ticker
  const handleSelectTicker = (tickerData) => {
    setFormData(prev => ({
      ...prev,
      ticker: tickerData.ticker,
      market: tickerData.market,
      asset_type: tickerData.type
    }));
    setTickerSearch(tickerData.ticker);
    setShowSuggestions(false);
  };

  // Manejar cambio manual del ticker
  const handleTickerChange = (value) => {
    const upperValue = value.toUpperCase();
    setTickerSearch(upperValue);
    setFormData(prev => ({ ...prev, ticker: upperValue }));
    setShowSuggestions(true);
  };

  // Función para resaltar la coincidencia en el texto
  const highlightMatch = (text, search) => {
    if (!search) return text;
    const index = text.toUpperCase().indexOf(search.toUpperCase());
    if (index === -1) return text;
    return (
      <>
        {text.slice(0, index)}
        <span className="bg-yellow-200 dark:bg-yellow-800 font-bold">{text.slice(index, index + search.length)}</span>
        {text.slice(index + search.length)}
      </>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md" data-testid="asset-modal">
        <DialogHeader>
          <DialogTitle>{asset ? 'Editar Activo' : 'Agregar Activo'}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="asset_type">Tipo de Activo</Label>
            <Select value={formData.asset_type} onValueChange={(value) => handleChange('asset_type', value)}>
              <SelectTrigger data-testid="asset-type-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="CEDEAR">CEDEAR</SelectItem>
                <SelectItem value="Acción">Acción</SelectItem>
                <SelectItem value="Obligación Negociable">Obligación Negociable</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2 relative">
            <Label htmlFor="ticker">Ticker</Label>
            <Input
              id="ticker"
              value={tickerSearch}
              onChange={(e) => handleTickerChange(e.target.value)}
              onFocus={() => tickerSearch && setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder="Escribí el ticker (ej: GG, AA, MSFT)"
              required
              autoComplete="off"
              data-testid="ticker-input"
            />
            {/* Dropdown de sugerencias */}
            {showSuggestions && filteredTickers.length > 0 && (
              <div className="absolute z-50 w-full mt-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-md shadow-lg max-h-60 overflow-auto">
                {filteredTickers.map((item) => (
                  <div
                    key={item.ticker}
                    className="px-3 py-2 cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800 border-b border-zinc-100 dark:border-zinc-800 last:border-0"
                    onMouseDown={() => handleSelectTicker(item)}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                        {highlightMatch(item.ticker, tickerSearch)}
                      </span>
                      <div className="flex gap-1">
                        <span className="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded">{item.type}</span>
                        <span className="text-xs bg-zinc-200 dark:bg-zinc-700 px-2 py-0.5 rounded">{item.market}</span>
                      </div>
                    </div>
                    <div className="text-sm text-zinc-500 dark:text-zinc-400">
                      {highlightMatch(item.name, tickerSearch)}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {tickerSearch && filteredTickers.length === 0 && showSuggestions && (
              <div className="absolute z-50 w-full mt-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-md shadow-lg p-3 text-center text-zinc-500">
                No se encontraron tickers. Podés escribir uno personalizado.
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="quantity">Cantidad</Label>
              <Input
                id="quantity"
                type="number"
                step="0.01"
                value={formData.quantity}
                onChange={(e) => handleChange('quantity', e.target.value)}
                placeholder="10"
                required
                data-testid="quantity-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="avg_purchase_price">Precio Promedio</Label>
              <Input
                id="avg_purchase_price"
                type="number"
                step="0.01"
                value={formData.avg_purchase_price}
                onChange={(e) => handleChange('avg_purchase_price', e.target.value)}
                placeholder="150.00"
                required
                data-testid="price-input"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="purchase_date">Fecha de Compra</Label>
            <Input
              id="purchase_date"
              type="date"
              value={formData.purchase_date}
              onChange={(e) => handleChange('purchase_date', e.target.value)}
              required
              data-testid="date-input"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="market">Mercado</Label>
            <Select value={formData.market} onValueChange={(value) => handleChange('market', value)}>
              <SelectTrigger data-testid="market-input">
                <SelectValue placeholder="Seleccionar mercado" />
              </SelectTrigger>
              <SelectContent>
                {MARKETS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              data-testid="cancel-button"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={isLoading}
              data-testid="save-asset-button"
            >
              {isLoading ? 'Guardando...' : 'Guardar'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AssetModal;