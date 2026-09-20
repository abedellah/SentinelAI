# services/risk_scoring.py
class RiskScorer:
    """Calcul du score de risque (0-10)"""
    
    # Mapping sévérité par type d'attaque
    SEVERITY_MAP = {
        'BENIGN': 0.0,
        'PortScan': 3.0,
        'DoS Hulk': 8.0,
        'DoS GoldenEye': 8.0,
        'DoS slowloris': 7.5,
        'DoS Slowhttptest': 7.5,
        'DDoS': 9.0,
        'FTP-Patator': 6.0,
        'SSH-Patator': 6.5,
        'Web Attack - Brute Force': 7.0,
        'Web Attack - XSS': 7.5,
        'Web Attack - Sql Injection': 8.5,
        'Bot': 8.0,
        'Infiltration': 9.5,
        'Heartbleed': 10.0
    }
    
    @staticmethod
    def calculate_risk(label, confidence, log_data):
        """Calcule le score de risque basé sur label, confiance et caractéristiques"""
        base_score = RiskScorer.SEVERITY_MAP.get(label, 5.0)
        
        # Ajustement par confiance
        confidence_factor = confidence * 1.2
        
        # Facteurs additionnels
        flow_factor = 0
        if log_data.get('flow_bytes_per_second', 0) > 100000:
            flow_factor += 0.5
        if log_data.get('flow_packets_per_second', 0) > 1000:
            flow_factor += 0.5
        
        # Calcul final
        final_score = min(10.0, base_score * confidence_factor + flow_factor)
        
        return round(final_score, 2)