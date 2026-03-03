from flask import Flask, render_template_string, request, redirect, url_for, send_file
import pandas as pd
import os

# Get port from environment variable for Render compatibility

app = Flask(__name__)
app.secret_key = 'ai-talent-assessment-secret-key'

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent 人才評估系統</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #6c757d;
        }
        .candidate-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .score-group {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .score-field {
            background: white;
            padding: 15px;
            border-radius: 10px;
        }
        .score-field label { font-size: 14px; }
        .score-field small {
            display: block;
            margin-top: 5px;
            color: #666;
            font-size: 12px;
        }
        .candidates-list {
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover { background: #f8f9fa; }
        .score { font-weight: bold; }
        .score-high { color: #28a745; }
        .score-mid { color: #ffc107; }
        .score-low { color: #dc3545; }
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-top { background: #d4edda; color: #155724; }
        .badge-strong { background: #cce5ff; color: #004085; }
        .badge-potential { background: #fff3cd; color: #856404; }
        .badge-novice { background: #f8d7da; color: #721c24; }
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .alert {
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-info { background: #cce5ff; color: #004085; }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty-state svg {
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Agent 人才評估系統</h1>
            <p>根據 Logic/Workflow、Tool Knowledge、Safety/Ethics 三個維度評估候選人</p>
        </div>
        
        <div class="content">
            {% if message %}
            <div class="alert alert-{{ message_type }}">
                {{ message }}
            </div>
            {% endif %}
            
            <form method="POST" action="/add">
                <div class="candidate-form">
                    <div class="form-group">
                        <label>👤 候選人姓名</label>
                        <input type="text" name="name" placeholder="例如：張三" required>
                    </div>
                    
                    <div class="form-group">
                        <label>🏢 部門</label>
                        <input type="text" name="department" placeholder="例如：Marketing" required>
                    </div>
                    
                    <div class="form-group">
                        <label>📊 評估分數 (1-5)</label>
                        <div class="score-group">
                            <div class="score-field">
                                <label>Logic/Workflow (40%)</label>
                                <input type="number" name="logic_score" min="1" max="5" step="0.1" placeholder="1-5" required>
                                <small>分析問題、流程設計能力</small>
                            </div>
                            <div class="score-field">
                                <label>Tool Knowledge (30%)</label>
                                <input type="number" name="tool_score" min="1" max="5" step="0.1" placeholder="1-5" required>
                                <small>AI 工具使用熟練度</small>
                            </div>
                            <div class="score-field">
                                <label>Safety/Ethics (30%)</label>
                                <input type="number" name="safety_score" min="1" max="5" step="0.1" placeholder="1-5" required>
                                <small>AI 安全同倫理意識</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">➕ 新增候選人</button>
            </form>
            
            <div class="candidates-list">
                <h2>📋 評估結果</h2>
                
                {% if candidates %}
                <table>
                    <thead>
                        <tr>
                            <th>候選人</th>
                            <th>部門</th>
                            <th>Logic</th>
                            <th>Tool</th>
                            <th>Safety</th>
                            <th>總分</th>
                            <th>建議</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for c in candidates %}
                        <tr>
                            <td><strong>{{ c.name }}</strong></td>
                            <td>{{ c.department }}</td>
                            <td>{{ c.logic_score }}</td>
                            <td>{{ c.tool_score }}</td>
                            <td>{{ c.safety_score }}</td>
                            <td class="score {% if c.final_score >= 4.5 %}score-high{% elif c.final_score >= 2.5 %}score-mid{% else %}score-low{% endif %}">
                                {{ c.final_score }}
                            </td>
                            <td>
                                {% if c.recommendation == 'TOP TIER' %}
                                <span class="badge badge-top">🌟 Agent Strategist</span>
                                {% elif c.recommendation == 'STRONG' %}
                                <span class="badge badge-strong">💪 Workflow Builder</span>
                                {% elif c.recommendation == 'POTENTIAL' %}
                                <span class="badge badge-potential">📚 Power User</span>
                                {% else %}
                                <span class="badge badge-novice">❌ Basic User</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="actions">
                    <a href="/download"><button class="btn btn-secondary">📥 下載 CSV</button></a>
                    <a href="/clear"><button class="btn btn-secondary" style="background: #dc3545;">🗑️ 清除全部</button></a>
                </div>
                {% else %}
                <div class="empty-state">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                    <p>暫時未有候選人資料</p>
                    <p>請輸入上方資料開始評估</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
'''

# 計算分數既 function
def calculate_ai_readiness(logic_score, tool_score, safety_score):
    """計算加權分數"""
    logic_weight = 0.4
    tool_weight = 0.3
    safety_weight = 0.3
    
    total = (logic_score * logic_weight + 
             tool_score * tool_weight + 
             safety_score * safety_weight)
    return round(total, 2)

def generate_recommendation(score):
    """產生聘請建議"""
    if score >= 4.5:
        return "TOP TIER"
    elif score >= 3.5:
        return "STRONG"
    elif score >= 2.5:
        return "POTENTIAL"
    else:
        return "NOVICE"

# 簡單既資料儲存（用 JSON file）
DATA_FILE = '/app/data/candidates_data.json'

def load_candidates():
    if os.path.exists(DATA_FILE):
        try:
            import json
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_candidates(candidates):
    import json
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    candidates = load_candidates()
    
    # 計算每個候選人既分數同建議
    processed = []
    for c in candidates:
        final_score = calculate_ai_readiness(c['logic_score'], c['tool_score'], c['safety_score'])
        recommendation = generate_recommendation(final_score)
        processed.append({
            'name': c['name'],
            'department': c['department'],
            'logic_score': c['logic_score'],
            'tool_score': c['tool_score'],
            'safety_score': c['safety_score'],
            'final_score': final_score,
            'recommendation': recommendation
        })
    
    # 按分數排序
    processed.sort(key=lambda x: x['final_score'], reverse=True)
    
    return render_template_string(HTML_TEMPLATE, candidates=processed)

@app.route('/add', methods=['POST'])
def add_candidate():
    name = request.form.get('name')
    department = request.form.get('department')
    logic_score = float(request.form.get('logic_score', 0))
    tool_score = float(request.form.get('tool_score', 0))
    safety_score = float(request.form.get('safety_score', 0))
    
    candidates = load_candidates()
    candidates.append({
        'name': name,
        'department': department,
        'logic_score': logic_score,
        'tool_score': tool_score,
        'safety_score': safety_score
    })
    save_candidates(candidates)
    
    return redirect(url_for('index'))

@app.route('/download')
def download_csv():
    candidates = load_candidates()
    
    if not candidates:
        return redirect(url_for('index'))
    
    # 建立 DataFrame
    data = []
    for c in candidates:
        final_score = calculate_ai_readiness(c['logic_score'], c['tool_score'], c['safety_score'])
        recommendation = generate_recommendation(final_score)
        
        rec_text = {
            'TOP TIER': 'Agent Strategist (Immediate Hire)',
            'STRONG': 'Workflow Builder (Recommended)',
            'POTENTIAL': 'Power User (Needs Training)',
            'NOVICE': 'Basic User (Not Recommended for AI Roles)'
        }
        
        data.append({
            'Candidate_Name': c['name'],
            'Department': c['department'],
            'Logic_Workflow_Score': c['logic_score'],
            'Tool_Knowledge_Score': c['tool_score'],
            'Safety_Guardrail_Score': c['safety_score'],
            'Final_AI_Score': final_score,
            'HR_Recommendation': rec_text[recommendation]
        })
    
    df = pd.DataFrame(data)
    output_file = '/app/data/candidate_evaluation_results.csv'
    df.to_csv(output_file, index=False)
    
    return send_file(output_file, as_attachment=True, download_name='evaluation_results.csv')

@app.route('/clear')
def clear_all():
    save_candidates([])
    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 啟動 AI Agent 人才評估系統...")
    print(f"📍 請訪問: http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)