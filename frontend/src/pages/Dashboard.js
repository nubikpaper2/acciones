import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import {
  LayoutDashboard,
  PieChart,
  Bell,
  History,
  LogOut,
  Plus
} from 'lucide-react';
import PortfolioSummary from '@/components/PortfolioSummary';
import AssetsList from '@/components/AssetsList';
import AlertsList from '@/components/AlertsList';
import AlertHistoryList from '@/components/AlertHistoryList';
import AssetModal from '@/components/AssetModal';
import AlertModal from '@/components/AlertModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [summary, setSummary] = useState(null);
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [alertHistory, setAlertHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAssetModal, setShowAssetModal] = useState(false);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [selectedAssetForAlert, setSelectedAssetForAlert] = useState(null);

  const token = localStorage.getItem('token');
  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [summaryRes, assetsRes, alertsRes, historyRes] = await Promise.all([
        axios.get(`${API}/portfolio/summary`, axiosConfig),
        axios.get(`${API}/portfolio/assets`, axiosConfig),
        axios.get(`${API}/alerts`, axiosConfig),
        axios.get(`${API}/alerts/history`, axiosConfig)
      ]);

      setSummary(summaryRes.data);
      setAssets(assetsRes.data);
      setAlerts(alertsRes.data);
      setAlertHistory(historyRes.data);
    } catch (error) {
      toast.error('Error al cargar datos');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddAsset = () => {
    setEditingAsset(null);
    setShowAssetModal(true);
  };

  const handleEditAsset = (asset) => {
    setEditingAsset(asset);
    setShowAssetModal(true);
  };

  const handleDeleteAsset = async (assetId) => {
    if (!window.confirm('¿Estás seguro de eliminar este activo?')) return;

    try {
      await axios.delete(`${API}/assets/${assetId}`, axiosConfig);
      toast.success('Activo eliminado');
      fetchData();
    } catch (error) {
      toast.error('Error al eliminar activo');
    }
  };

  const handleAssetSaved = () => {
    setShowAssetModal(false);
    setEditingAsset(null);
    fetchData();
  };

  const handleAddAlert = (asset) => {
    setSelectedAssetForAlert(asset);
    setShowAlertModal(true);
  };

  const handleAlertSaved = () => {
    setShowAlertModal(false);
    setSelectedAssetForAlert(null);
    fetchData();
  };

  const handleDeleteAlert = async (alertId) => {
    try {
      await axios.delete(`${API}/alerts/${alertId}`, axiosConfig);
      toast.success('Alerta eliminada');
      fetchData();
    } catch (error) {
      toast.error('Error al eliminar alerta');
    }
  };

  const handleToggleAlert = async (alert) => {
    try {
      await axios.put(
        `${API}/alerts/${alert.alert_id}`,
        { is_active: !alert.is_active },
        axiosConfig
      );
      toast.success(alert.is_active ? 'Alerta pausada' : 'Alerta activada');
      fetchData();
    } catch (error) {
      toast.error('Error al actualizar alerta');
    }
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'assets', label: 'Activos', icon: PieChart },
    { id: 'alerts', label: 'Alertas', icon: Bell },
    { id: 'history', label: 'Historial', icon: History }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background" data-testid="dashboard">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card hidden md:block">
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold text-primary">InvestTracker</h1>
          <p className="text-sm text-muted-foreground mt-1">{user?.name || 'Usuario'}</p>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                  activeTab === item.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted text-foreground'
                }`}
                data-testid={`nav-${item.id}`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-border">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={onLogout}
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Cerrar Sesión
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="border-b border-border bg-card p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold">
                {menuItems.find((item) => item.id === activeTab)?.label}
              </h2>
              <p className="text-muted-foreground mt-1">
                {activeTab === 'dashboard' && 'Resumen de tu cartera de inversiones'}
                {activeTab === 'assets' && 'Administra tus activos'}
                {activeTab === 'alerts' && 'Configura alertas de precios'}
                {activeTab === 'history' && 'Historial de alertas enviadas'}
              </p>
            </div>

            {activeTab === 'assets' && (
              <Button onClick={handleAddAsset} data-testid="add-asset-button">
                <Plus className="w-4 h-4 mr-2" />
                Agregar Activo
              </Button>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <PortfolioSummary summary={summary} />
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Tus Activos</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAddAsset}
                    data-testid="dashboard-add-asset-button"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Agregar
                  </Button>
                </div>
                <AssetsList
                  assets={assets}
                  onEdit={handleEditAsset}
                  onDelete={handleDeleteAsset}
                  onAddAlert={handleAddAlert}
                />
              </div>
            </div>
          )}

          {activeTab === 'assets' && (
            <AssetsList
              assets={assets}
              onEdit={handleEditAsset}
              onDelete={handleDeleteAsset}
              onAddAlert={handleAddAlert}
            />
          )}

          {activeTab === 'alerts' && (
            <AlertsList
              alerts={alerts}
              assets={assets}
              onToggle={handleToggleAlert}
              onDelete={handleDeleteAlert}
            />
          )}

          {activeTab === 'history' && <AlertHistoryList history={alertHistory} />}
        </div>
      </main>

      {/* Modals */}
      {showAssetModal && (
        <AssetModal
          isOpen={showAssetModal}
          onClose={() => {
            setShowAssetModal(false);
            setEditingAsset(null);
          }}
          onSave={handleAssetSaved}
          asset={editingAsset}
          token={token}
        />
      )}

      {showAlertModal && selectedAssetForAlert && (
        <AlertModal
          isOpen={showAlertModal}
          onClose={() => {
            setShowAlertModal(false);
            setSelectedAssetForAlert(null);
          }}
          onSave={handleAlertSaved}
          asset={selectedAssetForAlert}
          token={token}
        />
      )}
    </div>
  );
};

export default Dashboard;