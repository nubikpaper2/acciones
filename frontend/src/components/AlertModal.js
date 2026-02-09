import { useState } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AlertModal = ({ isOpen, onClose, onSave, asset, token }) => {
  const [formData, setFormData] = useState({
    alert_type: 'target_sell',
    target_value: '',
    is_percentage: false
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const data = {
      asset_id: asset.asset.asset_id,
      alert_type: formData.alert_type,
      target_value: parseFloat(formData.target_value),
      is_percentage: formData.is_percentage
    };

    try {
      await axios.post(`${API}/alerts`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Alerta creada');
      onSave();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear alerta');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md" data-testid="alert-modal">
        <DialogHeader>
          <DialogTitle>
            Crear Alerta para {asset.asset.ticker}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="alert_type">Tipo de Alerta</Label>
            <Select value={formData.alert_type} onValueChange={(value) => handleChange('alert_type', value)}>
              <SelectTrigger data-testid="alert-type-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="target_buy">Precio Objetivo de Compra</SelectItem>
                <SelectItem value="target_sell">Precio Objetivo de Venta</SelectItem>
                <SelectItem value="stop_loss">Stop Loss</SelectItem>
                <SelectItem value="take_profit">Take Profit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="target_value">Valor Objetivo</Label>
            <Input
              id="target_value"
              type="number"
              step="0.01"
              value={formData.target_value}
              onChange={(e) => handleChange('target_value', e.target.value)}
              placeholder={formData.is_percentage ? '10 (%)' : '200 ($)'}
              required
              data-testid="target-value-input"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="is_percentage"
              checked={formData.is_percentage}
              onCheckedChange={(checked) => handleChange('is_percentage', checked)}
              data-testid="percentage-switch"
            />
            <Label htmlFor="is_percentage" className="cursor-pointer">
              Usar porcentaje en lugar de precio fijo
            </Label>
          </div>

          <div className="bg-muted p-4 rounded-sm text-sm">
            <p className="text-muted-foreground">
              {formData.is_percentage
                ? `Se activará cuando el precio cambie ${formData.target_value || '0'}% respecto al precio de compra ($${asset.asset.avg_purchase_price.toFixed(2)})`
                : `Se activará cuando el precio alcance $${formData.target_value || '0'}`}
            </p>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              data-testid="cancel-alert-button"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={isLoading}
              data-testid="save-alert-button"
            >
              {isLoading ? 'Creando...' : 'Crear Alerta'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AlertModal;