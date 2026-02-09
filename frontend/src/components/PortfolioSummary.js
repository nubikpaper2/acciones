import { TrendingUp, TrendingDown, DollarSign, Package } from 'lucide-react';

const PortfolioSummary = ({ summary }) => {
  if (!summary) return null;

  const isPositive = summary.total_gain_loss >= 0;

  const stats = [
    {
      label: 'Inversión Total',
      value: `$${summary.total_investment.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: 'text-blue-600'
    },
    {
      label: 'Valor Actual',
      value: `$${summary.current_value.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: TrendingUp,
      color: 'text-primary'
    },
    {
      label: 'Ganancia/Pérdida',
      value: `$${summary.total_gain_loss.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      subValue: `${summary.total_gain_loss_pct >= 0 ? '+' : ''}${summary.total_gain_loss_pct.toFixed(2)}%`,
      icon: isPositive ? TrendingUp : TrendingDown,
      color: isPositive ? 'text-emerald-600' : 'text-rose-600'
    },
    {
      label: 'Activos',
      value: summary.assets_count.toString(),
      icon: Package,
      color: 'text-violet-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="portfolio-summary">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div
            key={index}
            className="stat-card bg-card border border-border rounded-sm p-6 shadow-sm"
            data-testid={`stat-card-${index}`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-muted-foreground font-medium uppercase tracking-wider">
                {stat.label}
              </span>
              <Icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div className={`text-3xl font-bold font-mono ${stat.color}`}>
              {stat.value}
            </div>
            {stat.subValue && (
              <div className={`text-sm font-mono mt-2 ${stat.color}`}>
                {stat.subValue}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default PortfolioSummary;