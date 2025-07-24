# v0.1.0
# { "Depends": "py-genlayer:latest" }

from genlayer import *
from dataclasses import dataclass
import json
import uuid

@allow_storage
@dataclass
class RaffleAnswer:
    answer: str
    address: str
    score: str

# contract class
class RaffleContract(gl.Contract):
    raffle_status: str
    resolution_end_date: str
    evaluation_criteria: str
    story_topic: str
    answers: TreeMap[str,RaffleAnswer]
    winner: str

    # constructor
    def __init__(self, evaluation_criteria: str, story_topic: str, resolution_end_date: str):
        self.evaluation_criteria = evaluation_criteria
        self.story_topic = story_topic
        self.resolution_end_date = resolution_end_date
        self.raffle_status = "OPEN"

    # read methods must be annotated with view
    @gl.public.view
    def get_state(self) -> dict:
        return {
            "evaluation_criteria": self.evaluation_criteria,
            "story_topic": self.story_topic,
            "resolution_end_date": self.resolution_end_date,
            "answers": {k: v for k, v in self.answers.items()},
            "winner": self.winner,
            "raffle_status": self.raffle_status
        }
        

    @gl.public.write
    def resolve_contract(
        self
    ) -> None:
        evaluation_criteria = self.evaluation_criteria
        if self.raffle_status == "CLOSED":
            raise Exception("Raffle is already closed")

        
        #need to parse all answers and for each:
        ## order by score
        sorted_answers = sorted(self.answers.values(), key=lambda x: float(x.score), reverse=True)

        # Get the first 4 answers
        top_4_answers = sorted_answers[:4]
        answers_json = [{"answer": answer.answer, "address": answer.address} for answer in top_4_answers]
        str_answers = json.dumps(answers_json)

        def llm_get_winner() -> str:
            task = f"""
SYSTEM:
You are the Raffle Judge. You will receive the following inputs:
  • “criteria”: the dimension to score by (e.g. “funniest”, “most interesting”, “most curious”).  
  • “story_topic”: the prompt or call participants responded to (e.g. “Tell me your funniest pizza‑eating story.”).  
  • “answers”: a list of participant submissions, each containing an “answer” and an “address”.

Respond in JSON:
{{
    "best_address": str
}}
It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parsable by a JSON parser without errors.

Your task:
1. Relevance check:
   - For each “answer”, if it does **not** address the “story_topic” (it’s off‑topic, empty, or nonsensical), immediately assign a score of **1**.
2. Scoring:
   - Otherwise, evaluate each “answer” **only** on the given “criteria”:
     • **1** = fails completely  
     • **5** = adequately meets expectations  
     • **10** = outstanding, exceeds all expectations  
3. Selection:
   - Determine the “answer” with the highest score. In case of a tie, select the first one in the list.
4. Output:
   - Return the “address” of the best “answer”.

USER:
criteria = {evaluation_criteria}  
answers = {str_answers}

JUDGE:


        """
            result = gl.nondet.exec_prompt(task).replace("```json", "").replace("```", "")
            return json.dumps(json.loads(result), sort_keys=True)

           

        result_json = json.loads(gl.eq_principle.strict_eq(llm_get_winner))   
        self.winner = result_json["best_address"]
        self.raffle_status = "CLOSED"
        print("winner:", self.winner)

       
        


    @gl.public.write
    def add_entry(
        self, answer: str
    ) -> None:
        address = gl.message.sender_address.as_hex
        evaluation_criteria = self.evaluation_criteria
        story_topic = self.story_topic

        def llm_evaluate_answer() -> str:
            
            task = f"""
You are an evaluator. Your task is to rate an answer based on a given topic and a criterion.

Rules:
1. If the answer is not related to the given topic at all, return 0.
2. Otherwise, score from 0 to 100 based on how well the answer matches the criterion:
   - 0 = does not meet the criterion at all (or unrelated).
   - 100 = perfectly matches the criterion.
   - Use intermediate values for partial matches.
3. Output only a single number (integer or one decimal). Do not add any explanation or text.

Input:
- Topic: {story_topic}
- Criterion: {evaluation_criteria}
- Answer: {answer}

Output:
A single number between 0 and 100 (for example: `85`).

Respond in JSON:
{{
    "score": str
}}



        """
            result = gl.nondet.exec_prompt(task).replace("```json", "").replace("```", "")
            return json.dumps(json.loads(result), sort_keys=True)

        result_json = json.loads(gl.eq_principle.strict_eq(llm_evaluate_answer))   
        print(result_json)
       
       
        self.answers[address] = RaffleAnswer(answer=answer, address=address, score=str(result_json["score"]))