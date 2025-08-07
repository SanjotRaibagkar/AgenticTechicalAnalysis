# src/langgraph_mcp_groq/server/tools/video_tools.py
import os
import json
from typing import Dict, Any
from ...agents.video_analysis_agent import run_video_analysis_agent


async def video_strategy_analyzer(
    video_file_path: str,
    person_context: str = "",
    analysis_focus: str = "operational strategies"
) -> str:
    """
    Analyze videos of people to extract operational strategies and create actionable understanding documents.
    
    This advanced agent processes video content to identify:
    - Communication patterns and leadership style
    - Decision-making frameworks
    - Operational methodologies  
    - Strategic thinking approaches
    - Process optimization strategies
    - Implementation tactics
    
    Args:
        video_file_path: Full path to the video file (mp4, avi, mov, etc.)
        person_context: Context about the person (e.g., "CEO of tech startup", "Operations Manager with 10 years experience")
        analysis_focus: Specific focus area (e.g., "leadership strategies", "sales methodologies", "operational efficiency")
        
    Returns:
        JSON string with comprehensive analysis
    """
    try:
        # Validate video file exists
        if not os.path.exists(video_file_path):
            return json.dumps({
                "status": "error",
                "error": f"Video file not found: {video_file_path}",
                "suggestion": "Please provide a valid path to an existing video file"
            }, indent=2)
        
        # Validate file extension
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        file_ext = os.path.splitext(video_file_path)[1].lower()
        if file_ext not in valid_extensions:
            return json.dumps({
                "status": "error", 
                "error": f"Unsupported video format: {file_ext}",
                "supported_formats": valid_extensions
            }, indent=2)
        
        # Run the video analysis agent
        result = await run_video_analysis_agent(
            video_path=video_file_path,
            person_context=person_context,
            analysis_focus=analysis_focus
        )
        
        return json.dumps({
            "status": "success",
            "video_file": os.path.basename(video_file_path),
            "person_context": result.get("person_context", ""),
            "analysis_focus": result.get("analysis_focus", ""),
            "transcript": result.get("transcript", ""),
            "audio_analysis": result.get("audio_analysis", ""),
            "visual_analysis": result.get("visual_analysis", ""),
            "strategy_extraction": result.get("strategy_extraction", ""),
            "actionable_insights": result.get("actionable_insights", []),
            "strategy_document": result.get("final_document", ""),
            "implementation_recommendations": result.get("recommendations", []),
            "video_duration": result.get("video_duration", 0)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "video_file": video_file_path,
            "troubleshooting": [
                "Ensure video file exists and is accessible",
                "Check video format is supported",
                "Verify sufficient disk space for processing",
                "Ensure required dependencies are installed"
            ]
        }, indent=2)


async def batch_video_analysis(
    video_directory: str,
    person_contexts: str = "",
    analysis_focus: str = "operational strategies"
) -> str:
    """
    Analyze multiple videos in a directory for operational strategies.
    
    Args:
        video_directory: Path to directory containing video files
        person_contexts: JSON string mapping filename to person context
        analysis_focus: Focus area for all analyses
        
    Returns:
        JSON string with batch analysis results
    """
    try:
        if not os.path.exists(video_directory):
            return json.dumps({
                "status": "error",
                "error": f"Directory not found: {video_directory}"
            })
        
        # Parse person contexts if provided
        contexts_map = {}
        if person_contexts:
            try:
                contexts_map = json.loads(person_contexts)
            except:
                contexts_map = {}
        
        # Find video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        video_files = []
        
        for file in os.listdir(video_directory):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(video_directory, file))
        
        if not video_files:
            return json.dumps({
                "status": "error",
                "error": "No video files found in directory",
                "directory": video_directory
            })
        
        # Process each video (limit to 5 to prevent overload)
        batch_results = []
        for video_path in video_files[:5]:
            filename = os.path.basename(video_path)
            person_context = contexts_map.get(filename, "Unknown person")
            
            result = await run_video_analysis_agent(
                video_path=video_path,
                person_context=person_context,
                analysis_focus=analysis_focus
            )
            
            batch_results.append({
                "filename": filename,
                "status": "success" if result.get("final_document") else "error",
                "summary": result.get("final_document", "")[:500] + "...",
                "insights_count": len(result.get("actionable_insights", [])),
                "recommendations_count": len(result.get("recommendations", []))
            })
        
        return json.dumps({
            "status": "success",
            "processed_count": len(batch_results),
            "results": batch_results,
            "analysis_focus": analysis_focus
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# Video tools metadata for registration
VIDEO_TOOLS = {
    "video_strategy_analyzer": {
        "function": video_strategy_analyzer,
        "description": "Analyze videos of people to extract operational strategies",
        "category": "Video Analysis"
    },
    "batch_video_analysis": {
        "function": batch_video_analysis,
        "description": "Batch analyze multiple videos for strategies",
        "category": "Video Analysis"
    }
}
