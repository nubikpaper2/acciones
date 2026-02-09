import { useState, useEffect } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    }
  }, [asset]);

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

          <div className="space-y-2">
            <Label htmlFor="ticker">Ticker</Label>
            <Input
              id="ticker"
              value={formData.ticker}
              onChange={(e) => handleChange('ticker', e.target.value.toUpperCase())}
              placeholder="AAPL, GGAL.BA, etc."
              required
              data-testid="ticker-input"
            />
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
            <Input
              id="market"
              value={formData.market}
              onChange={(e) => handleChange('market', e.target.value)}
              placeholder="NYSE, NASDAQ, BCBA"
              required
              data-testid="market-input"
            />
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