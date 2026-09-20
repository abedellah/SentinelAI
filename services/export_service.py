import json
from datetime import datetime
from bson import ObjectId
from fpdf import FPDF

class ExportService:
    """Service d'export PDF et JSON"""
    
    @staticmethod
    def to_json_serializable(obj):
        """Convertit les types MongoDB en types JSON"""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: ExportService.to_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [ExportService.to_json_serializable(i) for i in obj]
        return obj
    
    @staticmethod
    def export_logs_json(logs):
        """Export logs en JSON"""
        serializable_logs = ExportService.to_json_serializable(logs)
        return json.dumps(serializable_logs, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_alerts_json(alerts):
        """Export alerts en JSON"""
        serializable_alerts = ExportService.to_json_serializable(alerts)
        return json.dumps(serializable_alerts, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_logs_pdf(logs, filename='logs_export.pdf'):
        """Export logs en PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'SentinelAI - Export Logs', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
        pdf.cell(0, 10, f'Total logs: {len(logs)}', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 10)
        for log in logs[:50]:  # Limiter à 50 pour PDF
            pdf.cell(0, 5, f"Log ID: {log['_id']}", ln=True)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 5, f"  Source: {log.get('source_ip', 'N/A')} -> Dest: {log.get('destination_ip', 'N/A')}", ln=True)
            pdf.cell(0, 5, f"  Label: {log.get('Label', 'N/A')} | Port: {log.get('destination_port', 'N/A')}", ln=True)
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 10)
        
        pdf.output(filename)
        return filename
    
    @staticmethod
    def export_alerts_pdf(alerts, filename='alerts_export.pdf'):
        """Export alerts en PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'SentinelAI - Export Alertes', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
        pdf.cell(0, 10, f'Total alertes: {len(alerts)}', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 10)
        for alert in alerts[:50]:
            pdf.cell(0, 5, f"Alerte ID: {alert['_id']}", ln=True)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 5, f"  Type: {alert.get('alert_type', 'N/A')} | Score: {alert.get('score_risk', 0)}/10", ln=True)
            pdf.cell(0, 5, f"  Status: {alert.get('status', 'N/A')}", ln=True)
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 10)
        
        pdf.output(filename)
        return filename