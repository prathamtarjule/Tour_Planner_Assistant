from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from database.neo4j_client import Neo4jClient
from typing import Dict, List, Optional

class UserInteractionAgent:
    def __init__(self):
        self.db = Neo4jClient()
        
        # Load the model and tokenizer
        model_path = "models/EleutherAI/gpt-neo-125M"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        
    def process_initial_input(self, user_id: str, message: str) -> Dict:
        """Process initial user input interactively to gather all necessary details."""
        
        # Initialize prompts for each required piece of information
        questions = {
            "city": "In which city would you like to plan your visit?",
            "date": "What date are you planning to visit?",
            "start_time": "What time do you plan to start your itinerary?",
            "end_time": "What time do you plan to finish your itinerary?",
            "interests": "What are your main interests for this trip?",
            "budget": "What is your budget for this trip?",
            "starting_point": "Where will you be starting from?"
        }
        
        # Initialize the extracted information dictionary
        extracted_info = {}

        try:
            # Loop through each question and gather the response interactively
            for key, question in questions.items():
                # Ask the question through the model 
                print(f"Assistant: {question}")
                
                # You will now manually provide the answer as input
                user_answer = input(f"Your answer for {key}: ") 

                # Store the answer in the extracted_info dictionary
                extracted_info[key] = user_answer
                print(f"Extracted {key}: {user_answer}")

            # Store the gathered preferences in the database
            self._store_preferences(user_id, extracted_info)
            
            return extracted_info
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return {"error": str(e)}
        
    def suggest_attractions(self, city: str, interests: List[str]) -> List[Dict]:
        """Suggest attractions based on city and interests."""
        system_prompt = f"""
        Suggest popular attractions in {city} that match the following interests: {', '.join(interests)}.
        For each attraction, provide:
        - Name
        - Category
        - Typical duration
        - Approximate cost
        - Brief description
        """
        
        response = self.pipeline(system_prompt, max_length=200)
        return self._parse_attractions(response[0]['generated_text'])

    def _store_preferences(self, user_id: str, info: Dict):
        """Store user preferences in Neo4j."""
        if 'interests' in info:
            for interest in info['interests']:
                self.db.create_user_preference(user_id, 'Interest', 'LIKES', interest)
        
        if 'budget' in info:
            self.db.create_user_preference(user_id, 'Budget', 'HAS', str(info['budget']))

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured format."""
        try:
            # Additional parsing logic could be added if needed
            return eval(response)
        except Exception as e:
            return {"error": str(e)}

    def _parse_attractions(self, response: str) -> List[Dict]:
        """Parse attractions response into structured format."""
        try:
            # Additional parsing logic could be added if needed
            return eval(response)
        except Exception as e:
            return [{"error": str(e)}]
