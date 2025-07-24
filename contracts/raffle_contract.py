# v0.1.0
# { "Depends": "py-genlayer:latest" }

from genlayer import *
from dataclasses import dataclass
import json

@allow_storage
@dataclass
class RaffleAnswer:
    answer: str
    address: Address
    score: str

# contract class
class RaffleContract(gl.Contract):
    resolution_end_date: str
    evaluation_criteria: str
    story_topic: str
    answers: TreeMap[Address, RaffleAnswer]
    winner: Address

    # constructor
    def __init__(self, evaluation_criteria: str, story_topic: str, resolution_end_date: str):
        self.evaluation_criteria = evaluation_criteria
        self.story_topic = story_topic
        self.resolution_end_date = resolution_end_date

    # read methods must be annotated with view
    @gl.public.view
    def get_state(self) -> dict:
        return {
            "evaluation_criteria": self.evaluation_criteria,
            "story_topic": self.story_topic,
            "resolution_end_date": self.resolution_end_date,
            "answers": {k.as_hex: v for k, v in self.answers.items()},
            "winner": self.winner.as_hex,
        }
        
    @gl.public.write
    def add_entry(
        self, answer: str
    ) -> None:
        address = gl.message.sender_address

        def llm_evaluate_answer() -> str:
            
            task = f"""
SYSTEM:
You are the Raffle Judge. For every entry you will receive:
- “criteria”: the dimension to evaluate by (e.g., “funniest”, “most creative”, “most interesting”).
- “call”: the participant’s response text.

Your task:
1. Read the call.
2. Evaluate it **only** against the criteria.
3. Assign a score 1–10 (inclusive), where:
   - 1 means “does not meet the criteria at all”
   - 5 means “adequately meets the criteria”
   - 10 means “exceeds expectations in this criteria”

Rules:
- Respond **with an integer only**, matching the regex: `^(?:[1-9]|10)$`
- Do **not** output any additional text, punctuation, or formatting.
- If the call is empty, or the criteria is missing/invalid, respond with `1`.

USER:
criteria = {self.evaluation_criteria}
call = {answer}

Respond in JSON:
{{
    "score": str, // e.g., "1:2" or "-" if unresolved
}}
It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parsable by a JSON parser without errors.
        """
            result = gl.exec_prompt(task).replace("```json", "").replace("```", "")
            return json.dumps(json.loads(result), sort_keys=True)

        result_json = json.loads(gl.eq_principle.strict_eq(llm_evaluate_answer))   
        print(result_json)
       
        self.answers[address] = RaffleAnswer(answer=answer, address=address, score="0")