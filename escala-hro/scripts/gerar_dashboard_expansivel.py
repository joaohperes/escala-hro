#!/usr/bin/env python3
"""
Gera dashboard elegante com botões de expansão/colapso
"""

import json

with open('/tmp/extracao_inteligente.json') as f:
    data = json.load(f)

registros = data['registros']
data_escala = data['data']

# Cores elegantes e profissionais
cores_elegante = {
    'Emergência': '#E74C3C',
    'UTI': '#3498DB',
    'Cirurgia': '#9B59B6',
    'Obstetrícia': '#F39C12',
    'Clínica': '#16A085',
    'Ambulatório': '#D35400',
    'Residência': '#2C3E50'
}

def get_category(setor):
    setor_lower = setor.lower()
    if any(x in setor_lower for x in ['uti', 'terapia intensiva']):
        return 'UTI'
    elif any(x in setor_lower for x in ['gineco', 'obstet']):
        return 'Obstetrícia'
    elif any(x in setor_lower for x in ['cirurgia', 'transplante', 'vascular']):
        return 'Cirurgia'
    elif any(x in setor_lower for x in ['clínica', 'comanejo', 'hospitalista']):
        return 'Clínica'
    elif any(x in setor_lower for x in ['emergência', 'pronto', 'urgência']):
        return 'Emergência'
    elif any(x in setor_lower for x in ['ambulatório', 'oncologia']):
        return 'Ambulatório'
    elif any(x in setor_lower for x in ['residência', 'residencia']):
        return 'Residência'
    else:
        return 'Especialidades'

# Agrupar por categoria
categorias = {}
for reg in registros:
    cat = get_category(reg['setor'])
    if cat not in categorias:
        categorias[cat] = []
    categorias[cat].append(reg)

# Contar profissionais por categoria
stats = {cat: len(profs) for cat, profs in categorias.items()}

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escala HRO - {data_escala}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
            letter-spacing: 1px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }}

        .container {{
            max-width: 1500px;
            margin: 0 auto;
            padding: 30px 20px;
        }}

        .search-section {{
            margin-bottom: 40px;
            display: flex;
            justify-content: center;
        }}

        .search-bar {{
            width: 100%;
            max-width: 600px;
            position: relative;
        }}

        .search-bar input {{
            width: 100%;
            padding: 15px 20px;
            font-size: 1em;
            border: 2px solid #ecf0f1;
            border-radius: 4px;
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s;
            background: white;
        }}

        .search-bar input:focus {{
            border-color: #2a5298;
            box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #2a5298;
        }}

        .stat-card h3 {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: 300;
            color: #2c3e50;
        }}

        .categorias {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 25px;
        }}

        .categoria {{
            background: white;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s;
        }}

        .categoria:hover {{
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}

        .categoria-header {{
            padding: 20px;
            color: white;
            font-weight: 600;
            font-size: 1.1em;
            display: flex;
            justify-content: space-between;
            align-items: center;
            letter-spacing: 0.5px;
            cursor: pointer;
            user-select: none;
            transition: opacity 0.2s;
        }}

        .categoria-header:hover {{
            opacity: 0.9;
        }}

        .categoria-header .toggle {{
            font-size: 1.3em;
            transition: transform 0.3s ease;
        }}

        .categoria-header.expanded .toggle {{
            transform: rotate(180deg);
        }}

        .categoria-count {{
            background: rgba(255,255,255,0.25);
            padding: 4px 12px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .categoria-content {{
            padding: 0;
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.3s ease, opacity 0.3s ease;
            opacity: 1;
        }}

        .categoria-content.collapsed {{
            max-height: 0;
            opacity: 0;
        }}

        .profissional {{
            padding: 16px 20px;
            border-bottom: 1px solid #ecf0f1;
            transition: background-color 0.2s;
        }}

        .profissional:last-child {{
            border-bottom: none;
        }}

        .profissional:hover {{
            background-color: #f8f9fa;
        }}

        .profissional-nome {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 6px;
            font-size: 1em;
        }}

        .profissional-setor {{
            font-size: 0.9em;
            color: #34495e;
            margin-bottom: 4px;
        }}

        .profissional-info {{
            font-size: 0.85em;
            color: #7f8c8d;
        }}

        .controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background: #2a5298;
            color: white;
            cursor: pointer;
            font-size: 0.95em;
            transition: background 0.3s;
        }}

        .btn:hover {{
            background: #1e3c72;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            .categorias {{
                grid-template-columns: 1fr;
            }}
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ESCALA HRO</h1>
        <p>{data_escala}</p>
    </div>

    <div class="container">
        <div class="search-section">
            <div class="search-bar">
                <input type="text" id="search" placeholder="Buscar profissional, setor ou turno..." onkeyup="filtrarProfissionais()">
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Profissionais</h3>
                <div class="number">{len(registros)}</div>
            </div>
            <div class="stat-card">
                <h3>Especialidades</h3>
                <div class="number">{len(stats)}</div>
            </div>
            <div class="stat-card">
                <h3>Data</h3>
                <div class="number" style="font-size: 1.5em;">{data_escala.split()[0]} de out</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn" onclick="expandirTodas()">Expandir Tudo</button>
            <button class="btn" onclick="colapsarTodas()">Colapsar Tudo</button>
        </div>

        <div class="categorias" id="categorias">
