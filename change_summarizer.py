import os
import openai
from typing import Dict, List, Any

class ChangeSummarizer:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key

    async def analyze_changes(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze changes using OpenAI API and add summaries"""
        for change in changes:
            if change['type'] == 'site_check':
                continue

            try:
                # Prepare context based on change type
                context = self._prepare_change_context(change)
                
                # Generate analysis using OpenAI
                analysis = await self._generate_analysis(context)
                
                # Add analysis to change object
                change['analysis'] = analysis
                
            except Exception as e:
                print(f"Error analyzing change: {str(e)}")
                change['analysis'] = {
                    'explanation': 'Analysis unavailable',
                    'impact_category': 'Unknown',
                    'business_relevance': 'Unknown',
                    'recommendations': 'Unable to analyze this change'
                }

        return changes

    def _prepare_change_context(self, change: Dict[str, Any]) -> str:
        """Prepare context for AI analysis based on change type"""
        change_type = change['type']
        context = f"Analyze this website change:\n"
        
        if change_type in ['text_change', 'menu_structure_change']:
            context += f"""
Type: {change_type}
Location: {change['location']}
Before: {change.get('before', 'N/A')}
After: {change.get('after', 'N/A')}
            """
        elif change_type in ['links_added', 'links_removed']:
            context += f"""
Type: {change_type}
Location: {change['location']}
Changed Links: {change.get('after', '') or change.get('before', '')}
            """
            
        return context.strip()

    async def _generate_analysis(self, context: str) -> Dict[str, str]:
        """Generate analysis using OpenAI API"""
        prompt = f"""
{context}

Analyze this website change and provide:
1. A brief explanation of what changed
2. The impact category (Content, Structure, Navigation, Visual, or Technical)
3. Business relevance (Low, Medium, High, or Critical)
4. Specific recommendations for action

Format the response as JSON with the following keys:
- explanation
- impact_category
- business_relevance
- recommendations
"""

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert website analyst focusing on business impact."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and parse the JSON response
            analysis_text = response.choices[0].message.content
            
            # Note: In a real implementation, we'd need to properly parse the JSON
            # For now, we'll return a structured dict
            return {
                'explanation': analysis_text[:200],  # Truncate for brevity
                'impact_category': self._determine_impact_category(analysis_text),
                'business_relevance': self._determine_business_relevance(analysis_text),
                'recommendations': self._extract_recommendations(analysis_text)
            }
        except Exception as e:
            print(f"Error generating analysis: {str(e)}")
            raise

    def _determine_impact_category(self, analysis: str) -> str:
        """Extract impact category from analysis"""
        categories = ['Content', 'Structure', 'Navigation', 'Visual', 'Technical']
        for category in categories:
            if category.lower() in analysis.lower():
                return category
        return 'Content'  # Default category

    def _determine_business_relevance(self, analysis: str) -> str:
        """Extract business relevance from analysis"""
        relevance_levels = ['Critical', 'High', 'Medium', 'Low']
        for level in relevance_levels:
            if level.lower() in analysis.lower():
                return level
        return 'Medium'  # Default relevance

    def _extract_recommendations(self, analysis: str) -> str:
        """Extract recommendations from analysis"""
        try:
            # Look for recommendations after "recommendations" keyword
            if 'recommendations' in analysis.lower():
                recommendations = analysis.lower().split('recommendations')[1].split('\n')[0]
                return recommendations.strip()
            return "No specific recommendations provided"
        except:
            return "Unable to extract recommendations"
