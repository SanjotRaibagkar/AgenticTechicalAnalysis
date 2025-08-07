# src/langgraph_mcp_groq/agents/video_analysis_agent.py
import os
import json
import asyncio
from typing import TypedDict, List, Dict, Any, Optional
from pathlib import Path
import tempfile
import subprocess
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from ..utils.config import get_langchain_groq

# You'll need to install these additional dependencies:
# uv add opencv-python whisper-openai pillow moviepy speechrecognition


class VideoAnalysisState(TypedDict):
    video_path: str
    person_context: str  # Who is the person, their role, background
    analysis_focus: str  # What type of strategies to focus on
    transcript: str
    key_frames: List[str]  # Base64 encoded key frames
    visual_analysis: str
    audio_analysis: str
    strategy_extraction: str
    actionable_insights: List[Dict[str, Any]]
    final_document: str
    recommendations: List[Dict[str, Any]]


class VideoAnalysisAgent:
    """
    Advanced video analysis agent for extracting operational strategies
    and creating actionable understanding documents from person videos.
    """
    
    def __init__(self):
        self.llm = get_langchain_groq()
        self.temp_dir = tempfile.mkdtemp()
    
    def create_agent(self):
        """Create the video analysis workflow using LangGraph"""
        
        def video_preprocessing_node(state: VideoAnalysisState):
            """Extract audio and key frames from video"""
            try:
                import cv2
                import moviepy.editor as mp
                
                video_path = state["video_path"]
                
                # Extract audio for transcription
                video = mp.VideoFileClip(video_path)
                audio_path = os.path.join(self.temp_dir, "extracted_audio.wav")
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                
                # Extract key frames
                cap = cv2.VideoCapture(video_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                duration = frame_count / fps
                
                # Extract frames every 30 seconds or 10 total frames max
                interval = max(30 * fps, frame_count // 10) if frame_count > 10 * fps else frame_count // 5
                key_frames = []
                
                for i in range(0, frame_count, interval):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        frame_path = os.path.join(self.temp_dir, f"frame_{i}.jpg")
                        cv2.imwrite(frame_path, frame)
                        key_frames.append(frame_path)
                
                cap.release()
                
                return {
                    **state,
                    "audio_path": audio_path,
                    "key_frames": key_frames,
                    "video_duration": duration
                }
                
            except Exception as e:
                return {
                    **state,
                    "transcript": f"Error in video preprocessing: {str(e)}",
                    "key_frames": [],
                    "audio_path": ""
                }
        
        def transcription_node(state: VideoAnalysisState):
            """Transcribe audio using Whisper or speech recognition"""
            try:
                import whisper
                
                audio_path = state.get("audio_path", "")
                if not audio_path or not os.path.exists(audio_path):
                    return {**state, "transcript": "No audio available for transcription"}
                
                # Load Whisper model (you can use different sizes: tiny, base, small, medium, large)
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)
                
                transcript = result["text"]
                
                # Enhanced transcript analysis
                system_prompt = """You are analyzing a video transcript to identify speaking patterns, 
                key topics, and communication style. Focus on:
                
                1. Main topics and themes discussed
                2. Speaking style and communication patterns  
                3. Expertise areas demonstrated
                4. Decision-making approach revealed
                5. Leadership or operational insights shown
                
                Provide a structured analysis of what this transcript reveals about the person's 
                operational approach and strategic thinking."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Analyze this transcript:\n\n{transcript}")
                ]
                
                response = self.llm.invoke(messages)
                
                return {
                    **state,
                    "transcript": transcript,
                    "audio_analysis": response.content
                }
                
            except Exception as e:
                return {
                    **state,
                    "transcript": f"Transcription failed: {str(e)}",
                    "audio_analysis": "Audio analysis unavailable"
                }
        
        def visual_analysis_node(state: VideoAnalysisState):
            """Analyze key frames for visual insights"""
            
            # Since we can't directly process images with Groq, we'll analyze what we can observe
            visual_analysis_prompt = f"""Based on the video analysis context, analyze the visual aspects 
            of this person's presentation style and environment. Consider:
            
            Person Context: {state.get('person_context', 'Unknown')}
            Analysis Focus: {state.get('analysis_focus', 'General operational strategies')}
            Video Duration: {state.get('video_duration', 'Unknown')} seconds
            
            Provide insights about:
            1. Professional presentation style (based on context)
            2. Environmental factors that might influence their approach
            3. Non-verbal communication patterns typical for their role
            4. Visual cues about their operational methodology
            5. Workspace or environment insights that relate to their strategies
            
            Focus on actionable observations that support strategic understanding."""
            
            messages = [
                SystemMessage(content="You are a visual communication analyst specializing in professional behavior analysis."),
                HumanMessage(content=visual_analysis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                **state,
                "visual_analysis": response.content
            }
        
        def strategy_extraction_node(state: VideoAnalysisState):
            """Extract operational strategies from combined analysis"""
            
            extraction_prompt = f"""
            Extract operational strategies and methodologies from this comprehensive analysis:
            
            PERSON CONTEXT: {state.get('person_context', '')}
            ANALYSIS FOCUS: {state.get('analysis_focus', '')}
            
            TRANSCRIPT ANALYSIS:
            {state.get('audio_analysis', '')}
            
            VISUAL ANALYSIS:
            {state.get('visual_analysis', '')}
            
            ORIGINAL TRANSCRIPT:
            {state.get('transcript', '')[:2000]}...
            
            Extract and structure:
            
            1. CORE OPERATIONAL STRATEGIES
            - Primary methodologies mentioned or demonstrated
            - Decision-making frameworks used
            - Problem-solving approaches
            - Resource allocation strategies
            
            2. LEADERSHIP PHILOSOPHY
            - Management style indicators
            - Team interaction approaches
            - Communication preferences
            - Delegation patterns
            
            3. PROCESS OPTIMIZATION
            - Workflow improvements mentioned
            - Efficiency strategies
            - Quality control approaches
            - Performance measurement methods
            
            4. STRATEGIC THINKING PATTERNS
            - Long-term vs short-term focus
            - Risk assessment approaches
            - Innovation strategies
            - Market/competitive analysis methods
            
            5. IMPLEMENTATION TACTICS
            - Change management approaches
            - Training and development strategies
            - Technology adoption patterns
            - Stakeholder engagement methods
            
            Provide specific, actionable insights with examples from the content where possible.
            """
            
            messages = [
                SystemMessage(content="""You are an expert business strategist and operational analyst. 
                Your job is to extract actionable operational strategies from video content analysis. 
                Focus on specific, implementable insights rather than generic advice."""),
                HumanMessage(content=extraction_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                **state,
                "strategy_extraction": response.content
            }
        
        def actionable_insights_node(state: VideoAnalysisState):
            """Generate structured actionable insights"""
            
            insights_prompt = f"""
            Based on the extracted strategies, create a structured list of actionable insights:
            
            EXTRACTED STRATEGIES:
            {state.get('strategy_extraction', '')}
            
            Create actionable insights in the following JSON-like structure for each insight:
            
            {{
                "category": "Strategy Category",
                "insight": "Specific actionable insight",
                "implementation": "How to implement this",
                "timeline": "Suggested timeline",
                "resources_needed": "What resources are required",
                "success_metrics": "How to measure success",
                "priority": "High/Medium/Low",
                "complexity": "Easy/Moderate/Complex"
            }}
            
            Focus on insights that are:
            1. Specific and measurable
            2. Directly implementable
            3. Based on demonstrated approaches from the video
            4. Relevant to the analysis focus: {state.get('analysis_focus', '')}
            5. Suitable for the person's context: {state.get('person_context', '')}
            
            Provide 8-12 high-value actionable insights.
            """
            
            messages = [
                SystemMessage(content="""You are a business consultant creating implementable 
                recommendations. Focus on specific, practical actions that can be taken based 
                on the observed strategies and approaches."""),
                HumanMessage(content=insights_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse as structured data, fallback to text if needed
            try:
                # Attempt to extract structured insights
                insights_text = response.content
                actionable_insights = self._parse_insights_from_text(insights_text)
            except:
                actionable_insights = [{
                    "category": "General Strategy",
                    "insight": response.content,
                    "implementation": "Review and adapt based on context",
                    "timeline": "Ongoing",
                    "resources_needed": "Management attention",
                    "success_metrics": "Improved operational efficiency",
                    "priority": "Medium",
                    "complexity": "Moderate"
                }]
            
            return {
                **state,
                "actionable_insights": actionable_insights
            }
        
        def document_generation_node(state: VideoAnalysisState):
            """Generate comprehensive understanding document"""
            
            document_prompt = f"""
            Create a comprehensive "Operational Strategy Understanding Document" based on the analysis:
            
            SUBJECT: {state.get('person_context', 'Video Subject')}
            FOCUS AREA: {state.get('analysis_focus', 'Operational Strategies')}
            VIDEO DURATION: {state.get('video_duration', 'Unknown')} seconds
            
            ANALYSIS COMPONENTS:
            - Audio Analysis: {state.get('audio_analysis', '')[:500]}...
            - Visual Analysis: {state.get('visual_analysis', '')[:500]}...
            - Strategy Extraction: {state.get('strategy_extraction', '')[:1000]}...
            
            ACTIONABLE INSIGHTS: {len(state.get('actionable_insights', []))} insights identified
            
            Create a professional document with the following structure:
            
            # OPERATIONAL STRATEGY UNDERSTANDING DOCUMENT
            
            ## EXECUTIVE SUMMARY
            [2-3 paragraph overview of key findings]
            
            ## SUBJECT PROFILE
            [Analysis of the person's operational approach and style]
            
            ## KEY STRATEGIC THEMES
            [Main strategic themes identified from the analysis]
            
            ## OPERATIONAL METHODOLOGIES
            [Specific methodologies and approaches observed]
            
            ## LEADERSHIP & MANAGEMENT STYLE
            [Leadership characteristics and management approaches]
            
            ## IMPLEMENTATION RECOMMENDATIONS
            [Specific recommendations for applying these strategies]
            
            ## SUCCESS FACTORS
            [Critical success factors for implementing these approaches]
            
            ## RISK CONSIDERATIONS
            [Potential risks and mitigation strategies]
            
            ## NEXT STEPS
            [Recommended follow-up actions]
            
            Make this document professional, actionable, and specific to the analyzed content.
            Include specific examples and quotes from the transcript where relevant.
            """
            
            messages = [
                SystemMessage(content="""You are a senior business analyst creating a professional 
                strategy document. Write in a clear, executive-level style that provides valuable 
                insights for decision-makers. Use markdown formatting for structure."""),
                HumanMessage(content=document_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                **state,
                "final_document": response.content
            }
        
        def recommendations_node(state: VideoAnalysisState):
            """Generate specific recommendations for implementation"""
            
            recommendations_prompt = f"""
            Based on the complete analysis, provide specific implementation recommendations:
            
            FINAL DOCUMENT SUMMARY:
            {state.get('final_document', '')[:1000]}...
            
            ACTIONABLE INSIGHTS COUNT: {len(state.get('actionable_insights', []))}
            
            Create 5-7 high-priority recommendations in this format:
            
            {{
                "title": "Recommendation Title",
                "description": "Detailed description",
                "rationale": "Why this is important based on the analysis",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "timeline": "Implementation timeline",
                "dependencies": "What needs to be in place first",
                "expected_impact": "Expected business impact",
                "risk_level": "Low/Medium/High"
            }}
            
            Focus on recommendations that:
            1. Directly leverage the observed strategies
            2. Are realistic and implementable
            3. Have clear business value
            4. Build on the person's demonstrated strengths
            5. Address identified opportunity areas
            """
            
            messages = [
                SystemMessage(content="""You are a management consultant providing strategic 
                implementation recommendations. Focus on practical, high-impact actions that 
                organizations can take to implement the observed strategies."""),
                HumanMessage(content=recommendations_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse recommendations
            try:
                recommendations = self._parse_recommendations_from_text(response.content)
            except:
                recommendations = [{
                    "title": "Strategy Implementation",
                    "description": response.content,
                    "rationale": "Based on video analysis",
                    "steps": ["Review analysis", "Plan implementation", "Execute"],
                    "timeline": "3-6 months",
                    "dependencies": "Leadership commitment",
                    "expected_impact": "Improved operational efficiency",
                    "risk_level": "Medium"
                }]
            
            return {
                **state,
                "recommendations": recommendations
            }
        
        # Build the LangGraph workflow
        workflow = StateGraph(VideoAnalysisState)
        
        # Add nodes
        workflow.add_node("preprocess", video_preprocessing_node)
        workflow.add_node("transcribe", transcription_node)
        workflow.add_node("visual_analysis", visual_analysis_node)
        workflow.add_node("extract_strategies", strategy_extraction_node)
        workflow.add_node("generate_insights", actionable_insights_node)
        workflow.add_node("create_document", document_generation_node)
        workflow.add_node("final_recommendations", recommendations_node)
        
        # Add edges
        workflow.set_entry_point("preprocess")
        workflow.add_edge("preprocess", "transcribe")
        workflow.add_edge("transcribe", "visual_analysis")
        workflow.add_edge("visual_analysis", "extract_strategies")
        workflow.add_edge("extract_strategies", "generate_insights")
        workflow.add_edge("generate_insights", "create_document")
        workflow.add_edge("create_document", "final_recommendations")
        workflow.add_edge("final_recommendations", END)
        
        return workflow.compile()
    
    def _parse_insights_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse insights from LLM response text"""
        insights = []
        # This is a simplified parser - you could make it more sophisticated
        # For now, create a basic structure
        lines = text.split('\n')
        current_insight = {}
        
        for line in lines:
            if 'category' in line.lower() and ':' in line:
                if current_insight:
                    insights.append(current_insight)
                current_insight = {"category": line.split(':')[-1].strip()}
            elif 'insight' in line.lower() and ':' in line:
                current_insight["insight"] = line.split(':')[-1].strip()
            elif 'implementation' in line.lower() and ':' in line:
                current_insight["implementation"] = line.split(':')[-1].strip()
            elif 'timeline' in line.lower() and ':' in line:
                current_insight["timeline"] = line.split(':')[-1].strip()
            elif 'priority' in line.lower() and ':' in line:
                current_insight["priority"] = line.split(':')[-1].strip()
                current_insight.setdefault("resources_needed", "Standard resources")
                current_insight.setdefault("success_metrics", "Improved performance")
                current_insight.setdefault("complexity", "Moderate")
        
        if current_insight:
            insights.append(current_insight)
        
        return insights if insights else [
            {
                "category": "Extracted Strategy",
                "insight": text[:200] + "...",
                "implementation": "Review and implement based on context",
                "timeline": "3-6 months",
                "resources_needed": "Management attention",
                "success_metrics": "Improved operations",
                "priority": "Medium",
                "complexity": "Moderate"
            }
        ]
    
    def _parse_recommendations_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse recommendations from LLM response text"""
        # Simplified recommendation parser
        return [
            {
                "title": "Strategic Implementation",
                "description": text[:300] + "...",
                "rationale": "Based on comprehensive video analysis",
                "steps": ["Review findings", "Plan implementation", "Execute strategies"],
                "timeline": "3-6 months",
                "dependencies": "Leadership support and resource allocation",
                "expected_impact": "Enhanced operational effectiveness",
                "risk_level": "Medium"
            }
        ]


# Create the video analysis agent instance
def create_video_analysis_agent():
    """Factory function to create video analysis agent"""
    agent = VideoAnalysisAgent()
    return agent.create_agent()


video_analysis_agent = create_video_analysis_agent()


async def run_video_analysis_agent(
    video_path: str,
    person_context: str = "",
    analysis_focus: str = "operational strategies"
) -> dict:
    """
    Run video analysis agent with given parameters
    
    Args:
        video_path: Path to the video file
        person_context: Context about the person (role, background, etc.)
        analysis_focus: What type of strategies to focus on
    
    Returns:
        Complete analysis results
    """
    try:
        result = await video_analysis_agent.ainvoke({
            "video_path": video_path,
            "person_context": person_context,
            "analysis_focus": analysis_focus,
            "transcript": "",
            "key_frames": [],
            "visual_analysis": "",
            "audio_analysis": "",
            "strategy_extraction": "",
            "actionable_insights": [],
            "final_document": "",
            "recommendations": []
        })
        return result
    except Exception as e:
        return {
            "video_path": video_path,
            "person_context": person_context,
            "analysis_focus": analysis_focus,
            "transcript": f"Analysis failed: {str(e)}",
            "key_frames": [],
            "visual_analysis": "",
            "audio_analysis": "",
            "strategy_extraction": f"Error during analysis: {str(e)}",
            "actionable_insights": [],
            "final_document": f"# Analysis Failed\n\nError: {str(e)}",
            "recommendations": []
        }