"""
Chart generation service using matplotlib
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging
import sys

logger = logging.getLogger(__name__)

# Try to import matplotlib with detailed error logging
MATPLOTLIB_AVAILABLE = False
plt = None
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
    logger.info("matplotlib successfully imported")
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    logger.error(f"matplotlib ImportError: {e}")
    logger.error(f"Python executable: {sys.executable if 'sys' in dir() else 'unknown'}")
except Exception as e:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    logger.error(f"matplotlib import failed with exception: {type(e).__name__}: {e}")
    import sys
    logger.error(f"Python executable: {sys.executable}")
    logger.error(f"Python path: {sys.path[:3]}")


def _ensure_charts_dir() -> Path:
    """Ensure charts directory exists"""
    charts_dir = Path("generated_charts")
    charts_dir.mkdir(exist_ok=True)
    return charts_dir


def generate_cost_chart(all_periods_stats: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
    """Generate cost comparison bar chart"""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available, skipping chart generation")
        return None
    
    try:
        period_labels = {
            "day": "Nap",
            "week": "Hét",
            "month": "Hó",
            "year": "Év"
        }
        
        periods = list(all_periods_stats.keys())
        labels = [period_labels.get(p, p) for p in periods]
        
        worksheet_costs = [all_periods_stats[p].get('cost', {}).get('worksheet_cost', 0) for p in periods]
        service_costs = [all_periods_stats[p].get('cost', {}).get('service_cost', 0) for p in periods]
        
        x = range(len(periods))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar([i - width/2 for i in x], worksheet_costs, width, label='Munkalap Költség', color='#10B981')
        bars2 = ax.bar([i + width/2 for i in x], service_costs, width, label='Szerviz Költség', color='#6366F1')
        
        ax.set_xlabel('Időszak', fontsize=12, fontweight='bold')
        ax.set_ylabel('Költség (€)', fontsize=12, fontweight='bold')
        ax.set_title('Költség Elemzés Időszakonként', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:,.0f}',
                           ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if output_path is None:
            charts_dir = _ensure_charts_dir()
            output_path = charts_dir / "cost_chart.png"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Verify file was created
        if not output_path.exists():
            logger.error(f"Failed to create chart file: {output_path}")
            return None
        
        logger.info(f"Cost chart generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating cost chart: {e}")
        return None


def generate_time_chart(all_periods_stats: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
    """Generate time comparison line chart"""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available, skipping chart generation")
        return None
    
    try:
        period_labels = {
            "day": "Nap",
            "week": "Hét",
            "month": "Hó",
            "year": "Év"
        }
        
        periods = list(all_periods_stats.keys())
        labels = [period_labels.get(p, p) for p in periods]
        
        downtime = [all_periods_stats[p].get('time', {}).get('worksheet_downtime_hours', 0) for p in periods]
        pm_time = [all_periods_stats[p].get('time', {}).get('pm_duration_hours', 0) for p in periods]
        service_time = [all_periods_stats[p].get('time', {}).get('service_duration_hours', 0) for p in periods]
        total_time = [all_periods_stats[p].get('time', {}).get('total_time_hours', 0) for p in periods]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(labels, downtime, marker='o', linewidth=2, label='Leállás', color='#EF4444')
        ax.plot(labels, pm_time, marker='s', linewidth=2, label='PM Idő', color='#F59E0B')
        ax.plot(labels, service_time, marker='^', linewidth=2, label='Szerviz Idő', color='#8B5CF6')
        ax.plot(labels, total_time, marker='D', linewidth=3, label='Összesen', color='#6366F1', linestyle='--')
        
        ax.set_xlabel('Időszak', fontsize=12, fontweight='bold')
        ax.set_ylabel('Idő (óra)', fontsize=12, fontweight='bold')
        ax.set_title('Idő Elemzés Időszakonként', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best')
        ax.grid(alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if output_path is None:
            charts_dir = _ensure_charts_dir()
            output_path = charts_dir / "time_chart.png"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Verify file was created
        if not output_path.exists():
            logger.error(f"Failed to create chart file: {output_path}")
            return None
        
        logger.info(f"Time chart generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating time chart: {e}")
        return None


def generate_tasks_chart(all_periods_stats: Dict, output_path: Optional[Path] = None) -> Optional[Path]:
    """Generate tasks comparison bar chart"""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available, skipping chart generation")
        return None
    
    try:
        period_labels = {
            "day": "Nap",
            "week": "Hét",
            "month": "Hó",
            "year": "Év"
        }
        
        periods = list(all_periods_stats.keys())
        labels = [period_labels.get(p, p) for p in periods]
        
        worksheets = [all_periods_stats[p].get('tasks', {}).get('worksheet_count', 0) for p in periods]
        pm_tasks = [all_periods_stats[p].get('tasks', {}).get('pm_count', 0) for p in periods]
        
        x = range(len(periods))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar([i - width/2 for i in x], worksheets, width, label='Munkalapok', color='#F59E0B')
        bars2 = ax.bar([i + width/2 for i in x], pm_tasks, width, label='PM Feladatok', color='#8B5CF6')
        
        ax.set_xlabel('Időszak', fontsize=12, fontweight='bold')
        ax.set_ylabel('Feladatok száma', fontsize=12, fontweight='bold')
        ax.set_title('Feladat Elemzés Időszakonként', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if output_path is None:
            charts_dir = _ensure_charts_dir()
            output_path = charts_dir / "tasks_chart.png"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Verify file was created
        if not output_path.exists():
            logger.error(f"Failed to create chart file: {output_path}")
            return None
        
        logger.info(f"Tasks chart generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating tasks chart: {e}")
        return None


def generate_tasks_pie_chart(all_periods_stats: Dict, period: str = "year", output_path: Optional[Path] = None) -> Optional[Path]:
    """Generate tasks pie chart for a specific period"""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available, skipping chart generation")
        return None
    
    try:
        stats = all_periods_stats.get(period, {})
        task_stats = stats.get('tasks', {})
        
        worksheet_count = task_stats.get('worksheet_count', 0)
        pm_count = task_stats.get('pm_count', 0)
        
        if worksheet_count == 0 and pm_count == 0:
            return None
        
        period_labels = {
            "day": "Nap",
            "week": "Hét",
            "month": "Hó",
            "year": "Év"
        }
        
        labels = ['Munkalapok', 'PM Feladatok']
        sizes = [worksheet_count, pm_count]
        colors = ['#F59E0B', '#8B5CF6']
        explode = (0.05, 0.05)  # Slight separation
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90,
                                         textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        period_label = period_labels.get(period, period)
        ax.set_title(f'Feladat Eloszlás ({period_label})', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if output_path is None:
            charts_dir = _ensure_charts_dir()
            output_path = charts_dir / f"tasks_pie_{period}.png"
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fig.savefig(str(output_path), dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Verify file was created
        if not output_path.exists():
            logger.error(f"Failed to create chart file: {output_path}")
            return None
        
        logger.info(f"Tasks pie chart generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating tasks pie chart: {e}")
        return None

