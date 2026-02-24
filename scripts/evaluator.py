import pandas as pd
import numpy as np

def calculate_ai_readiness(row):
    """
    Calculates a weighted score for AI Agent competency.
    Weights: 
    - Logic/Workflow: 40%
    - Tool Knowledge: 30% 
    - Safety/Ethics: 30%
    """
    logic_score = row['Logic_Workflow_Score'] * 0.4
    tool_score = row['Tool_Knowledge_Score'] * 0.3
    safety_score = row['Safety_Guardrail_Score'] * 0.3
    
    total_score = logic_score + tool_score + safety_score
    return round(total_score, 2)

def generate_recommendation(score):
    if score >= 4.5:
        return "TOP TIER: Agent Strategist (Immediate Hire)"
    elif score >= 3.5:
        return "STRONG: Workflow Builder (Recommended)"
    elif score >= 2.5:
        return "POTENTIAL: Power User (Needs Training)"
    else:
        return "NOVICE: Basic User (Not Recommended for AI Roles)"

def process_candidates(input_file):
    # Load data
    try:
        df = pd.read_csv(input_file)
    except:
        df = pd.read_excel(input_file)

    # Apply Scoring
    df['Final_AI_Score'] = df.apply(calculate_ai_readiness, axis=1)
    df['HR_Recommendation'] = df['Final_AI_Score'].apply(generate_recommendation)

    # Sort by highest score
    df = df.sort_values(by='Final_AI_Score', ascending=False)

    # Export results
    output_file = "candidate_evaluation_results.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Evaluation complete. Results saved to {output_file}")

if __name__ == "__main__":
    # Example usage:
    process_candidates('candidates.csv')
    print("AI Agent Talent Evaluator Script Loaded.")

