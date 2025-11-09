#!/usr/bin/env python3
"""
Health Check para o Sistema de Atualização do Dashboard

Verifica:
1. Se os arquivos de dados existem
2. Se o dashboard foi gerado
3. Se há dados suficientes
4. Status geral do sistema
"""

import json
from pathlib import Path
from datetime import datetime

class HealthCheck:
    def __init__(self):
        self.checks = {}
        self.data = {}

    def check_extraction_file(self):
        """Verifica se o arquivo de extração existe"""
        path = Path("/tmp/extracao_inteligente.json")
        exists = path.exists()

        if exists:
            try:
                with open(path) as f:
                    data = json.load(f)
                    # Nova estrutura: data["atual"]["registros"]
                    # Estrutura antiga: data["professionals"]
                    count = 0
                    if isinstance(data, dict):
                        if "atual" in data and "registros" in data["atual"]:
                            count = len(data["atual"]["registros"])
                        elif "professionals" in data:
                            count = len(data["professionals"])

                    self.checks["extraction_file"] = f"✅ {count} professionals"
                    self.data["professionals_count"] = count
                    return True
            except Exception as e:
                self.checks["extraction_file"] = f"⚠️ File exists but invalid: {str(e)[:30]}"
                return False
        else:
            self.checks["extraction_file"] = "⚠️ File not found"
            return False

    def check_previous_day_file(self):
        """Verifica se o arquivo de dia anterior existe"""
        path = Path("/tmp/extracao_inteligente_anterior.json")
        exists = path.exists()

        if exists:
            try:
                with open(path) as f:
                    data = json.load(f)
                    # Nova estrutura: data["anterior"]["registros"]
                    # Estrutura antiga: data["professionals"]
                    count = 0
                    if isinstance(data, dict):
                        if "anterior" in data and "registros" in data["anterior"]:
                            count = len(data["anterior"]["registros"])
                        elif "professionals" in data:
                            count = len(data["professionals"])

                    self.checks["previous_day_file"] = f"✅ {count} professionals"
                    self.data["previous_day_count"] = count
                    return True
            except Exception as e:
                self.checks["previous_day_file"] = f"⚠️ File exists but invalid: {str(e)[:30]}"
                return False
        else:
            # This is not critical since we have fallback
            self.checks["previous_day_file"] = "⚠️ File not found (fallback available)"
            return False

    def check_dashboard_exists(self):
        """Verifica se o dashboard foi gerado"""
        desktop = Path("index.html")
        tmp = Path("/tmp/dashboard_executivo.html")

        desktop_exists = desktop.exists()
        tmp_exists = tmp.exists()

        if desktop_exists:
            self.checks["dashboard_html"] = "✅ index.html found"
            return True
        elif tmp_exists:
            self.checks["dashboard_html"] = "✅ /tmp/dashboard_executivo.html found"
            return True
        else:
            self.checks["dashboard_html"] = "❌ Dashboard not found"
            return False

    def check_workflows(self):
        """Verifica se há workflow configurado"""
        workflow_dir = Path(".github/workflows")
        workflows = list(workflow_dir.glob("*.yml"))

        if workflows:
            count = len(workflows)
            names = [w.name for w in workflows]
            self.checks["workflows"] = f"✅ {count} workflow(s): {', '.join(names)}"
            return len(workflows) == 1  # Should have exactly 1
        else:
            self.checks["workflows"] = "❌ No workflows found"
            return False

    def check_fallback_data(self):
        """Verifica se dados de fallback estão disponíveis"""
        path = Path("data/extracao_inteligente_sample.json")
        exists = path.exists()

        if exists:
            self.checks["fallback_data"] = "✅ Fallback data available"
            return True
        else:
            self.checks["fallback_data"] = "⚠️ No fallback data"
            return False

    def run_all_checks(self):
        """Executa todas as verificações"""
        print("\n" + "="*60)
        print("🏥 DASHBOARD HEALTH CHECK")
        print("="*60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.check_extraction_file()
        self.check_previous_day_file()
        self.check_dashboard_exists()
        self.check_workflows()
        self.check_fallback_data()

        # Print results
        for check_name, status in self.checks.items():
            print(f"{status}")

        # Summary
        print("\n" + "-"*60)

        # CRITICAL: Dashboard must exist
        dashboard_ok = "✅" in self.checks["dashboard_html"]

        # Data must be available from SOME source
        has_data = (
            "✅" in self.checks["extraction_file"] or
            "✅" in self.checks["previous_day_file"] or
            "✅" in self.checks["fallback_data"]
        )

        # Workflows must be valid
        workflows_ok = "✅" in self.checks["workflows"]

        # System is healthy if dashboard exists, has data, and workflows are configured
        is_healthy = dashboard_ok and has_data and workflows_ok

        if is_healthy:
            print("✅ SYSTEM STATUS: HEALTHY")
            print("\nData Summary:")
            if self.data.get("professionals_count"):
                print(f"  • Today: {self.data['professionals_count']} professionals")
            if self.data.get("previous_day_count"):
                print(f"  • Yesterday: {self.data['previous_day_count']} professionals")
            return True
        else:
            # Only fail if something CRITICAL is missing
            if not dashboard_ok:
                print("❌ SYSTEM STATUS: FAILED - Dashboard not generated")
            elif not has_data:
                print("❌ SYSTEM STATUS: FAILED - No data available")
            elif not workflows_ok:
                print("❌ SYSTEM STATUS: FAILED - Workflow not configured")
            else:
                print("⚠️ SYSTEM STATUS: DEGRADED (using fallback)")
            return False

def main():
    health = HealthCheck()
    is_healthy = health.run_all_checks()
    print("="*60 + "\n")
    exit(0 if is_healthy else 1)

if __name__ == "__main__":
    main()
