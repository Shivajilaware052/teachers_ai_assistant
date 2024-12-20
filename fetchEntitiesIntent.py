import requests
import json




def process_action(request: dict):
    action = request.get("action")

    if action == "add_student":
        student_name = request.get("student_name")
        if student_name:
            response = requests.post("http://localhost:8000/add-student/", json={"name": student_name})
            return response.json()
        
    elif action == "get_student":
        student_name = request.get("student_name")
        
        if student_name:
            # Call the get_student API to fetch student data
            student_response = requests.get(f"http://localhost:8000/get-student/{student_name}")
            
            if student_response.status_code == 200:
                # Return the student data received from the API
                return student_response.json()
            else:
                # If student not found or any error occurs
                return {"message": f"Student '{student_name}' not found"}
        else:
            return {"message": "Student name is required"} 

    elif action == "add_score":
        student_name = request.get("student_name")
        subject = request.get("subject")
        score = request.get("score")

        # Check if all required fields are present
        if student_name and subject and score is not None:
            # Fetch student information by name
            student_response = requests.get(f"http://localhost:8000/get-student/{student_name}")
            
            if student_response.status_code == 200:
                student_id = student_response.json().get("id")
                
                # Fetch all subjects
                subject_response = requests.get("http://localhost:8000/get-all-subjects/")
                
                if subject_response.status_code == 200:
                    # Extract subjects list from the response
                    print("subject_response: ",subject_response)
                    subjects = subject_response.json().get("subjects", [])
                    print("subjects: ",subjects)
                    # Find the subject ID based on the subject name
                    subject_id = next((sub['id'] for sub in subjects if sub['name'] == subject), None)
                    
                    if subject_id is not None:
                        # Add the score
                        score_response = requests.post(
                            "http://localhost:8000/add-score/",
                            json={"student_id": student_id, "subject_id": subject_id, "score": score}
                        )
                        return score_response.json()
                    else:
                        return {"message": f"Subject '{subject}' not found"}
                else:
                    return {"message": "Error fetching subjects from the database"}
            else:
                return {"message": f"Student '{student_name}' not found"}
        else:
            return {"message": "Missing required fields: student_name, subject, or score"}
        
    elif action == "add_subject":
        subject_name = request.get("subject")
        if subject_name:
            # Make a POST request to add the new subject
            response = requests.post(
                "http://localhost:8000/add-subject/",
                json={"name": subject_name}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"message": "Failed to add the subject. Please try again."}
        else:
            return {"message": "Subject name is required to add a new subject."}
        
    elif action == "get_subjects":
        student_name = request.get("student_name")
        if student_name:
            response = requests.get(f"http://localhost:8000/get-subjects/?student_name={student_name}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"message": f"Subjects not found for student {student_name}."}
        else:
            return {"message": "Student name is required to fetch subjects."}

    elif action == "summarize_scores":
        subject_name = request.get("subject")
        if subject_name:
            response = requests.get(f"http://localhost:8000/summarize-scores/?subject_name={subject_name}")
            return response.json()
        else:
            return {"message": "subject_name must be provided"}

    elif action == "get_all_students":
        response = requests.get("http://localhost:8000/get-all-students/")
        return response.json()

    elif action == "unknown":
        return {"message": "Unknown action received"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    
    
    
def getIntent(userInput: str) -> dict:
    # URL of the external API you want to send the request to
    external_api_url = "https://prod-01.centralindia.logic.azure.com:443/workflows/a16ab099595b4157be536ef02253373c/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=-au0vLfs2nzLoaw8J3_Ok_zwLQW_cFBPC199UTzhiRM"

    # Prepare the payload to send to the external API
    payload = {
        "userInput": userInput
    }

    try:
        response = requests.post(external_api_url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            resp=response.json()["modelResp"]
            print(resp)
            # json_str = re.search(r'```\n(.*?)\n```', resp, re.DOTALL)
            try:
                    # Get the JSON part and load it into a Python dictionary
                json_data = json.loads(resp)
                # print("json_data: ",json_data)
                # return json_data
                if json_data["action"]=="unknown":
                    return  json_data["other_resp"]
                else:
                    return process_action(json_data)
            except json.JSONDecodeError as e:
                return ("Error decoding JSON:", e)
        else:
            return {"error": "Request failed", "status_code": response.status_code, "message": response.text}
    except Exception as e:
        return {"error": "An error occurred", "message": str(e)}
    
print(getIntent("give me all subjects"))