'''

# Cores para as categorias
cores_ordem = ['Emergência', 'UTI', 'Cirurgia', 'Obstetrícia', 'Clínica', 'Ambulatório', 'Residência', 'Especialidades']

for cat in cores_ordem:
    if cat in categorias:
        cor = cores_elegante.get(cat, '#34495e')
        count = len(categorias[cat])

        html += f'''            <div class="categoria">
                <div class="categoria-header expanded" style="background-color: {cor};" onclick="toggleCategoria(this)">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                        <span>{cat}</span>
                        <span class="categoria-count">{count}</span>
                    </div>
                    <span class="toggle">▼</span>
                </div>
                <div class="categoria-content">
'''

        for prof in categorias[cat]:
            html += f'''                    <div class="profissional" data-search="{prof['profissional'].lower()} {prof['setor'].lower()} {prof['tipo_turno'].lower()}">
                        <div class="profissional-nome">{prof['profissional']}</div>
                        <div class="profissional-setor">{prof['setor']}</div>
                        <div class="profissional-info">{prof['horario']} • {prof['tipo_turno']}</div>
                    </div>
'''

        html += '''                </div>
            </div>
'''

html += '''        </div>
    </div>

    <script>
        function toggleCategoria(header) {
            const content = header.nextElementSibling;
            header.classList.toggle('expanded');
            content.classList.toggle('collapsed');
        }

        function expandirTodas() {
            const headers = document.querySelectorAll('.categoria-header');
            const contents = document.querySelectorAll('.categoria-content');

            headers.forEach(h => h.classList.add('expanded'));
            contents.forEach(c => c.classList.remove('collapsed'));
        }

        function colapsarTodas() {
            const headers = document.querySelectorAll('.categoria-header');
            const contents = document.querySelectorAll('.categoria-content');

            headers.forEach(h => h.classList.remove('expanded'));
            contents.forEach(c => c.classList.add('collapsed'));
        }

        function filtrarProfissionais() {
            const searchText = document.getElementById('search').value.toLowerCase();
            const profissionais = document.querySelectorAll('.profissional');
            let temResultado = false;

            profissionais.forEach(prof => {
                const texto = prof.getAttribute('data-search');
                if (searchText === '' || texto.includes(searchText)) {
                    prof.style.display = 'block';
                    temResultado = true;
                } else {
                    prof.style.display = 'none';
                }
            });

            // Auto expandir se há resultados de busca
            if (searchText !== '') {
                expandirTodas();
            }
        }
    </script>
</body>
</html>
'''

with open('/tmp/escala_hro_dashboard_expansivel.html', 'w') as f:
    f.write(html)

print("✅ Dashboard com expansão/colapso criado!")
print("📍 Arquivo: /tmp/escala_hro_dashboard_expansivel.html")
print("\n🎯 Recursos:")
print("   ✓ Botões 'Expandir Tudo' e 'Colapsar Tudo'")
print("   ✓ Clique nos headers para expandir/colapsar categorias")
print("   ✓ Auto-expande ao buscar")
print("   ✓ Design elegante e profissional")
