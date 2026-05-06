from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
import base64
from typing import Optional
import csv
from datetime import datetime
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JIRA AI Testcase Generator")

class RequirementRequest(BaseModel):
    requirement: str

class JiraGenerateRequest(BaseModel):
    base_url: str
    email: str
    token: str
    issue: str

class TimeEstimateRequest(BaseModel):
    requirement: str

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JIRA AI Testcase Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
            .loading { display: none; color: #007bff; text-align: center; margin: 20px 0; }
            .loading-spinner { 
                border: 4px solid #f3f3f3; 
                border-top: 4px solid #007bff; 
                border-radius: 50%; 
                width: 40px; 
                height: 40px; 
                animation: spin 1s linear infinite; 
                margin: 0 auto 10px;
            }
            .loading-text { font-size: 14px; color: #666; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .error { color: #dc3545; }
            .success { color: #28a745; }
        </style>
    </head>
    <body>
        <h1>JIRA AI Testcase Generator</h1>
        <p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;">
            Created by Rohit with assistance from Cascade AI 🤖
        </p>
        <form id="testcaseForm">
            <div class="form-group">
                <label for="baseUrl">JIRA Base URL:</label>
                <input type="text" id="baseUrl" value="https://leadschool.atlassian.net" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" value="enter your email id" required>
            </div>
            <div class="form-group">
                <label for="token">API Token:</label>
                <input type="password" id="token" placeholder="Your JIRA API token" required>
            </div>
            <div class="form-group">
                <label for="issue">Issue ID:</label>
                <input type="text" id="issue" placeholder="e.g., TEA-7360" required>
            </div>
            <button type="submit">Generate Test Cases</button>
            <button type="button" id="estimateBtn" style="margin-left: 10px; background-color: #28a745;" onclick="getTimeEstimate()">Get Time Estimate</button>
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <div class="loading-text" id="loadingText">🤖 AI is analyzing your JIRA ticket...</div>
            </div>
        </form>
        
        <div id="result" class="result" style="display: none;">
            <h3>Results</h3>
            <div id="resultContent"></div>
            <div id="timeEstimate" style="display: none; margin-top: 15px; padding: 10px; background-color: #e8f5e8; border-radius: 4px;">
                <strong>⏱️ Estimated Development Time:</strong> <span id="timeValue"></span>
            </div>
            <button id="downloadBtn" style="display: none;" onclick="downloadCSV()">Download CSV</button>
            <button id="sheetsBtn" style="display: none; margin-left: 10px;" onclick="exportToSheets()">Export to Google Sheets</button>
        </div>

        <script>
            let generatedData = null;
            
            document.getElementById('testcaseForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const baseUrl = document.getElementById('baseUrl').value;
                const email = document.getElementById('email').value;
                const token = document.getElementById('token').value;
                const issue = document.getElementById('issue').value;
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                // Simulate AI thinking process
                const loadingSteps = [
                    '🤖 AI is analyzing your JIRA ticket...',
                    '🔍 Extracting requirements and identifying risks...',
                    '🧠 Processing with Llama3 AI model...',
                    '📝 Generating comprehensive test scenarios...',
                    '✨ Formatting test cases in BDD structure...'
                ];
                
                let stepIndex = 0;
                const loadingInterval = setInterval(() => {
                    if (stepIndex < loadingSteps.length) {
                        document.getElementById('loadingText').textContent = loadingSteps[stepIndex];
                        stepIndex++;
                    } else {
                        clearInterval(loadingInterval);
                    }
                }, 3000);
                
                try {
                    const response = await fetch(`/generate?base_url=${encodeURIComponent(baseUrl)}&email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}&issue=${encodeURIComponent(issue)}`);
                    const data = await response.json();
                    
                    clearInterval(loadingInterval);
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        generatedData = data;
                        document.getElementById('resultContent').innerHTML = `
                            <div class="success">
                                <strong>Issue:</strong> ${data.issue}<br>
                                <strong>Summary:</strong> ${data.summary}<br>
                                <br>
                                <strong>Generated Test Cases:</strong><br>
                                <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 4px;">${data.test_cases}</pre>
                            </div>
                        `;
                        document.getElementById('downloadBtn').style.display = 'inline-block';
                        document.getElementById('sheetsBtn').style.display = 'inline-block';
                    } else {
                        document.getElementById('resultContent').innerHTML = `<div class="error"><strong>Error:</strong> ${data.detail || data.error}</div>`;
                    }
                } catch (error) {
                    clearInterval(loadingInterval);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('resultContent').innerHTML = `<div class="error"><strong>Error:</strong> ${error.message}</div>`;
                }
                
                document.getElementById('result').style.display = 'block';
            });
            
            function downloadCSV() {
                if (generatedData) {
                    window.open(`/download?issue=${encodeURIComponent(generatedData.issue)}&test_cases=${encodeURIComponent(generatedData.test_cases)}`, '_blank');
                }
            }
            
            function exportToSheets() {
                if (generatedData) {
                    window.open(`/export-to-google-sheets?issue=${encodeURIComponent(generatedData.issue)}&test_cases=${encodeURIComponent(generatedData.test_cases)}`, '_blank');
                }
            }
            
            async function getTimeEstimate() {
                const baseUrl = document.getElementById('baseUrl').value;
                const email = document.getElementById('email').value;
                const token = document.getElementById('token').value;
                const issue = document.getElementById('issue').value;
                
                if (!issue) {
                    alert('Please enter an Issue ID first');
                    return;
                }
                
                // Show loading for estimate
                document.getElementById('loading').style.display = 'block';
                document.getElementById('loadingText').textContent = '🧠 AI is calculating time estimate...';
                
                try {
                    const response = await fetch(`/time-estimate?base_url=${encodeURIComponent(baseUrl)}&email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}&issue=${encodeURIComponent(issue)}`);
                    const data = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        document.getElementById('timeValue').textContent = data.estimate;
                        document.getElementById('timeEstimate').style.display = 'block';
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert('Error getting time estimate: ' + (data.detail || data.error));
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "JIRA AI Testcase Generator"}

@app.get("/generate")
def generate_from_jira(base_url: str, email: str, token: str, issue: str):
    """
    Generate test cases from JIRA issue using query parameters
    """
    try:
        # Create JIRA API URL
        jira_api_url = f"{base_url.rstrip('/')}/rest/api/2/issue/{issue}"
        
        # Setup authentication
        auth_string = f"{email}:{token}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        # Fetch JIRA issue
        response = requests.get(jira_api_url, headers=headers)
        response.raise_for_status()
        
        issue_data = response.json()
        
        # Extract requirement from JIRA fields
        summary = issue_data.get('fields', {}).get('summary', '')
        description = issue_data.get('fields', {}).get('description', '')
        issue_type = issue_data.get('fields', {}).get('issuetype', {}).get('name', '')
        
        # Create requirement text
        requirement = f"""
        Issue: {issue}
        Type: {issue_type}
        Summary: {summary}
        Description: {description}
        """
        
        # Generate test cases
        test_cases = generate_testcases(requirement)
        
        return {
            "success": True,
            "issue": issue,
            "summary": summary,
            "test_cases": test_cases
        }
        
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch JIRA issue: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")

@app.get("/time-estimate")
def get_time_estimate(base_url: str, email: str, token: str, issue: str):
    """
    Get time estimate for JIRA issue using AI
    """
    try:
        # Create JIRA API URL
        jira_api_url = f"{base_url.rstrip('/')}/rest/api/2/issue/{issue}"
        
        # Setup authentication
        auth_string = f"{email}:{token}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        # Fetch JIRA issue
        response = requests.get(jira_api_url, headers=headers)
        response.raise_for_status()
        
        issue_data = response.json()
        
        # Extract requirement from JIRA fields
        summary = issue_data.get('fields', {}).get('summary', '')
        description = issue_data.get('fields', {}).get('description', '')
        issue_type = issue_data.get('fields', {}).get('issuetype', {}).get('name', '')
        priority = issue_data.get('fields', {}).get('priority', {}).get('name', '')
        
        # Create requirement text for time estimation
        requirement = f"""
        Issue: {issue}
        Type: {issue_type}
        Priority: {priority}
        Summary: {summary}
        Description: {description}
        """
        
        # Get time estimate from AI
        time_estimate = estimate_development_time(requirement)
        
        return {
            "success": True,
            "issue": issue,
            "summary": summary,
            "estimate": time_estimate
        }
        
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch JIRA issue: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating time: {str(e)}")

@app.post("/estimate-time")
def estimate_time_endpoint(request: TimeEstimateRequest):
    try:
        result = estimate_development_time(request.requirement)
        return {"success": True, "estimate": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def estimate_development_time(requirement):
    ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')
    timeout = int(os.getenv('OLLAMA_TIMEOUT', '600'))
    
    # Truncate requirement if too long
    if len(requirement) > 2000:
        requirement = requirement[:2000] + "..."
    
    prompt = f"""As an experienced project manager and developer, estimate the development time for this requirement:

Requirement: {requirement}

Consider:
- Feature complexity
- Number of test cases needed (typically 15-20 test cases)
- Time to write each test case (Given/When/Then format)
- Test case review and refinement
- Documentation time
- Integration requirements

Provide estimates in this format:
"Development Time: X hours/days/weeks/months"
"Test Case Generation Time: X minutes/hours"
"Total Time: X hours/days/weeks/months"

Be conservative but realistic. Consider a standard 8-hour workday."""

    try:
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "max_tokens": 200,
                    "num_predict": 200
                }
            },
            timeout=timeout
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        if not response_data or "response" not in response_data:
            raise Exception("Empty or invalid response from Ollama")
        
        # Extract clean time estimate
        estimate = response_data["response"].strip()
        
        # Parse the response to extract both development and test case times
        dev_time = ""
        test_time = ""
        total_time = ""
        
        lines = estimate.split('\n')
        for line in lines:
            line = line.strip()
            if "Development Time:" in line:
                dev_time = line.split("Development Time:")[1].strip()
            elif "Test Case Generation Time:" in line:
                test_time = line.split("Test Case Generation Time:")[1].strip()
            elif "Total Time:" in line:
                total_time = line.split("Total Time:")[1].strip()
        
        # Return formatted estimate
        if dev_time and test_time and total_time:
            return f"Development: {dev_time}\nTest Cases: {test_time}\nTotal: {total_time}"
        elif total_time:
            return total_time
        else:
            return estimate
        
    except requests.exceptions.Timeout:
        raise Exception("Time estimation request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to Ollama. Please ensure Ollama is running.")
    except Exception as e:
        raise Exception(f"Error estimating time: {str(e)}")

@app.get("/export-to-google-sheets")
def export_to_google_sheets(issue: str, test_cases: str):
    """
    Generate a downloadable CSV file optimized for Google Sheets import
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as tmp_file:
            filename = tmp_file.name
            
            # Add Google Sheets optimized header and formatting
            tmp_file.write(f"# Test Cases for {issue}\n")
            tmp_file.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            tmp_file.write("# Import this file into Google Sheets: File > Import > Upload\n\n")
            tmp_file.write(test_cases)
        
        # Generate a proper filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheets_filename = f"testcases_{issue}_for_google_sheets_{timestamp}.csv"
        
        # Return the file for download
        return FileResponse(
            filename,
            media_type='text/csv',
            filename=sheets_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Google Sheets export: {str(e)}")

@app.get("/download")
def download_csv(issue: str, test_cases: str):
    """
    Download test cases as CSV file
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as tmp_file:
            filename = tmp_file.name
            
            # Write the test cases to CSV file
            tmp_file.write(test_cases)
        
        # Generate a proper filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"testcases_{issue}_{timestamp}.csv"
        
        # Return the file for download
        return FileResponse(
            filename,
            media_type='text/csv',
            filename=csv_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating CSV file: {str(e)}")

@app.post("/generate-testcases")
def generate_testcases_endpoint(request: RequirementRequest):
    try:
        result = generate_testcases(request.requirement)
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_testcases(requirement):
    ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')
    timeout = int(os.getenv('OLLAMA_TIMEOUT', '600'))
    max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '3000'))
    max_length = int(os.getenv('REQUIREMENT_MAX_LENGTH', '3000'))
    
    # Truncate requirement if too long to avoid timeout
    if len(requirement) > max_length:
        requirement = requirement[:max_length] + "..."
        logger.warning(f"Requirement truncated from {len(requirement)} to {max_length} characters")
    
    # Adaptive prompt based on requirement size
    if len(requirement) > 1500:
        prompt_suffix = "This is a complex requirement. Generate an appropriate number of test cases to ensure comprehensive coverage."
    else:
        prompt_suffix = "Generate an appropriate number of test cases based on the complexity and scope of this requirement."
    
    prompt = f"""You are a Senior QA Engineer with 15 years of experience in functional, security, API, and edge-case testing.

Your task is to generate comprehensive and professional test cases from the Jira story provided.

Follow these rules strictly:

1. Understand the functional requirement carefully.
2. Generate test cases covering:

   * Positive scenarios
   * Negative scenarios
   * Edge cases
   * Boundary value conditions
   * Validation checks
   * Security scenarios
   * Performance considerations
3. Think like a malicious user trying to break the system.
4. Consider UI, API, backend validation, and database integrity.
5. Include missing requirement assumptions if needed.

Requirement: {requirement}

Output format must be a table with the following columns:

Test Case ID,Test Scenario,Preconditions,Test Steps,Test Data,Expected Result,Priority,Test Type

Generate at least 30–50 meaningful test cases.

For each test case:
- Test Case ID: TC001, TC002, etc.
- Test Scenario: Brief description of what's being tested
- Preconditions: Setup or initial state
- Test Steps: Step-by-step actions
- Test Data: Sample data for testing
- Expected Result: Expected outcome
- Priority: High/Medium/Low
- Test Type: Functional/Negative/Security/Edge/Boundary

Ensure comprehensive test coverage for the requirement."""

    try:
        logger.info(f"Generating test cases with {max_tokens} max tokens, timeout {timeout}s")
        
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "max_tokens": max_tokens,
                    "num_predict": max_tokens,
                    "repeat_penalty": 1.1
                }
            },
            timeout=timeout
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        if not response_data or "response" not in response_data:
            raise Exception("Empty or invalid response from Ollama")
        
        # Extract only CSV content, remove any explanatory text
        csv_content = response_data["response"]
        
        # Find CSV header and extract from there
        csv_start = csv_content.find("Test Case ID,Test Scenario,Preconditions,Test Steps,Test Data,Expected Result,Priority,Test Type")
        if csv_start != -1:
            csv_content = csv_content[csv_start:]
        
        # Clean up the response to get just the CSV data
        lines = csv_content.split('\n')
        csv_lines = []
        for line in lines:
            line = line.strip()
            # Keep the header row and any valid CSV data lines
            if line and ',' in line and not line.startswith(('Here are', 'Note:', 'Please', 'The following', 'You are', 'Requirement:', 'Output format')):
                csv_lines.append(line)
        
        logger.info(f"Successfully generated {len(csv_lines)} lines of CSV data")
        return '\n'.join(csv_lines)
        
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {timeout} seconds")
        raise Exception(f"Request timed out after {timeout} seconds. The requirement might be too complex. Try with a smaller scope or check if the model is busy.")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise Exception("Failed to connect to Ollama. Please ensure Ollama is running on your host machine and accessible.")
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise Exception(f"Error generating test cases: {str(e)}")