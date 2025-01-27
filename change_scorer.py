from openai import OpenAI
import os
from typing import Dict, Any, List, Tuple
import json

class ChangeScorer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def analyze_change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single change and return significance score with explanation"""
        
        # Prepare the change description for analysis
        change_description = self._format_change_for_analysis(change)
        
        try:
            # Get AI analysis of the change
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    You are a website change analyzer. Analyze the provided website change and:
                    1. Assign a significance score (1-10)
                    2. Provide a brief explanation of the score
                    3. Categorize the impact (Visual, Content, Structure, or Technical)
                    4. Assess business relevance
                    
                    Return the analysis in JSON format with these keys:
                    {
                        "score": int,
                        "explanation": string,
                        "impact_category": string,
                        "business_relevance": string,
                        "recommendations": string
                    }
                    """},
                    {"role": "user", "content": f"Analyze this website change:\n{change_description}"}
                ]
            )
            
            # Parse the AI response
            analysis = json.loads(response.choices[0].message.content)
            
            # Add the analysis to the change dict
            change.update({
                "significance_score": analysis["score"],
                "analysis": {
                    "explanation": analysis["explanation"],
                    "impact_category": analysis["impact_category"],
                    "business_relevance": analysis["business_relevance"],
                    "recommendations": analysis["recommendations"]
                }
            })
            
            return change
            
        except Exception as e:
            # If AI analysis fails, provide a basic score
            change.update({
                "significance_score": 5,
                "analysis": {
                    "explanation": "Automated scoring unavailable",
                    "impact_category": "Unknown",
                    "business_relevance": "Could not determine",
                    "recommendations": "Manual review recommended"
                }
            })
            return change
    
    def _format_change_for_analysis(self, change: Dict[str, Any]) -> str:
        """Format the change data for AI analysis"""
        description = f"Change Type: {change['type']}\n"
        description += f"Location: {change['location']}\n"
        
        if 'before' in change:
            description += f"Previous Content:\n{change['before']}\n"
        if 'after' in change:
            description += f"New Content:\n{change['after']}\n"
            
        return description
    
    def score_changes(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score a list of changes and sort by significance"""
        scored_changes = []
        
        for change in changes:
            scored_change = self.analyze_change(change)
            scored_changes.append(scored_change)
            
        # Sort changes by significance score in descending order
        return sorted(scored_changes, 
                     key=lambda x: x.get('significance_score', 0), 
                     reverse=True)
